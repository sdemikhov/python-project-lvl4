release: python manage.py migrate
release: python manage.py initadmin
release: python manage.py initstatuses
web:  gunicorn task_manager.wsgi --log-file -
