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
    return app.test_client()


@pytest.fixture()
def authenticated_client(app, create_user):
    current_user = create_user
    token = make_token(current_user.public_id)
    client = app.test_client()
    # is this legit?
    client.current_user = current_user
    client.environ_base['HTTP_AUTHORIZATION'] = f"Bearer {token}"
    return client


# pytest fixture magic - if this fixture is passed along with a fixture named "authenticated",
# is will grab the value of authenticated at the point that it is called
@pytest.fixture()
def client(authenticated, authenticated_client, unauthenticated_client):
    if authenticated:
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
        added_todo = db.session.scalars(db.select(Todo).filter_by(user_id=user_id).filter_by(id=todo_to_add.id)).first()
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


# parameterized fixture; passing this fixture to test will run test for each param value
@pytest.fixture(params=[True, False], ids=["authenticated", "unauthenticated"])
def authenticated(request):
    return request.param

def assert_unsuccessful_response(response, expected_response_code, error_message):
    assert response.status_code == expected_response_code
    assert error_message in response.json


def assert_unauthenticated_response(response):
    assert_unsuccessful_response(response, 401, MISSING_TOKEN_ERROR)
