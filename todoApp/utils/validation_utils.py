import re

from todoApp.exceptions.validation_exception import ValidationException


def get_nice_name(prop_name):
    return prop_name.replace('_', ' ')



def validate_todo_route_param(param):
    only_digits = re.compile(r'^\d+$')
    if not only_digits.match(param):
        raise ValidationException('ID route parameter must be an integer')


def validate_presence(field, value):
    if not value:
        raise ValidationException(f'Your user needs a {get_nice_name(field)}')


def validate_length(field, value, max_length):
    if value and len(value) > max_length:
        raise ValidationException(f'Your {get_nice_name(field)} must be {max_length} characters or fewer')


def validate_data_type(field, value, data_type):
    if not isinstance(value, data_type):
        # Could do with better formatting of data type here
        raise ValidationException(f'Your {get_nice_name(field)} must be a {data_type}')


def check_valid_password_string(password_plaintext):
    if len(password_plaintext) < 8:
        raise ValidationException("Password must be at least 8 characters long")
    if not re.match("^(?=.*[A-Z])(?=.*\\d)\\S+$", password_plaintext):
        raise ValidationException("Password must contain at least one capital letter and at least one digit and must not contain spaces")