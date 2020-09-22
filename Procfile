release: python manage.py migrate
release: python manage.py initadmin
web:  gunicorn task_manager.wsgi --log-file -
