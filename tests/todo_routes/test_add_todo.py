import pytest

from todoApp.models.Todo import *
from tests.fixtures import client, app


def test_successful_add_todo(client, app):
    data = {"title": "Test Title", "description": "Test Description"}
    expected_response_data = {**data, "id": 1}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 201
    assert added_todo is not None
    assert added_todo.title == data["title"]
    assert added_todo.description == data["description"]
    assert serialize_todo(added_todo) == expected_response_data
    assert response.json == expected_response_data


def test_can_add_todo_without_description(client, app):
    data = {"title": "Test Title"}
    expected_response_data = {**data, "id": 1}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 201
    assert added_todo is not None
    assert added_todo.title == data["title"]
    assert added_todo.description is None
    assert serialize_todo(added_todo) == expected_response_data
    assert response.json == expected_response_data


    # Validation tests

def test_cannot_add_todo_null_title(client, app):
    data = {"title": None, "description": "Test Description"}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo needs a title."


def test_cannot_add_todo_no_title_key(client, app):
    data = {"description": "Test Description"}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo needs a title."


def test_cannot_add_todo_title_over_40_characters(client, app):
    data = {"title": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARGH"}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo title must be 40 characters or under."


def test_cannot_add_todo_description_over_250_characters(client, app):
    data = {"title": "Test Title", "description": "Domestic cats, with their graceful charms and independent natures, "
                                                  "enchant as beloved companions. Playful antics and soothing purrs "
                                                  "make them universal darlings, seamlessly integrating into diverse "
                                                  "households and leaving lasting impressions on hearts."}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo description must be 250 characters or under."


def test_cannot_add_todo_with_duplicate_title(client, app):
    data = {"title": "Test Title", "description": "Test Description"}
    client.post('/todos', json=data)
    response = client.post('/todos', json=data)
    first_added_todo = Todo.query.get(1)
    second_added_todo = Todo.query.get(2)
    assert response.status_code == 400
    assert serialize_todo(first_added_todo) == {**data, "id": 1}
    assert second_added_todo is None
    assert response.json == "Error: Your todo must have a unique title."
