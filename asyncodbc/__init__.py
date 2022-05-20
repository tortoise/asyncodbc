import asyncio

from pyodbc import dataSources as _dataSources

from .connection import Connection, connect
from .pool import Pool, create_pool

__version__ = "0.1.1"
__all__ = ["connect", "Connection", "create_pool", "Pool", "data_sources"]


async def data_sources(executor=None):
    """Returns a dictionary mapping available DSNs to their descriptions.

    :param executor: instance of custom ThreadPoolExecutor, if not supplied
        default executor will be used
    :return dict: mapping of dsn to driver description
    """
    loop = asyncio.get_event_loop()
    sources = await loop.run_in_executor(executor, _dataSources)
    return sources
