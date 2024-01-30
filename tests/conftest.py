import pytest

from todoApp import Todo
from todoApp import create_app
from todoApp.blueprints.user_routes import make_token
from todoApp.config import *
from todoApp.extensions.db import db
from todoApp.models.User import User


MISSING_TOKEN_ERROR = "Error: Token is missing"

@pytest.fixture()
def app():
    test_app = create_app(TestConfig)
    with test_app.app_context():
        yield test_app


@pytest.fixture()
def unauthenticated_client(app):
    client = app.test_client()
    client.authenticated = False
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


@pytest.fixture(params=[True, False], ids=["authenticated", "unauthenticated"])
def client(request, authenticated_client, unauthenticated_client):
    if request.param:
        return authenticated_client
    else:
        return unauthenticated_client


@pytest.fixture
def create_todo(authenticated_client):

    description_sentinel = object()

    def _create_todo(title='Test Title', user_id=authenticated_client.current_user.id, description=description_sentinel):
        if description is description_sentinel:
            description = 'Test Description'
        todo_to_add = Todo(title=title, user_id=user_id, description=description)
        db.session.add(todo_to_add)
        db.session.commit()
        added_todo = db.session.scalars(db.select(Todo).filter_by(id=todo_to_add.id)).first()
        return added_todo
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
        added_user = db.session.scalars(db.select(User).filter_by(username=username)).first()
        return added_user
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
    added_user = db.session.scalars(db.select(User).filter_by(username=username)).first()
    return added_user

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

def assert_unauthenticated_response(response):
    assert_unsuccessful_response_generic(response, 401, MISSING_TOKEN_ERROR)


def get_original_values(todo):
    return {"title": todo.title, "description": todo.description, "id": todo.id}

def remove_null_values(dict):
    dict_to_edit = dict.copy()
    none_values = [key for key, value in dict_to_edit.items() if value is None]
    for key in none_values:
        del dict_to_edit[key]
    return dict_to_edit


def assert_record_unchanged(todo, original_values):
    # original values unedited
    for key, value in original_values.items():
        assert getattr(todo, key) == value
