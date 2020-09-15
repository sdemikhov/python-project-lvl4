from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django import forms

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

    def test_field_first_name_max_length(self):
        form = tm_forms.CustomRegistrationForm()
        self.assertEquals(
            form.fields['first_name'].max_length,
            100
        )

    def test_field_first_name_required(self):
        form = tm_forms.CustomRegistrationForm()
        self.assertTrue(
            form.fields['first_name'].required
        )

    def test_field_first_name_validation(self):
        form = tm_forms.CustomRegistrationForm()
        regex_validator = form.fields['first_name'].validators[0]
        self.assertEquals(
            regex_validator.regex.pattern,
            '^[a-zA-Zа-яА-Я]+$'
        )

    def test_field_last_name_label(self):
        form = tm_forms.CustomRegistrationForm()
        self.assertEquals(
            form.fields['last_name'].label,
            'Last name'
        )

    def test_field_last_name_max_length(self):
        form = tm_forms.CustomRegistrationForm()
        self.assertEquals(
            form.fields['last_name'].max_length,
            100
        )

    def test_field_last_name_required(self):
        form = tm_forms.CustomRegistrationForm()
        self.assertTrue(
            form.fields['last_name'].required
        )

    def test_field_last_name_help_text(self):
        form = tm_forms.CustomRegistrationForm()
        self.assertEquals(
            form.fields['last_name'].help_text,
            'Required. Letters Only'
        )

    def test_field_last_name_validation(self):
        form = tm_forms.CustomRegistrationForm()
        regex_validator = form.fields['last_name'].validators[0]
        self.assertEquals(
            regex_validator.regex.pattern,
            '^[a-zA-Zа-яА-Я]+$'
        )

    def test_save_method(self):
        form_data = {
            'first_name': 'Vasya',
            'last_name': 'Ivanov',
            'username': 'vivanov',
            'email': 'ivanov@example.com',
            'password1': 't1e2s3t4',
            'password2': 't1e2s3t4',
        }
        form = tm_forms.CustomRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
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


class FilterTypeFormTest(TestCase):

    def test_field_filter_label(self):
        form = tm_forms.FilterTypeForm()
        self.assertEquals(
            form.fields['filter_'].label,
            'Filter'
        )


class FilterByMyTaskFormTest(TestCase):
    def test_attribute_filter_type_label(self):
        form = tm_forms.FilterByMyTasksForm()
        self.assertEquals(
            form.filter_type,
            'my_tasks'
        )


class FilterByTagsFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tag_hello = tm_models.Tag.objects.create(name="hello")
        cls.tag_bye = tm_models.Tag.objects.create(name="bye")

    def test_attribute_filter_type_label(self):
        form = tm_forms.FilterByTagsForm()
        self.assertEquals(
            form.filter_type,
            'tags'
        )

    def test_field_tags_label(self):
        form = tm_forms.FilterByTagsForm()
        self.assertEquals(
            form.fields['tags'].label,
            'Select tags'
        )

    def test_field_tags_choices(self):
        form = tm_forms.FilterByTagsForm()
        self.assertEquals(
            set(form.fields['tags'].choices),
            {
                (self.tag_hello.pk, self.tag_hello.name),
                (self.tag_bye.pk, self.tag_bye.name),
            }
        )

    def test_field_status_widget(self):
        form = tm_forms.FilterByTagsForm()
        self.assertTrue(
            isinstance(
                form.fields['tags'].widget,
                forms.CheckboxSelectMultiple
            )
        )


class FilterByStatusFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.status_new = tm_models.TaskStatus.objects.create(name="new")
        cls.status_done = tm_models.TaskStatus.objects.create(name="done")

    def test_attribute_filter_type_label(self):
        form = tm_forms.FilterByStatusForm()
        self.assertEquals(
            form.filter_type,
            'status'
        )

    def test_field_status_label(self):
        form = tm_forms.FilterByStatusForm()
        self.assertEquals(
            form.fields['status'].label,
            'Select status'
        )

    def test_field_status_choices(self):
        form = tm_forms.FilterByStatusForm()
        self.assertEquals(
            set(form.fields['status'].choices),
            {
                (self.status_new.pk, self.status_new.name),
                (self.status_done.pk, self.status_done.name),
            }
        )


class FilterByAssignedToFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ivanov = User.objects.create(
            first_name='Petya',
            last_name='Ivanov',
            username='pivanov',
        )
        cls.petrov = User.objects.create(
            first_name='Ivan',
            last_name='Petrov',
            username='ipetrov',
        )
        cls.staff = User.objects.create(
            first_name='Nicolay',
            last_name='Sidorov',
            username='nsidorov',
            is_staff=True
        )

    def test_attribute_filter_type_label(self):
        form = tm_forms.FilterByAssignedToForm()
        self.assertEquals(
            form.filter_type,
            'assigned_to'
        )

    def test_field_assigned_to_label(self):
        form = tm_forms.FilterByAssignedToForm()
        self.assertEquals(
            form.fields['assigned_to'].label,
            'Select person'
        )

    def test_field_assigned_to_choices(self):
        form = tm_forms.FilterByAssignedToForm()
        self.assertEquals(
            set(form.fields['assigned_to'].choices),
            {
                (self.ivanov.pk, self.ivanov.get_full_name()),
                (self.petrov.pk, self.petrov.get_full_name()),
            }
        )


class TaskFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ivanov = User.objects.create(
            first_name='Misha',
            last_name='Ivanov',
            username='mivanov',
        )
        cls.petrov = User.objects.create(
            first_name='Alexandr',
            last_name='Petrov',
            username='apetrov',
        )
        cls.staff = User.objects.create(
            first_name='Alekey',
            last_name='Sidorov',
            username='asidorov',
            is_staff=True
        )

    def test_form_fields(self):
        form = tm_forms.TaskForm()
        self.assertEquals(
            form.Meta().fields,
            (
                'name',
                'description',
                'status',
                'creator',
                'assigned_to',
            )
        )
