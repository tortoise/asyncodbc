checkfiles = asyncodbc/ examples/ tests/ conftest.py
py_warn = PYTHONDEVMODE=1
pytest_opts = -n auto --cov=asyncodbc --tb=native -q

up:
	@poetry update

deps:
	@poetry install

check: deps build
ifneq ($(shell which black),)
	black --check $(checkfiles) || (echo "Please run 'make style' to auto-fix style issues" && false)
endif
	pflake8 $(checkfiles)
	#mypy $(checkfiles)
	#pylint -d C,W,R $(checkfiles)
	#bandit -r $(checkfiles)
	twine check dist/*


test_mssql: deps
	$(py_warn) TEST_DSN="DRIVER=ODBC Driver 18 for SQL Server;SERVER=127.0.0.1,1433;UID=sa;PWD=$(TEST_MSSQL_PASS);TrustServerCertificate=YES;MARS_Connection=YES" pytest $(pytest_opts)

_testall: test_mssql

testall: deps _testall
	coverage report

ci: check testall

docs: deps
	rm -fR ./build
	sphinx-build -M html docs build

style: deps
	isort -src $(checkfiles)
	black $(checkfiles)

build: deps
	rm -fR dist/
	poetry build

publish: deps build
	twine upload dist/*
