from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MaximumLengthValidator:
    def __init__(self, max_length=24):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(self.get_help_text(pronoun="this"), code="password_too_long", params={'max_length': self.max_length})

    def get_help_text(self, pronoun="your"):
        return _(f"{pronoun.capitalize()} password must contain no more than {self.max_length} characters")
