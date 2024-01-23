import pytest

from todoApp.models.Todo import *
from tests.conftest import client, app, create_user


def test_successful_add_todo(client, app, create_user):
    data = {"title": "Test Title", "description": "Test Description", "user_id": 1}
    expected_response_data = {**data, "id": 1}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 201
    assert added_todo is not None
    assert added_todo.title == data["title"]
    assert added_todo.description == data["description"]
    assert serialize_todo(added_todo) == expected_response_data
    assert response.json == expected_response_data


def test_successful_add_todo_without_description(client, app, create_user):
    data = {"title": "Test Title", "user_id": 1}
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

def test_cannot_add_todo_with_invalid_data_type(client, app, create_user):
    data = {"title": "Test Title", "description": 1234, "user_id": 1}
    response = client.post('/todos', json=data)
    assert response.json == "Error: Your description must be a string."


def test_cannot_add_todo_null_title(client, app, create_user):
    data = {"title": None, "description": "Test Description", "user_id": 1}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo needs a title."


def test_cannot_add_todo_no_title_key(client, app, create_user):
    data = {"description": "Test Description", "user_id": 1}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo needs a title."


def test_cannot_add_todo_title_over_40_characters(client, app, create_user):
    data = {"title": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARGH", "user_id": 1}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo title must be 40 characters or fewer."


def test_cannot_add_todo_description_over_250_characters(client, app, create_user):
    data = {"title": "Test Title", "description": "Domestic cats, with their graceful charms and independent natures, "
                                                  "enchant as beloved companions. Playful antics and soothing purrs "
                                                  "make them universal darlings, seamlessly integrating into diverse "
                                                  "households and leaving lasting impressions on hearts.", "user_id": 1}
    response = client.post('/todos', json=data)
    added_todo = Todo.query.get(1)
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo description must be 250 characters or fewer."


def test_cannot_add_todo_with_duplicate_title(client, app, create_user):
    data = {"title": "Test Title", "description": "Test Description", "user_id": 1}
    client.post('/todos', json=data)
    response = client.post('/todos', json=data)
    first_added_todo = Todo.query.get(1)
    second_added_todo = Todo.query.get(2)
    assert response.status_code == 400
    assert serialize_todo(first_added_todo) == {**data, "id": 1}
    assert second_added_todo is None
    assert response.json == "Error: Your todo must have a unique title."


