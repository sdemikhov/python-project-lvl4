import re
from django_registration.forms import RegistrationForm
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from task_manager.models import TaskStatus, Tag, Task
from task_manager import fields as tm_fields

ONLY_LETTERS = r'^[a-zA-Zа-яА-Я]+$'

MY_TASKS = 'my_tasks'
TAGS = 'tags'
STATUS = 'status'
ASSIGNED_TO = 'assigned_to'

FILTERS = (
    (MY_TASKS, 'My tasks'),
    (TAGS, 'Tags'),
    (STATUS, 'Status'),
    (ASSIGNED_TO, 'Assigned to'),
)
NOT_PERMITED_TAG_SYMBOLS = r'[^0-9a-zA-Zа-яА-Я _|]'


class CustomRegistrationForm(RegistrationForm):
    first_name = forms.CharField(
        label='First name',
        max_length=100,
        required=True,
        validators=[
            validators.RegexValidator(
                ONLY_LETTERS,
                message='First name can contain letters only'
            )
        ],
        help_text='Required. Letters Only',
    )
    last_name = forms.CharField(
        label='Last name',
        max_length=100,
        required=True,
        validators=[
            validators.RegexValidator(
                ONLY_LETTERS,
                message='Last name can contain letters only'
            )
        ],
        help_text='Required. Letters Only',
    )

    class Meta(RegistrationForm.Meta):
        fields = ['first_name', 'last_name'] + RegistrationForm.Meta.fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
        return user


class FilterTypeForm(forms.Form):
    filter_ = forms.ChoiceField(
        label='Filter',
        choices=FILTERS
    )


class FilterByMyTasksForm(forms.Form):
    filter_type = MY_TASKS


class FilterByTagsForm(forms.Form):
    filter_type = TAGS
    tags = forms.MultipleChoiceField(
        label='Select tags',
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].choices = [
            (row.pk, getattr(row, 'name'))
            for row in Tag.objects.order_by('name').all()
        ]


class FilterByStatusForm(forms.Form):
    filter_type = STATUS
    status = forms.TypedChoiceField(
        coerce=int,
        label='Select status',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            (row.pk, getattr(row, 'name'))
            for row in TaskStatus.objects.all()
        ]


class FilterByAssignedToForm(forms.Form):
    filter_type = ASSIGNED_TO
    assigned_to = forms.TypedChoiceField(
        coerce=int,
        label='Select person',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].choices = [
            (user.pk, user.get_full_name())
            for user in User.objects.filter(is_staff=False)
        ]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            'name',
            'description',
            'status',
            'creator',
            'assigned_to',
        )
        field_classes = {
            'creator': tm_fields.UserModelChoiceField,
            'assigned_to': tm_fields.UserModelChoiceField
        }

        labels = {
            'assigned_to': 'Assigned to'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['creator'].queryset = User.objects.filter(
            is_staff=False
        )
        self.fields['assigned_to'].queryset = User.objects.filter(
            is_staff=False
        )


def validate_tags(value):
    match = re.search(NOT_PERMITED_TAG_SYMBOLS, value)
    if match:
        raise ValidationError('Invalid tag chars')
    tags = value.split('|')
    for tag in tags:
        if len(tag) <= 2:
            raise ValidationError(
                'Minimum tag length is 3 chars'
            )
    if len(tags) > 10:
        raise ValidationError('You can select 10 tags maximum')


class CreateTagsForm(forms.Form):
    tags = forms.CharField(
        help_text=(
            'Separate each tag by "|"'
        ),
        validators=[validate_tags],
        required=False
    )


class StatusForm(forms.ModelForm):
    class Meta:
        model = TaskStatus
        fields = (
            'name',
        )
