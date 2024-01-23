import pytest
from sqlalchemy.exc import NoResultFound

from todoApp.models.Todo import *
from tests.conftest import *


def test_successful_delete_todo_single_todo_in_database(client, create_todo):
    create_todo()
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json == "Todo successfully deleted."
    assert Todo.query.get(1) is None
    assert len(client.get("/todos").json) == 0


def test_successful_delete_todo_multiple_todos_in_database(client, multiple_sample_todos):
    original_todos_length = len(client.get("/todos").json)
    response = client.delete("/todos/3")
    assert response.status_code == 200
    assert response.json == "Todo successfully deleted."
    assert Todo.query.get(3) is None
    todos_after_deletion_length = len(client.get("/todos").json)
    assert todos_after_deletion_length == original_todos_length - 1


def test_cannot_delete_non_existent_todo_empty_database(client):
    response = client.delete("/todos/1")
    assert response.status_code == 404
    assert response.json == "Error: Cannot delete todo, no result found for todo ID 1."


def test_cannot_delete_non_existent_todo_multiple_todos_in_database(client, multiple_sample_todos):
    original_todos_length = len(client.get("/todos").json)
    response = client.delete("/todos/4")
    assert response.status_code == 404
    assert response.json == "Error: Cannot delete todo, no result found for todo ID 4."
    todos_after_deletion_length = len(client.get("/todos").json)
    assert todos_after_deletion_length == original_todos_length


def test_cannot_use_invalid_route_parameter_type(client):
    response = client.delete("/todos/a")
    assert response.status_code == 400
    assert response.json == "Error: ID route parameter must be an integer."

