from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from task_manager import models as tm_models


class TaskStatusModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        tm_models.TaskStatus.objects.create(name='task_status_model_test')

    def test_field_name_label(self):
        status = tm_models.TaskStatus.objects.get(
            name='task_status_model_test'
        )
        field_label = status._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_field_name_max_length(self):
        status = tm_models.TaskStatus.objects.get(
            name='task_status_model_test'
        )
        max_length = status._meta.get_field('name').max_length
        self.assertEquals(max_length, 100)

    def test_field_name_unique_constraint(self):
        tm_models.TaskStatus.objects.create(name='unique')
        with self.assertRaises(IntegrityError):
            tm_models.TaskStatus.objects.create(name='unique')

    def test_init_statuses(self):
        tm_models.TaskStatus.init_statuses()

        for default_status in tm_models.DEFAULT_TASK_STATUSES:
            status = tm_models.TaskStatus.objects.get(
                name=default_status
            )
            self.assertEquals(status.name, default_status)

    def test__str__(self):
        status = tm_models.TaskStatus.objects.get(
            name='task_status_model_test'
        )
        self.assertEquals(
            status.__str__(),
            'task_status_model_test'
        )

    def test__repr__(self):
        status = tm_models.TaskStatus.objects.get(
            name='task_status_model_test'
        )
        self.assertEquals(
            status.__repr__(),
            '<TaskStatus task_status_model_test>'
        )


class TagModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        tm_models.Tag.objects.create(name='tag_model_test')

    def test_field_name_label(self):
        tag = tm_models.Tag.objects.get(name='tag_model_test')
        field_label = tag._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_field_name_max_length(self):
        tag = tm_models.Tag.objects.get(name='tag_model_test')
        max_length = tag._meta.get_field('name').max_length
        self.assertEquals(max_length, 100)

    def test_field_name_unique_constraint(self):
        tm_models.Tag.objects.create(name='unique')
        with self.assertRaises(IntegrityError):
            tm_models.Tag.objects.create(name='unique')

    def test__str__(self):
        status = tm_models.Tag.objects.get(
            name='tag_model_test'
        )
        self.assertEquals(
            status.__str__(),
            'tag_model_test'
        )

    def test__repr__(self):
        status = tm_models.Tag.objects.get(
            name='tag_model_test'
        )
        self.assertEquals(
            status.__repr__(),
            '<Tag tag_model_test>'
        )


class TaskModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        status = tm_models.TaskStatus.objects.create(name='test_status')
        tag1 = tm_models.Tag.objects.create(name='task')
        tag2 = tm_models.Tag.objects.create(name='manager')
        user_ivanov = User.objects.create(username='iivanov')
        user_petrov = User.objects.create(username='ppetrov')

        task = tm_models.Task.objects.create(
            name='task_model_test',
            status=status,
            creator=user_ivanov,
            assigned_to=user_petrov,
        )
        task.tags.set([tag1, tag2])

    def test_field_name_max_length(self):
        task = tm_models.Task.objects.get(name='task_model_test')
        max_length = task._meta.get_field('name').max_length
        self.assertEquals(max_length, 200)

    def test_field_status(self):
        task = tm_models.Task.objects.get(name='task_model_test')
        self.assertEquals(task.status.name, 'test_status')

    def test_field_creator(self):
        task = tm_models.Task.objects.get(name='task_model_test')
        self.assertEquals(task.creator.username, 'iivanov')

    def test_field_assigned_to(self):
        task = tm_models.Task.objects.get(name='task_model_test')
        self.assertEquals(task.assigned_to.username, 'ppetrov')

    def test_field_tags(self):
        task = tm_models.Task.objects.get(name='task_model_test')
        for tag in task.tags.all():
            self.assertTrue(tag.name in ['task', 'manager'])

    def test__str__(self):
        status = tm_models.Task.objects.get(
            name='task_model_test'
        )
        self.assertEquals(
            status.__str__(),
            'task_model_test'
        )

    def test__repr__(self):
        status = tm_models.Task.objects.get(
            name='task_model_test'
        )
        self.assertEquals(
            status.__repr__(),
            '<Task task_model_test>'
        )
