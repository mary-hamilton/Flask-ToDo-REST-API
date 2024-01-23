import pytest

from tests.conftest import app
from todoApp.models.User import *


INVALID_PASSWORD_STRING_EXCEPTION = "Password must contain at least one capital letter and at least one digit and must not contain spaces"


def test_successful_instantiate_user(app):
    test_user = User(first_name="Steven", last_name="Puff", username="steviep", password_plaintext="Password123")
    assert test_user is not None
    assert test_user.first_name == "Steven"
    assert test_user.last_name == "Puff"
    assert test_user.username == "steviep"
    assert test_user.check_password("Password123") is True


def test_cannot_instantiate_user_no_first_name(app):
    with pytest.raises(ValidationException) as exception_info:
        test_user = User(first_name=None, last_name="Puff", username="steviep", password_plaintext="Password123")
        assert test_user is None
        assert "Your user needs a first name" in exception_info


def test_cannot_instantiate_user_no_last_name(app):
    with pytest.raises(ValidationException) as exception_info:
        test_user = User(first_name="Steven", last_name=None, username="steviep", password_plaintext="Password123")
        assert test_user is None
        assert "Your user needs a last name" in exception_info


def test_cannot_instantiate_user_no_username(app):
    with pytest.raises(ValidationException) as exception_info:
        test_user = User(first_name="Steven", last_name="Puff", username=None, password_plaintext="Password123")
        assert test_user is None
        assert "Your user needs a username" in exception_info


def test_cannot_instantiate_user_no_password(app):
    with pytest.raises(ValidationException) as exception_info:
        test_user = User(first_name="Steven", last_name="Puff", username="steviep", password_plaintext=None)
        assert test_user is None
        assert "Your user needs a password" in exception_info


def test_cannot_instantiate_user_password_too_short(app):
    with pytest.raises(ValidationException) as exception_info:
        test_user = User(first_name="Steven", last_name="Puff", username="steviep", password_plaintext="Pass123")
        assert test_user is None
        assert "Password must be at least 8 characters long" in exception_info


def test_cannot_use_password_no_capital(app):
    with pytest.raises(ValidationException) as exception_info:
        test_user = User(first_name="Steven", last_name="Puff", username="steviep", password_plaintext="password123")
        assert test_user is None
        assert INVALID_PASSWORD_STRING_EXCEPTION in exception_info


def test_cannot_use_password_no_digit(app):
    with pytest.raises(ValidationException) as exception_info:
        test_user = User(first_name="Steven", last_name="Puff", username="steviep", password_plaintext="Password")
        assert test_user is None
        assert INVALID_PASSWORD_STRING_EXCEPTION in exception_info


def test_cannot_use_password_with_spaces(app):
    with pytest.raises(ValidationException) as exception_info:
        test_user = User(first_name="Steven", last_name="Puff", username="steviep", password_plaintext="Password 123")
        assert test_user is None
        assert INVALID_PASSWORD_STRING_EXCEPTION in exception_info


def test_serialize_function_without_ID(app):
    test_user = User(first_name="Steven", last_name="Puff", username="steviep", password_plaintext="Password123")
    public_id = test_user.public_id
    serialized_test_user = serialize_user(test_user)
    assert serialized_test_user == {"first_name": "Steven", "last_name": "Puff", "username": "steviep", "public_id": public_id}
    assert serialized_test_user.get("password") is None


def test_serialize_function_with_ID(app):
    test_user = User(first_name="Steven", last_name="Puff", username="steviep", password_plaintext="Password123")
    test_user.id = 123
    public_id = test_user.public_id
    serialized_test_user = serialize_user(test_user)
    assert serialized_test_user == {"first_name": "Steven", "last_name": "Puff", "username": "steviep", "id": 123, "public_id": public_id}
    assert serialized_test_user.get("password") is None
