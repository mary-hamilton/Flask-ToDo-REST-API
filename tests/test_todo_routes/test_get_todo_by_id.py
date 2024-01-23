import pytest
from sqlalchemy.exc import NoResultFound

from todoApp.models.Todo import *
from tests.conftest import *


def test_successful_get_todo_when_single_todo_in_database(authenticated_client, create_todo):
    create_todo()
    response = authenticated_client.get("/todos/1")
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["title"] == "Test Title"
    assert response.json["description"] == "Test Description"


def test_successful_get_todo_when_multiple_todos_in_database(authenticated_client, multiple_sample_todos):
    response = authenticated_client.get("/todos/2")
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["title"] == "Test Title 2"
    assert response.json.get("description") == "Test Description"
    response = authenticated_client.get("/todos/3")
    assert response.status_code == 200
    assert response.json is not None
    assert response.json["title"] == "Test Title 3"
    assert response.json.get("description") is None


def test_todo_not_found_when_database_empty(authenticated_client):
    response = authenticated_client.get("/todos/1")
    assert response.status_code == 404
    assert response.json == "Error: No result found for todo ID 1."


def test_todo_not_found_when_multiple_todos_in_database(authenticated_client, multiple_sample_todos):
    response = authenticated_client.get("/todos/4")
    assert response.status_code == 404
    assert response.json == "Error: No result found for todo ID 4."


def test_cannot_use_invalid_route_parameter_type(authenticated_client):
    response = authenticated_client.get("/todos/a")
    assert response.status_code == 400
    assert response.json == "Error: ID route parameter must be an integer."
