install:
	poetry install
lint:
	poetry run flake8 task_manager

test:
	poetry run coverage run manage.py test
	poetry run coverage xml

selfcheck:
	poetry check

check: selfcheck lint test

local:
	poetry run gunicorn task_manager.wsgi

migrate:
	poetry run python manage.py migrate

initadmin:
	poetry run python manage.py initadmin
initstatuses:
	poetry run python manage.py initstatuses

prepare: migrate initadmin initstatuses

.PHONY: install test lint selfcheck check local migrate initadmin