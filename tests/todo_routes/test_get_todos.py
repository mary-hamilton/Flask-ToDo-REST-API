import pytest

from todoApp.models.Todo import *
from tests.fixtures import client, app


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
def get_todos_response_with_multiple_todos(client, create_todo):
    create_todo()
    create_todo(title="Test Title 2")
    create_todo(title="Test Title 3", description=None)
    return client.get('/todos')


def test_returns_empty_if_no_todos_exist(client):
    response = client.get('/todos')
    assert response.status_code == 204
    assert response.json is None


def test_returns_list_of_todos(client, get_todos_response_with_multiple_todos):
    response = get_todos_response_with_multiple_todos
    response_data = response.json
    assert response.status_code == 200
    assert len(response_data) == 3
    assert response_data[0].get('title') == 'Test Title'
    assert response_data[0].get('description') == 'Test Description'
    assert response_data[1].get('title') == 'Test Title 2'
    assert response_data[1].get('description') == 'Test Description'
    assert response_data[2].get('title') == 'Test Title 3'
    assert response_data[2].get('description') is None

