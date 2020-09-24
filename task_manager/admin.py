from django.contrib import admin

from task_manager.models import TaskStatus, Tag, Task

admin.site.register((TaskStatus, Tag, Task))
