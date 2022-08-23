lint:
	poetry run black . --check
	poetry run flake8 .

mypy:
	poetry run mypy

static: lint mypy

format:
	poetry run black .

test:
	poetry run pytest .