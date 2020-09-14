from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from task_manager import models as tm_models
from task_manager import forms as tm_forms

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


class CustomRegistrationFormTest(TestCase):
    def test_field_first_name_label(self):
        form = tm_forms.CustomRegistrationForm()
        self.assertEquals(
            form.fields['first_name'].label,
            'First name'
        )

    def test_field_first_name_help_text(self):
        form = tm_forms.CustomRegistrationForm()
        self.assertEquals(
            form.fields['first_name'].help_text,
            'Required. Letters Only'
        )

    def test_field_first_name_validation(self):
        form_data = {
            'last_name': 'Ivanov',
            'username': 'vivanov',
            'email': 'ivanov@example.com',
            'password1': 't1e2s3t4',
            'password2': 't1e2s3t4',
        }

        form_data['first_name'] = '123'
        form = tm_forms.CustomRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data['first_name'] = 'Vasya 123'
        form = tm_forms.CustomRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data['first_name'] = 'Vasya-A'
        form = tm_forms.CustomRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data['first_name'] = '^%*)(*@#_+'
        form = tm_forms.CustomRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_field_last_name_label(self):
        form = tm_forms.CustomRegistrationForm()
        self.assertEquals(
            form.fields['last_name'].label,
            'Last name'
        )

    def test_field_last_name_help_text(self):
        form = tm_forms.CustomRegistrationForm()
        self.assertEquals(
            form.fields['last_name'].help_text,
            'Required. Letters Only'
        )

    def test_field_last_name_validation(self):
        form_data = {
            'last_name': 'Vasya',
            'username': 'vivanov',
            'email': 'ivanov@example.com',
            'password1': 't1e2s3t4',
            'password2': 't1e2s3t4',
        }

        form_data['last_name'] = 'Ivanov123'
        form = tm_forms.CustomRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data['last_name'] = 'iv@nov'
        form = tm_forms.CustomRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data['last_name'] = 'i_vanov'
        form = tm_forms.CustomRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data['last_name'] = 'ivan0v'
        form = tm_forms.CustomRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def tes_save_method(self):
        form_data = {
            'first_name': 'Vasya',
            'last_name': 'Ivanov',
            'username': 'vivanov',
            'email': 'ivanov@example.com',
            'password1': 't1e2s3t4',
            'password2': 't1e2s3t4',
        }
        form = tm_forms.CustomRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        user = form.save()
        self.assertTrue(
            isinstance(user, User)
        )
        self.assertEquals(
            user.first_name,
            'Vasya'
        )
        self.assertEquals(
            user.last_name,
            'Ivanov'
        )
