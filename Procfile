release: python task_manager/manage.py migrate
web:  gunicorn --pythonpath task_manager task_manager.wsgi --log-file -
