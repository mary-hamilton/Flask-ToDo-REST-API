import pytest

from todoApp import Todo
from todoApp import create_app
from todoApp.config import *
from todoApp.extensions.db import db
from todoApp.models.User import User


@pytest.fixture()
def app():
    test_app = create_app(TestConfig)
    with test_app.app_context():
        yield test_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture
def create_todo():

    description_sentinel = object()

    def _create_todo(title='Test Title', description=description_sentinel):
        if description is description_sentinel:
            description = 'Test Description'
        todo_to_add = Todo(title=title, description=description)
        db.session.add(todo_to_add)
        db.session.commit()
    return _create_todo


@pytest.fixture
def multiple_sample_todos(client, create_todo):
    create_todo()
    create_todo(title="Test Title 2")
    create_todo(title="Test Title 3", description=None)


@pytest.fixture
def create_user():
    def _create_user(first_name="Jan", last_name="West", username="janwest", password_plaintext="Password123"):
        user_to_add = User(first_name=first_name, last_name=last_name, username=username, password_plaintext=password_plaintext)
        db.session.add(user_to_add)
        db.session.commit()
    return _create_user
