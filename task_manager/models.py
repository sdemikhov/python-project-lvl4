from django.db import models
from django.contrib.auth.models import User

DEFAULT_TASK_STATUS_ID = 1
DEFAULT_TASK_STATUSES = [
    'New',
    'In progress',
    'Testing',
    'Done'
]


class TaskStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)

    @classmethod
    def init_statuses(cls):
        for status in DEFAULT_TASK_STATUSES:
            try:
                cls.objects.get(name=status)
            except cls.DoesNotExist:
                new_status = cls(name=status)
                new_status.save()

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<TaskStatus {}>'.format(self.name)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def delete_if_not_used(self):
        bounded_tasks = self.task_set.all()
        print(f'$$$$$$$$$$$$$$$$ {bounded_tasks}')
        if not bounded_tasks:
            print(f'!!!!!!!!!!delete {self}')
            self.delete()

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Tag {}>'.format(self.name)


class Task(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.ForeignKey(
        TaskStatus,
        related_name='bounded_tasks',
        on_delete=models.CASCADE,
        default=DEFAULT_TASK_STATUS_ID
    )
    creator = models.ForeignKey(
        User,
        related_name='created_tasks',
        on_delete=models.CASCADE,
    )
    assigned_to = models.ForeignKey(
        User,
        related_name='assigned_tasks',
        on_delete=models.CASCADE,
    )
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Task {}>'.format(self.name)
