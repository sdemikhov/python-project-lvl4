from django_registration.forms import RegistrationForm
from django import forms
from django.core import validators
from django.contrib.auth.models import User

from task_manager.models import TaskStatus, Tag, Task
from task_manager import fields as tm_fields

ONLY_LETTERS = r'^[a-zA-Zа-яА-Я]+$'


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


class FilterForm(forms.Form):
    my_tasks = forms.BooleanField(
        label='My tasks',
        required=False,
    )
    status = forms.TypedChoiceField(
        coerce=int,
        label='Status',
        required=False,
    )
    creator = forms.TypedChoiceField(
        coerce=int,
        label='Creator',
        required=False,
    )
    assigned_to = forms.TypedChoiceField(
        coerce=int,
        label='Assigned to',
        required=False,
    )
    tags__in = forms.MultipleChoiceField(
        label='Tags',
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [(None, '-----')] + [
            (row.pk, getattr(row, 'name'))
            for row in TaskStatus.objects.all()
        ]
        self.fields['creator'].choices = [(None, '-----')] + [
            (user.pk, user.get_full_name())
            for user in User.objects.filter(is_staff=False)
        ]
        self.fields['assigned_to'].choices = [(None, '-----')] + [
            (user.pk, user.get_full_name())
            for user in User.objects.filter(is_staff=False)
        ]
        self.fields['tags__in'].choices = [
            (row.pk, getattr(row, 'name'))
            for row in Tag.objects.order_by('name').all()
        ]


class TaskForm(forms.ModelForm):
    tags = tm_fields.TagsField()

    class Meta:
        model = Task
        fields = (
            'name',
            'description',
            'status',
            'creator',
            'assigned_to',
            'tags',
        )
        field_classes = {
            'creator': tm_fields.UserModelChoiceField,
            'assigned_to': tm_fields.UserModelChoiceField,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['creator'].queryset = User.objects.filter(
            is_staff=False
        )
        self.fields['creator'].disabled = True

        self.fields['assigned_to'].queryset = User.objects.filter(
            is_staff=False
        )

        if kwargs.get('instance'):
            self.initial['tags'] = '|'.join(
                tag.name for tag in self.instance.tags.all()
            )

    def save(self, commit=True):
        task = super().save(commit=False)
        if commit:
            task.save()
            #self.save_m2m()
        return task

    #def save_m2m(self):
        #pass
        #task = self.instance
        #previous_tags = task.tags.all()
        #tag_names = self.cleaned_data['tags']
        #new_tags = []
        #if tag_names:
            #for name in tag_names:
                #tag, _ = Tag.objects.get_or_create(name=name)
                #new_tags.append(tag)
        ##for previous_tag in previous_tags:
            ##check = previous_tag not in new_tags
            ##if previous_tag not in new_tags:
                ##previous_tag.delete_if_not_used()
        #task.tags.set(new_tags)
        #print(f'prev_tags {previous_tags}')
        #setted_tags = task.tags.all()
        #print(f'setted_tags {setted_tags}')
