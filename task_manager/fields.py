from django.forms import CharField, ModelChoiceField
from django.core.validators import RegexValidator

from task_manager.models import Tag

NOT_PERMITED_TAG_SYMBOLS = r'[^0-9a-zA-Zа-яА-Я _|]'


class UserModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


def validate_tags(value):
    tags = value.split('|')
    for tag in tags:
        if len(tag) <= 2:
            raise ValidationError(
                'Minimum tag length is 3 chars'
            )
    if len(tags) > 10:
        raise ValidationError('You can select 10 tags maximum')


class TagsField(CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.required = False
        self.help_text = 'Separate each tag by "|"'

        validators=[
            RegexValidator(
                NOT_PERMITED_TAG_SYMBOLS,
                inverse_match=True
            ),
            validate_tags
        ]
        self.validators.extend(validators)

    def clean(self, value):
        tag_names = super().clean(value)
        tags = []
        if tag_names:
            for name in tag_names.split('|'):
                tag = Tag.objects.create(name=name.strip())
                if tag not in tags:
                    tags.add(tag)
        return tags
