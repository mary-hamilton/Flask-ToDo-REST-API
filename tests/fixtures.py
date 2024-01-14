import pytest

from todoApp import Todo
from todoApp.__init__ import create_app
from todoApp.config import *
from todoApp.extensions.db import db


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
