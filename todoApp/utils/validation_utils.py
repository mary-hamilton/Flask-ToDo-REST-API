import re

from todoApp.exceptions.validation_exception import ValidationException


def validate_todo_route_param(param):
    only_digits = re.compile(r'^\d+$')
    if not only_digits.match(param):
        raise ValidationException('ID route parameter must be an integer')