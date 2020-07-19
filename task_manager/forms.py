from django_registration.forms import RegistrationForm
from django import forms
from django.core import validators

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
        fields = RegistrationForm.Meta.fields + ['first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
        return user
