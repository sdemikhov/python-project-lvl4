install:
	poetry install
lint:
	poetry run flake8 task_manager

test:
	export DJANGO_ENVIRONMENT=local
	poetry run python task_manager/manage.py test

selfcheck:
	poetry check

check: selfcheck lint test


.PHONY: install test lint selfcheck check