from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        # Length check
        if len(password) < 8:
            raise ValidationError(
                _("This password is too short. It must contain at least 8 characters."),
                code='password_too_short',
            )
        
        # Check if the password is composed entirely of digits
        if password.isdigit():
            raise ValidationError(
                _("This password is too simple. It cannot be composed entirely of digits."),
                code='password_entirely_digits',
            )
        
        # Regex check for at least one uppercase letter, one lowercase letter, and one digit
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("This password must contain at least one lowercase letter."),
                code='password_no_lower',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code='password_no_digit',
            )

    def get_help_text(self):
        return _("Your password must contain at least 8 characters, including at least one uppercase letter, one lowercase letter, and one digit, and it cannot be composed entirely of digits.")