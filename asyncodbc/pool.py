import asyncio
import collections
from typing import Deque, Set

from .connection import Connection, connect
from .utils import _PoolAcquireContextManager, _PoolContextManager

__all__ = ["create_pool", "Pool"]


def create_pool(minsize=1, maxsize=10, echo=False, pool_recycle=-1, **kwargs):
    return _PoolContextManager(
        _create_pool(
            minsize=minsize,
            maxsize=maxsize,
            echo=echo,
            pool_recycle=pool_recycle,
            **kwargs
        )
    )


async def _create_pool(minsize=1, maxsize=10, echo=False, pool_recycle=-1, **kwargs):
    pool = Pool(
        minsize=minsize, maxsize=maxsize, echo=echo, pool_recycle=pool_recycle, **kwargs
    )
    if minsize > 0:
        async with pool.cond:
            await pool.fill_free_pool(False)
    return pool


class Pool(asyncio.AbstractServer):
    """Connection pool, just from aiomysql"""

    def __init__(
        self,
        minsize: int,
        maxsize: int,
        pool_recycle: int,
        echo: bool = False,
        **kwargs
    ):
        if minsize < 0:
            raise ValueError("minsize should be zero or greater")
        if maxsize < minsize:
            raise ValueError("maxsize should be not less than minsize")
        self._minsize = minsize
        self._loop = asyncio.get_event_loop()
        self._conn_kwargs = kwargs
        self._acquiring = 0
        self._free: Deque[Connection] = collections.deque(maxlen=maxsize)
        self._cond = asyncio.Condition()
        self._used: Set[Connection] = set()
        self._terminated: Set[Connection] = set()
        self._closing = False
        self._closed = False
        self._echo = echo
        self._recycle = pool_recycle

    @property
    def echo(self):
        return self._echo

    @property
    def cond(self):
        return self._cond

    @property
    def minsize(self):
        return self._minsize

    @property
    def maxsize(self):
        return self._free.maxlen

    @property
    def size(self):
        return self.freesize + len(self._used) + self._acquiring

    @property
    def freesize(self):
        return len(self._free)

    @property
    def closed(self):
        return self._closed

    async def clear(self):
        """Close all free connections in pool."""
        async with self._cond:
            while self._free:
                conn = self._free.popleft()
                await conn.close()
            self._cond.notify()

    def close(self):
        """Close pool.

        Mark all pool connections to be closed on getting back to pool.
        Closed pool doesn't allow to acquire new connections.
        """
        if self._closed:
            return
        self._closing = True

    def terminate(self):
        """Terminate pool.

        Close pool with instantly closing all acquired connections also.
        """

        self.close()

        for conn in list(self._used):
            conn.close()
            self._terminated.add(conn)

        self._used.clear()

    async def wait_closed(self):
        """
        Wait for closing all pool's connections.

        :raises RuntimeError: if pool is not closing
        """

        if self._closed:
            return
        if not self._closing:
            raise RuntimeError(".wait_closed() should be called " "after .close()")

        while self._free:
            conn = self._free.popleft()
            await conn.close()

        async with self._cond:
            while self.size > self.freesize:
                await self._cond.wait()

        self._closed = True

    def acquire(self):
        """Acquire free connection from the pool."""
        coro = self._acquire()
        return _PoolAcquireContextManager(coro, self)

    async def _acquire(self):
        if self._closing:
            raise RuntimeError("Cannot acquire connection after closing pool")
        async with self._cond:
            while True:
                await self.fill_free_pool(True)
                if self._free:
                    conn = self._free.popleft()
                    self._used.add(conn)
                    return conn
                else:
                    await self._cond.wait()

    async def fill_free_pool(self, override_min: bool = False):
        # iterate over free connections and remove timeouted ones
        free_size = len(self._free)
        n = 0
        while n < free_size:
            conn = self._free[-1]
            if conn.expired or (
                self._recycle > -1
                and self._loop.time() - conn.last_usage > self._recycle
            ):
                self._free.pop()
                await conn.close()
            else:
                self._free.rotate()
            n += 1

        while self.size < self.minsize:
            self._acquiring += 1
            try:
                conn = await connect(echo=self._echo, **self._conn_kwargs)
                # raise exception if pool is closing
                self._free.append(conn)
                self._cond.notify()
            finally:
                self._acquiring -= 1
        if self._free:
            return

        if override_min and self.size < self.maxsize:
            self._acquiring += 1
            try:
                conn = await connect(echo=self._echo, **self._conn_kwargs)
                # raise exception if pool is closing
                self._free.append(conn)
                self._cond.notify()
            finally:
                self._acquiring -= 1

    async def _wakeup(self):
        async with self._cond:
            self._cond.notify()

    async def release(self, conn):
        if conn in self._terminated:
            self._terminated.remove(conn)
            return
        self._used.remove(conn)
        if conn.connected:
            if self._closing:
                await conn.close()
            else:
                self._free.append(conn)
            await self._wakeup()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()
        await self.wait_closed()
