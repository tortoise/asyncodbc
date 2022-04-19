import asyncio
import os
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
import pytest_asyncio

import asyncodbc


@pytest_asyncio.fixture
async def conn(connection_maker, database):
    connection = await connection_maker()
    await connection.execute(f"USE {database};")
    await connection.commit()
    return connection


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def database():
    connection = await asyncodbc.connect(dsn=os.getenv("TEST_DSN"), autocommit=True)
    cur = await connection.cursor()
    db = f"test_{uuid.uuid4()}".replace("-", "")
    await cur.execute(f"CREATE DATABASE {db};")
    yield db
    await cur.execute(f"DROP DATABASE {db};")
    await connection.close()


@pytest.fixture
async def connection_maker(dsn):
    cleanup = []

    async def make(**kw):
        if kw.get("executor", None) is None:
            executor = ThreadPoolExecutor(max_workers=1)
            kw["executor"] = executor
        else:
            executor = kw["executor"]

        conn = await asyncodbc.connect(dsn=dsn, **kw)
        cleanup.append((conn, executor))
        return conn

    try:
        yield make
    finally:
        for conn, executor in cleanup:
            await conn.close()
            executor.shutdown(True)


@pytest_asyncio.fixture
async def pool(dsn):
    p = await asyncodbc.create_pool(dsn=dsn)

    try:
        yield p
    finally:
        p.close()
        await p.wait_closed()


@pytest.fixture
def dsn():
    return os.getenv("TEST_DSN")


@pytest_asyncio.fixture
async def pool_maker():
    pool_list = []

    async def make(**kw):
        pool = await asyncodbc.create_pool(**kw)
        pool_list.append(pool)
        return pool

    try:
        yield make
    finally:
        for pool in pool_list:
            pool.close()
            await pool.wait_closed()


@pytest.fixture
def executor():
    return ThreadPoolExecutor(max_workers=10)


@pytest_asyncio.fixture
async def table(conn):
    cur = await conn.cursor()
    await cur.execute("CREATE TABLE t1(n INT, v VARCHAR(10));")
    await cur.execute("INSERT INTO t1 VALUES (1, '123.45');")
    await cur.execute("INSERT INTO t1 VALUES (2, 'foo');")
    await conn.commit()
    await cur.close()

    try:
        yield "t1"
    finally:
        cur = await conn.cursor()
        await cur.execute("DROP TABLE t1;")
        await cur.commit()
        await cur.close()
