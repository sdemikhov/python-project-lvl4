install:
	poetry install
lint:
	poetry run flake8 task_manager

test:
	poetry run python manage.py test

selfcheck:
	poetry check

check: selfcheck lint test

local:
	poetry run gunicorn task_manager.wsgi

.PHONY: install test lint selfcheck check local