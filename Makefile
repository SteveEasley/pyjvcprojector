all: clean build

build:
	rm -rf dist
	python3 -m build
	python -m twine upload -u __token__ dist/*

dev-setup:
	python -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements_dev.txt && \
	pip install -r requirements.txt && \
	echo "Dev setup complete. Run 'source .venv/bin/activate' to activate the virtual environment and pre-commit install."

clean:
	rm -rf dist

test:
	coverage run --source jvcprojector --module pytest && coverage report --show-missing