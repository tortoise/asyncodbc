.. asyncodbc documentation master file, created by
   sphinx-quickstart on Sun Jan 18 22:02:31 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to asyncodbc's documentation!
===================================

.. _GitHub: https://github.com/tortoise/asyncodbc
.. _asyncio: http://docs.python.org/3.14/library/asyncio.html
.. _aioodbc: https://github.com/aio-libs/aioodbc
.. _pyodbc: https://github.com/mkleehammer/pyodbc
.. _PEP492: https://www.python.org/dev/peps/pep-0492/
.. _ODBC: https://learn.microsoft.com/en-us/sql/odbc/microsoft-open-database-connectivity-odbc
.. _unixODBC: http://www.unixodbc.org/
.. _threads: http://techspot.zzzeek.org/2015/02/15/asynchronous-python-and-databases/

**asyncodbc** is Python 3.9+ module that makes possible accessing ODBC_ databases
with asyncio_. It is rely on awesome pyodbc_ library, preserve same look and
feel. *asyncodbc* was written using `async/await` syntax (PEP492_) and only support
Python that is not end-of-life(EOL).  Internally *asyncodbc* employs threads
to avoid blocking the event loop, btw threads_ are not that bad as you think :)


Features
--------
* Implements `asyncio` :term:`DBAPI` *like* interface for
  :term:`ODBC`.  It includes :ref:`asyncodbc-connection`,
  :ref:`asyncodbc-cursor` and :ref:`asyncodbc-pool` objects.
* Support connection pooling.


Source code
-----------

The project is hosted on GitHub_

Please feel free to file an issue on `bug tracker
<https://github.com/tortoise/asyncodbc/issues>`_ if you have found a bug
or have some suggestion for library improvement.

The library uses `Github Action <https://github.com/tortoise/asyncodbc/actions?query=workflow:ci>`_ for
Continious Integration and `Coveralls
<https://coveralls.io/r/tortoise/asyncodbc?branch=main>`_ for
coverage reports.


Dependencies
------------

- Python 3.9+ (PEP492_ coroutines)
- pyodbc_
- unixODBC_


Authors and License
-------------------

The ``asyncodbc`` package is inspired by aioodbc_.
It's Apache-2.0 licensed.

Feel free to improve this package and send a pull request to GitHub_.

Contents:
---------

.. toctree::
   :maxdepth: 2

   examples
   tuning
   glossary
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
