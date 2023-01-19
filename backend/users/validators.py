from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

RESERVED_USERNAME: str = r'^[me, Me, ME]*$'
ACCEPT_REGEX: bool = False
REJECT_REGEX: bool = True
USERNAME_REGEXES: list = [
    (fr'(^{RESERVED_USERNAME})$', REJECT_REGEX),
    (r'(^[\w.@+-]+)$', ACCEPT_REGEX,),
]


def name_validator(value):
    for regex, inverse_match in USERNAME_REGEXES:
        RegexValidator(
            regex=regex,
            message=_(f'{value} - недопустимые символы.'),
            inverse_match=inverse_match
        )(value)
