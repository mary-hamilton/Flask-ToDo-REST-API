import pytest

from todoApp.models.Todo import *
from tests.fixtures import client, app


@pytest.fixture
def create_todo():
    def _create_todo(title='Test Title', description='Test Description'):
        todo_to_add = Todo(title=title, description=description)
        db.session.add(todo_to_add)
        db.session.commit()
    return _create_todo


@pytest.fixture
def get_todos_response(client, create_todo):
    create_todo()
    create_todo(title="Test Title 2")
    create_todo(title="Test Title 3")
    return client.get('/todos')


def test_returns_empty_if_no_todos_exist(client):
    response = client.get('/todos')
    assert response.status_code == 204
    assert response.text == ""


def test_returns_list_of_todos(client, get_todos_response):
    response = get_todos_response
    assert response.status_code == 200
    # more assertions

