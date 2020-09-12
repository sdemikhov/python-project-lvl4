import django
from django.core.management.base import BaseCommand

from task_manager.models import TaskStatus


class Command(BaseCommand):
    help = 'Check for task statuses and create if it does not exist.'

    def handle(self, *args, **kwargs):
        django.setup()
        TaskStatus.init_statuses()
