all: format check test

format:
	ruff format jvcprojector tests

check:
	mypy jvcprojector tests
	ruff check jvcprojector tests --fix
	pylint jvcprojector tests

test:
	pytest

build: clean
	python3 -m build
	python -m twine upload -u __token__ dist/*

clean:
	rm -rf dist build pyjvcprojector.egg-info