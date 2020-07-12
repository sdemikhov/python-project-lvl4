import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    help = 'Check for superuser and create if it does not exist.'

    def handle(self, *args, **kwargs):
        django.setup()
        try:
            User.objects.get(username=settings.ADMIN_USERNAME)
        except User.DoesNotExist:
            admin = User.objects.create_user(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL
            )
            admin.set_password(settings.ADMIN_PASSWORD)
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
