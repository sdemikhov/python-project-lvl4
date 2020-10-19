from django.test import TestCase
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from task_manager import models as tm_models
from task_manager import forms as tm_forms
from task_manager import fields as tm_fields


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
        cls.task = tm_models.Task.objects.create(
            name='task_test',
            description='desc',
            creator=cls.ivanov,
            assigned_to=cls.petrov,
            status=tm_models.TaskStatus.objects.create(name='new_test'),
        )
        cls.task.tags.set(
            [
                tm_models.Tag.objects.create(name='task'),
                tm_models.Tag.objects.create(name='test')
            ]
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
                'tags'
            )
        )

    def test_form_model(self):
        form = tm_forms.TaskForm()
        self.assertEquals(
            form.Meta().model,
            tm_models.Task
        )

    def test_form_field_classes(self):
        form = tm_forms.TaskForm()
        self.assertTrue(
            isinstance(
                form.fields['creator'],
                tm_fields.UserModelChoiceField
            )
        )
        self.assertTrue(
            form.fields['creator'].disabled
        )
        self.assertEquals(
            form.fields['creator'].label_from_instance(self.ivanov),
            self.ivanov.get_full_name()
        )
        self.assertTrue(
            isinstance(
                form.fields['assigned_to'],
                tm_fields.UserModelChoiceField
            )
        )
        self.assertEquals(
            form.fields['assigned_to'].label_from_instance(self.ivanov),
            self.ivanov.get_full_name()
        )
        self.assertTrue(
            form.fields['tags'],
            tm_fields.TagsField
        )

    def test_field_creator_queryset(self):
        form = tm_forms.TaskForm()
        self.assertEquals(
            len(form.fields['creator'].queryset),
            2
        )
        self.assertEquals(
            set(form.fields['creator'].queryset),
            {self.ivanov, self.petrov}
        )

    def test_field_assigned_to_queryset(self):
        form = tm_forms.TaskForm()
        self.assertEquals(
            len(form.fields['assigned_to'].queryset),
            2
        )
        self.assertEquals(
            set(form.fields['assigned_to'].queryset),
            {self.ivanov, self.petrov}
        )

    def test_field_tags_type(self):
        form = tm_forms.TaskForm()
        self.assertTrue(form.fields['tags'], forms.CharField)

    def test_field_tags_help_text(self):
        form = tm_forms.TaskForm()
        self.assertEquals(
            form.fields['tags'].help_text,
            'Separate each tag by "|"'
        )

    def test_field_tags_required(self):
        form = tm_forms.TaskForm()
        self.assertFalse(form.fields['tags'].required)

    def test_field_tags_validators_regex(self):
        form = tm_forms.TaskForm()
        regex_validator = form.fields['tags'].validators[1]
        self.assertTrue(
            isinstance(
                regex_validator,
                validators.RegexValidator
            )
        )
        self.assertTrue(
            regex_validator.inverse_match,
        )

    def test_field_tags_validators_validate_tags(self):
        form = tm_forms.TaskForm()
        self.assertEquals(
                form.fields['tags'].validators[2],
                tm_fields.validate_tags
        )

    def test_field_tags_validators_validate_tags(self):
        form = tm_forms.TaskForm()
        self.assertEquals(
                form.fields['tags'].validators[2],
                tm_fields.validate_tags
        )

    def test_field_tags_instance_as_initial(self):
        form = tm_forms.TaskForm(instance=self.task)
        self.assertEquals(
                form.initial['tags'],
                'task|test'
        )

class ValidateTagsTest(TestCase):
    def test_min_tag_length(self):
        with self.assertRaises(ValidationError):
            tm_fields.validate_tags('t|tag|name')

        with self.assertRaises(ValidationError):
            tm_fields.validate_tags('test|ta|name')

        with self.assertRaises(ValidationError):
            tm_fields.validate_tags('test|tag|na')
        self.assertEquals(
            tm_fields.validate_tags('test|tag|name'),
            None
        )

    def test_max_tags_count(self):
        with self.assertRaises(ValidationError):
            tm_fields.validate_tags(
                'one|two|three|four|five|six|seven|eight|nine|ten|eleven'
            )
        self.assertEquals(
            tm_fields.validate_tags(
                'one|two|three|four|five|six|seven|eight|nine|ten'
            ),
            None
        )
