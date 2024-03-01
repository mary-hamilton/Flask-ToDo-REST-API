import copy
from datetime import datetime, timedelta

import jwt
import pytest
from flask import current_app

from todoApp import Todo
from todoApp import create_app
from todoApp.blueprints.user_routes import make_token
from todoApp.config import *
from todoApp.extensions.db import db
from todoApp.models.Todo import serialize_todo, serialize_todo_with_children
from todoApp.models.User import User


MISSING_TOKEN_ERROR = "Error: Token is missing"
EXPIRED_TOKEN_ERROR = "Error: Token has expired."
INVALID_TOKEN_ERROR = "Error: Invalid token."

@pytest.fixture()
def app():
    test_app = create_app(TestConfig)
    with test_app.app_context():
        yield test_app


@pytest.fixture()
def not_logged_in_client(app):
    client = app.test_client()
    client.authenticated = False
    client.problem = "not_logged_in"
    return client


@pytest.fixture()
def expired_token_client(app, create_user):

    current_user = create_user
    current_time = datetime.utcnow()
    expiry_time = datetime.utcnow()

    token = make_test_token(current_user.public_id, current_time, expiry_time)
    client = app.test_client()
    client.current_user = current_user
    client.authenticated = False
    client.problem = "expired_token"
    client.environ_base['HTTP_AUTHORIZATION'] = f"Bearer {token}"
    return client


@pytest.fixture()
def invalid_token_client(app, create_user):

    current_user = create_user
    current_time = datetime.utcnow() + timedelta(minutes=5)
    expiry_time = datetime.utcnow()

    token = make_test_token(current_user.public_id, current_time, expiry_time)
    client = app.test_client()
    client.current_user = current_user
    client.authenticated = False
    client.problem = "invalid_token"
    client.environ_base['HTTP_AUTHORIZATION'] = f"Bearer {token}"
    return client


@pytest.fixture()
def deleted_user_client(app, create_user):
    # Make user and token for user
    current_user = create_user
    token = make_token(current_user.public_id)
    # Delete user
    db.session.delete(current_user)
    db.session.commit()

    client = app.test_client()
    client.authenticated = False
    client.problem = "deleted_user"
    client.environ_base['HTTP_AUTHORIZATION'] = f"Bearer {token}"
    return client


@pytest.fixture()
def authenticated_client(app, create_user):
    current_user = create_user
    token = make_token(current_user.public_id)
    client = app.test_client()
    # is this legit?
    client.current_user = current_user
    client.authenticated = True
    client.environ_base['HTTP_AUTHORIZATION'] = f"Bearer {token}"
    return client


@pytest.fixture(params=["authenticated", "not_logged_in", "expired_token", "invalid_token"])
def client(request):
    if request.param == "authenticated":
        return request.getfixturevalue("authenticated_client")
    if request.param == "not_logged_in":
        return request.getfixturevalue("not_logged_in_client")
    if request.param == "expired_token":
        return request.getfixturevalue("expired_token_client")
    if request.param == "invalid_token":
        return request.getfixturevalue("invalid_token_client")


@pytest.fixture
def create_todo(authenticated_client):

    description_sentinel = object()

    def _create_todo(title='Test Title', user_id=authenticated_client.current_user.id, description=description_sentinel, parent_id=None, checked=False):
        if description is description_sentinel:
            description = 'Test Description'
        todo_to_add = Todo(title=title, user_id=user_id, description=description, parent_id=parent_id)
        todo_to_add.checked = checked
        db.session.add(todo_to_add)
        db.session.commit()
        db.session.refresh(todo_to_add)
        return todo_to_add
    return _create_todo


@pytest.fixture
def multiple_sample_todos(create_todo):
    todo_1 = create_todo()
    todo_2 = create_todo(title="Test Title 2")
    todo_3 = create_todo(title="Test Title 3", description=None)
    return [todo_1, todo_2, todo_3]


@pytest.fixture
def create_user_flex():
    def _create_user(first_name="Jan", last_name="West", username="janwest", password_plaintext="Password123"):
        user_to_add = User(first_name=first_name, last_name=last_name, username=username, password_plaintext=password_plaintext)
        db.session.add(user_to_add)
        db.session.commit()
        db.session.refresh(user_to_add)
        return user_to_add
    return _create_user


@pytest.fixture
def create_user():
    first_name = "Jan"
    last_name = "West"
    username = "janwest"
    password_plaintext = "Password123"
    user_to_add = User(first_name=first_name, last_name=last_name, username=username,
                       password_plaintext=password_plaintext)
    db.session.add(user_to_add)
    db.session.commit()
    db.session.refresh(user_to_add)
    return user_to_add


def make_test_token(public_user_id, current_time, expiry_time):
    payload = {"sub": public_user_id, "iat": current_time, "exp": expiry_time}
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")


def assert_successful_response_generic(response, expected_status_code, expected_json):
    assert response.status_code == expected_status_code
    assert response.json == expected_json


def assert_unsuccessful_response_generic(response, expected_status_code, error_message):
    assert response.status_code == expected_status_code
    assert error_message in response.json


def assert_no_result_found_response(response, nonexistant_id):
    not_found_message = f"Error: No result found for todo ID {nonexistant_id}."
    assert_unsuccessful_response_generic(response, 404, not_found_message)


def assert_bad_parameter_response(response):
    bad_parameter_message = "Error: ID route parameter must be an integer."
    assert_successful_response_generic(response, 400, bad_parameter_message)


def assert_unauthenticated_response(client, response):
    if client.problem == "not_logged_in":
        assert_unsuccessful_response_generic(response, 401, MISSING_TOKEN_ERROR)
    if client.problem == "expired_token":
        assert_unsuccessful_response_generic(response, 401, EXPIRED_TOKEN_ERROR)
    if client.problem == "invalid_token":
        assert_unsuccessful_response_generic(response, 401, INVALID_TOKEN_ERROR)


def get_original_values_todo(todo):
    db.session.refresh(todo)
    test_todo = serialize_todo(todo)

    return test_todo


def get_original_values_todo_with_children(todo):
    return serialize_todo_with_children(todo)


def remove_null_values(dict):
    dict_to_edit = copy.deepcopy(dict)
    # Removes empty and None values but not False (to handle .checked)
    none_values = [key for key, value in dict_to_edit.items() if not value and value is not False]
    for key in none_values:
        del dict_to_edit[key]
    return dict_to_edit


def assert_record_unchanged(todo, original_values):
    # original values unedited
    for key, value in original_values.items():
        if isinstance(value, list):
            for index, item in enumerate(value):
                assert item["id"] == getattr(todo, key)[index].id
        else:
            assert getattr(todo, key) == value
