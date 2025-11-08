checkfiles = asyncodbc/ examples/ tests/ conftest.py
py_warn = PYTHONDEVMODE=1
pytest_opts = -n auto --cov=asyncodbc --tb=native -q

up:
	@uv lock --upgrade

deps:
	@uv sync --all-extras --all-groups --no-group docs $(options)

_style:
	@ruff format $(checkfiles)
	@ruff check --fix $(checkfiles)
style: deps _style

_codeqc:
	#mypy $(checkfiles)
	bandit -c pyproject.toml -r $(checkfiles)
	twine check dist/*
codeqc: build _codeqc

_check: _build
	@ruff format --check $(checkfiles) || (echo "Please run 'make style' to auto-fix style issues" && false)
	@ruff check $(checkfiles)
	$(MAKE) _codeqc
check: deps _check

_lint: _build _style _codeqc
lint: deps _lint

test: deps test_mssql

test_mssql:
	$(py_warn) TEST_DSN="DRIVER=ODBC Driver 18 for SQL Server;SERVER=127.0.0.1,1433;UID=sa;PWD=$(TEST_MSSQL_PASS);TrustServerCertificate=YES;MARS_Connection=YES" pytest $(pytest_opts)

_testall: test_mssql

testall: deps _testall
	coverage report

ci: check _testall

docs: deps
	uv pip install --group docs
	rm -fR ./build
	sphinx-build -M html docs build

_build:
	rm -fR dist/
	uv build
build: deps _build

publish: deps build
	twine upload dist/*
