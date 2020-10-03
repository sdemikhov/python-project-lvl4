.PHONY: install
install:
	poetry install

.PHONY: lint
lint:
	poetry run flake8 task_manager

.PHONY: test
test:
	poetry run coverage run manage.py test
	poetry run coverage xml

.PHONY: selfcheck
selfcheck:
	poetry check

.PHONY: check
check: selfcheck lint test

.PHONY: local
local:
	poetry run gunicorn task_manager.wsgi

.PHONY: migrate
migrate:
	poetry run python manage.py migrate

.PHONY: collectstatic
collectstatic:
	poetry run python manage.py collectstatic

.PHONY: initadmin
initadmin:
	poetry run python manage.py initadmin

.PHONY: initstatuses
initstatuses:
	poetry run python manage.py initstatuses

.PHONY: prepare
prepare:
	migrate collectstatic initadmin initstatuses

.PHONY: heroku_release
heroku_release:
	python manage.py migrate
	python manage.py initadmin
	python manage.py initstatuses
