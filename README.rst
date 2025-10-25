asyncodbc
=========
.. image:: https://travis-ci.com/tortoise/asyncodbc.svg?branch=main
    :target: https://travis-ci.com/tortoise/asyncodbc
.. image:: https://coveralls.io/repos/tortoise/asyncodbc/badge.svg?branch=main&service=github
    :target: https://coveralls.io/github/tortoise/asyncodbc?branch=main
.. image:: https://img.shields.io/pypi/v/asyncodbc.svg
    :target: https://pypi.python.org/pypi/asyncodbc

**asyncodbc** is a Python 3.9+ module that makes it possible to access ODBC_ databases
with asyncio_. It relies on the awesome pyodbc_ library and preserves the same look and
feel. *asyncodbc* was written using `async/await` syntax (PEP492_) and only support
Python that is not end-of-life(EOL).  Internally *asyncodbc* employs threads to avoid
blocking the event loop, threads_ are not that as bad as you think!. Other
drivers like motor_ use the same approach.

**asyncodbc** is fully compatible and tested with uvloop_. Take a look at the test
suite, all tests are executed with both the default event loop and uvloop_.

Supported Databases
-------------------

**asyncodbc** should work with all databases supported by pyodbc_. But for now the
library has been tested with: **SQLite**, **MySQL** and **PostgreSQL**. Feel
free to add other databases to the test suite by submitting a PR.

Basic Example
-------------

**asyncodbc** is based on pyodbc_ and provides the same api, you just need
to use  ``yield from conn.f()`` or ``await conn.f()`` instead of ``conn.f()``

Properties are unchanged, so ``conn.prop`` is correct as well as
``conn.prop = val``.


.. code:: python

    import asyncio
    import asyncodbc


    loop = asyncio.get_event_loop()


    async def test_example():
        dsn = 'Driver=SQLite;Database=sqlite.db'
        conn = await asyncodbc.connect(dsn=dsn, loop=loop)

        cur = await conn.cursor()
        await cur.execute("SELECT 42 AS age;")
        rows = await cur.fetchall()
        print(rows)
        print(rows[0])
        print(rows[0].age)
        await cur.close()
        await conn.close()

    loop.run_until_complete(test_example())


Connection Pool
---------------
Connection pooling is ported from aiopg_ and relies on PEP492_ features:

.. code:: python

    import asyncio
    import asyncodbc


    loop = asyncio.get_event_loop()


    async def test_pool():
        dsn = 'Driver=SQLite;Database=sqlite.db'
        pool = await asyncodbc.create_pool(dsn=dsn, loop=loop)

        async with pool.acquire() as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT 42;")
            r = await cur.fetchall()
            print(r)
            await cur.close()
            await conn.close()
        pool.close()
        await pool.wait_closed()

    loop.run_until_complete(test_pool())


Context Managers
----------------
`Pool`, `Connection` and `Cursor` objects support the context management
protocol:

.. code:: python

    import asyncio
    import asyncodbc


    loop = asyncio.get_event_loop()


    async def test_example():
        dsn = 'Driver=SQLite;Database=sqlite.db'

        async with asyncodbc.create_pool(dsn=dsn, loop=loop) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT 42 AS age;')
                    val = await cur.fetchone()
                    print(val)
                    print(val.age)

    loop.run_until_complete(test_example())


Installation
------------

In a linux environment pyodbc_ (hence *asyncodbc*) requires the unixODBC_ library.
You can install it using your package manager, for example::

      $ sudo apt-get install unixodbc
      $ sudo apt-get install unixodbc-dev

then::

   pip install asyncodbc


Run tests
---------

For testing purposes you need to install docker_ and the development
requirements::

    $ pip install -r pyproject.toml --group test -e .

In order to simplify development you should install the provided docker container.
This way you don't need to install any databases or other system libraries, everything happens inside the container.

Then just execute::

    $ make docker_build
    $ make docker_test

The test will automatically pull images and build containers with
the required databases.

*NOTE:* Running tests requires Python 3.9 or higher.


Other SQL Drivers
-----------------

* asyncpg_ - asyncio client for PostgreSQL
* aiomysql_ - asyncio client form MySQL


Requirements
------------

* Python_ 3.9+
* pyodbc_
* uvloop_ (optional)


.. _Python: https://www.python.org
.. _asyncio: http://docs.python.org/3.14/library/asyncio.html
.. _pyodbc: https://github.com/mkleehammer/pyodbc
.. _uvloop: https://github.com/MagicStack/uvloop
.. _ODBC: https://en.wikipedia.org/wiki/Open_Database_Connectivity
.. _asyncpg: https://github.com/MagicStack/asyncpg
.. _aiopg: https://github.com/aio-libs/aiopg
.. _aiomysql: https://github.com/aio-libs/aiomysql
.. _PEP492: https://www.python.org/dev/peps/pep-0492/
.. _unixODBC: http://www.unixodbc.org/
.. _threads: http://techspot.zzzeek.org/2015/02/15/asynchronous-python-and-databases/
.. _docker: https://docs.docker.com/engine/installation/
.. _motor: https://emptysqua.re/blog/motor-0-7-beta/
