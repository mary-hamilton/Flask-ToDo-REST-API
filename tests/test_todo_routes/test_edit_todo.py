import pytest

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import make_transient

from todoApp.models.Todo import *
from tests.fixtures import *

edited_data = {"title": "Edited Todo", "description": "Edited Description"}


def test_successful_edit_todo_single_todo_in_database(client, create_todo):
    create_todo()
    original_todo = Todo.query.get(1)
    make_transient(original_todo)
    response = client.patch("/todos/1", json=edited_data)
    assert response.status_code == 200
    assert original_todo != response.json
    assert response.json == {**edited_data, "id": 1}
    assert response.json["id"] == original_todo.id


def test_successful_edit_todo_multiple_todos_in_database(client, multiple_sample_todos):
    original_todo = Todo.query.get(2)
    make_transient(original_todo)
    response = client.patch("/todos/2", json=edited_data)
    assert response.status_code == 200
    assert response.json == {**edited_data, "id": 2}
    assert response.json["id"] == original_todo.id


def test_cannot_edit_non_existent_todo_empty_database(client):
    response = client.patch("/todos/1")
    assert response.status_code == 404
    assert response.json == "Error: Cannot edit todo, no result found for todo ID 1."


def test_cannot_edit_non_existent_todo_multiple_todos_in_database(client, multiple_sample_todos):
    response = client.patch("/todos/4")
    assert response.status_code == 404
    assert response.json == "Error: Cannot edit todo, no result found for todo ID 4."


def test_cannot_use_invalid_route_parameter_type(client):
    response = client.delete("/todos/a")
    assert response.status_code == 400
    assert response.json == "Error: ID route parameter must be an integer."


    # Do I really want to ignore this or should I raise an error?
def test_ignores_attempt_to_manually_change_id_attribute(client, multiple_sample_todos):
    # ID outside existing ID range
    original_todo = Todo.query.get(3)
    make_transient(original_todo)
    response = client.patch("/todos/3", json={**edited_data, "id": 4})
    assert response.status_code == 200
    assert response.json["id"] != 4
    assert response.json["id"] == original_todo.id
    # ID within existing ID range
    original_todo = Todo.query.get(3)
    make_transient(original_todo)
    response = client.patch("/todos/3", json={**edited_data, "id": 2})
    assert response.status_code == 200
    assert response.json["id"] != 2
    assert response.json["id"] == original_todo.id


def test_cannot_edit_title_to_already_existing_title(client, multiple_sample_todos):
    original_todo = db.session.scalars(db.select(Todo).filter_by(id=2)).one()
    make_transient(original_todo)
    response = client.patch("/todos/2", json={"title": "Test Title", "description": "Test Description"})
    assert response.status_code == 400
    assert response.json == "Error: Your todo must have a unique title."
    edited_todo = db.session.scalars(db.select(Todo).filter_by(id=2)).one()
    make_transient(edited_todo)
    assert edited_todo.title != "Test Title"
    assert original_todo.title == edited_todo.title
    assert edited_todo.title != "Test Description"
    assert original_todo.description == edited_todo.description


def test_absent_request_attribute_does_not_alter_stored_data(client, multiple_sample_todos):
    original_todo = Todo.query.get(2)
    make_transient(original_todo)
    assert original_todo.description is not None
    response = client.patch("/todos/2", json={"title": "Edited title"})
    assert response.status_code == 200
    assert response.json["description"] == original_todo.description


def test_null_request_attribute_does_alter_stored_data(client, multiple_sample_todos):
    original_todo = Todo.query.get(2)
    make_transient(original_todo)
    assert original_todo.description is not None
    response = client.patch("/todos/2", json={"title": "Edited title", "description": None})
    assert response.status_code == 200
    assert response.json.get("description") != original_todo.description
    assert response.json.get("description") is None


def test_cannot_edit_description_to_be_over_250_characters(client, multiple_sample_todos):
    original_todo = Todo.query.get(1)
    make_transient(original_todo)
    response = client.patch("/todos/1", json={"description": "Domestic cats, with their graceful charms and independent natures, "
                                                  "enchant as beloved companions. Playful antics and soothing purrs "
                                                  "make them universal darlings, seamlessly integrating into diverse "
                                                  "households and leaving lasting impressions on hearts."})
    assert response.status_code == 400
    edited_todo = Todo.query.get(1)
    assert edited_todo.description == original_todo.description
    assert response.json == "Error: Your todo description must be 250 characters or fewer."
