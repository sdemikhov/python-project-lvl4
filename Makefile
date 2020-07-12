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

migrate:
	poetry run python manage.py migrate

initadmin:
	poetry run python manage.py initadmin
prepare: migrate initadmin

.PHONY: install test lint selfcheck check local migrate initadmin