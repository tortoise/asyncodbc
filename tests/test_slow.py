import gc
from unittest import mock

import pytest

import asyncodbc


@pytest.mark.asyncio
async def test___del__(dsn, recwarn, executor):
    conn = await asyncodbc.connect(dsn=dsn, executor=executor)
    exc_handler = mock.Mock()
    loop = conn.loop
    loop.set_exception_handler(exc_handler)

    del conn
    gc.collect()
    w = recwarn.pop()
    assert issubclass(w.category, ResourceWarning)

    msg = {"connection": mock.ANY, "message": "Unclosed connection"}  # conn was deleted
    if loop.get_debug():
        msg["source_traceback"] = mock.ANY
    exc_handler.assert_called_with(loop, msg)
    assert not loop.is_closed()
