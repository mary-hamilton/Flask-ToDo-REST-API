import copy

import pytest

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import make_transient

from todoApp.models.Todo import *
from tests.conftest import *

EDITED_DATA = {"title": "Edited Todo", "description": "Edited Description"}


def get_original_values(todo):
    return {"title": todo.title, "description": todo.description}


def assert_record_edited(todo, original_values, edited_data):
    for key, value in original_values.items():
        # original data unaltered if no new value set
        if key not in edited_data.keys():
            assert getattr(todo, key) == value
        # original data edited if new value sent
        else:
            assert getattr(todo, key) == edited_data[key]


def assert_record_not_edited(todo, original_values):
    # original values unedited
    for key, value in original_values.items():
        assert getattr(todo, key) == value



def assert_succesful_response_edit_todo(response, original_values, edited_data, current_user, original_id):
    assert response.status_code == 200
    # expected response is original data overwritten with any values sent in edited data
    expected_response = original_values.copy()
    expected_response.update(edited_data)
    # do not return none values
    none_values = [key for key, value in expected_response.items() if value is None]
    for key in none_values:
        del expected_response[key]
    assert response.json == {**expected_response, "id": original_id, "user_id": current_user.id}


def assert_unsuccessful_response_edit_todo(response, expected_status_code, error_message):
    assert response.status_code == expected_status_code
    assert error_message in response.json


def test_successful_edit_todo_single_todo_in_database(authenticated_client, create_todo):
    current_user = authenticated_client.current_user
    todo = create_todo()
    original_values = get_original_values(todo)
    original_id = todo.id
    response = authenticated_client.patch(f"/todos/{original_id}", json=EDITED_DATA)
    assert_record_edited(todo, original_values, EDITED_DATA)
    assert_succesful_response_edit_todo(response, original_values, EDITED_DATA, current_user, original_id)


def test_successful_edit_todo_single_todo_in_database_field_not_present(authenticated_client, create_todo):
    edited_data_no_description = {"title": "Edited Title"}
    current_user = authenticated_client.current_user
    todo = create_todo()
    original_values = get_original_values(todo)
    original_id = todo.id
    response = authenticated_client.patch(f"/todos/{original_id}", json=edited_data_no_description)
    assert_record_edited(todo, original_values, edited_data_no_description)
    assert_succesful_response_edit_todo(response, original_values, edited_data_no_description, current_user, original_id)


def test_successful_edit_todo_single_todo_in_database_null_field(authenticated_client, create_todo):
    edited_data_null_description = {"title": "Edited Title", "description": None}
    current_user = authenticated_client.current_user
    todo = create_todo()
    original_values = get_original_values(todo)
    original_id = todo.id
    response = authenticated_client.patch(f"/todos/{original_id}", json=edited_data_null_description)
    assert_record_edited(todo, original_values, edited_data_null_description)
    assert_succesful_response_edit_todo(response, original_values, edited_data_null_description, current_user, original_id)


@pytest.mark.parametrize("todo_index", [0, 1, 2])
def test_successful_edit_todo_multiple_todos_in_database(authenticated, authenticated_client, unauthenticated_client, multiple_sample_todos, todo_index):
    todo = multiple_sample_todos[todo_index]
    original_values = get_original_values(todo)
    original_id = todo.id

    if authenticated:
        client = authenticated_client
        current_user = client.current_user
    else:
        client = unauthenticated_client

    response = client.patch(f"/todos/{original_id}", json=EDITED_DATA)

    if authenticated:
        assert_succesful_response_edit_todo(response, original_values, EDITED_DATA, current_user, original_id)
        for todo in multiple_sample_todos:
            original_values = get_original_values(todo)
            if todo.id == original_id:
                assert_record_edited(todo, original_values, EDITED_DATA)
            else:
                assert_record_not_edited(todo, original_values)
    else:
        assert_unauthenticated_response(response)


def test_cannot_edit_non_existent_todo_empty_database(authenticated_client):
    response = authenticated_client.patch("/todos/1")
    assert response.status_code == 404
    assert response.json == "Error: Cannot edit todo, no result found for todo ID 1."


def test_cannot_edit_non_existent_todo_multiple_todos_in_database(authenticated_client, multiple_sample_todos):
    response = authenticated_client.patch("/todos/4")
    assert response.status_code == 404
    assert response.json == "Error: Cannot edit todo, no result found for todo ID 4."


def test_cannot_use_invalid_route_parameter_type(authenticated_client):
    response = authenticated_client.delete("/todos/a")
    assert response.status_code == 400
    assert response.json == "Error: ID route parameter must be an integer."


    # Do I really want to ignore this or should I raise an error?
def test_ignores_attempt_to_manually_change_id_attribute(authenticated_client, multiple_sample_todos):
    # ID outside existing ID range
    original_todo = Todo.query.get(3)
    make_transient(original_todo)
    response = authenticated_client.patch("/todos/3", json={**EDITED_DATA, "id": 4})
    assert response.status_code == 200
    assert response.json["id"] != 4
    assert response.json["id"] == original_todo.id
    # ID within existing ID range
    original_todo = Todo.query.get(3)
    make_transient(original_todo)
    response = authenticated_client.patch("/todos/3", json={**EDITED_DATA, "id": 2})
    assert response.status_code == 200
    assert response.json["id"] != 2
    assert response.json["id"] == original_todo.id


def test_cannot_edit_title_to_already_existing_title(authenticated_client, multiple_sample_todos):
    original_todo = db.session.scalars(db.select(Todo).filter_by(id=2)).one()
    make_transient(original_todo)
    response = authenticated_client.patch("/todos/2", json={"title": "Test Title", "description": "Test Description"})
    assert response.status_code == 400
    assert response.json == "Error: Your todo must have a unique title."
    edited_todo = db.session.scalars(db.select(Todo).filter_by(id=2)).one()
    make_transient(edited_todo)
    assert edited_todo.title != "Test Title"
    assert original_todo.title == edited_todo.title
    assert edited_todo.title != "Test Description"
    assert original_todo.description == edited_todo.description


def test_absent_request_attribute_does_not_alter_stored_data(authenticated_client, multiple_sample_todos):
    original_todo = Todo.query.get(2)
    make_transient(original_todo)
    assert original_todo.description is not None
    response = authenticated_client.patch("/todos/2", json={"title": "Edited title"})
    assert response.status_code == 200
    assert response.json["description"] == original_todo.description


def test_null_request_attribute_does_alter_stored_data(authenticated_client, multiple_sample_todos):
    original_todo = Todo.query.get(2)
    make_transient(original_todo)
    assert original_todo.description is not None
    response = authenticated_client.patch("/todos/2", json={"title": "Edited title", "description": None})
    assert response.status_code == 200
    assert response.json.get("description") != original_todo.description
    assert response.json.get("description") is None


def test_cannot_edit_description_to_be_over_250_characters(authenticated_client, multiple_sample_todos):
    original_todo = Todo.query.get(1)
    make_transient(original_todo)
    response = authenticated_client.patch("/todos/1", json={"description": "Domestic cats, with their graceful charms and independent natures, "
                                                  "enchant as beloved companions. Playful antics and soothing purrs "
                                                  "make them universal darlings, seamlessly integrating into diverse "
                                                  "households and leaving lasting impressions on hearts."})
    assert response.status_code == 400
    edited_todo = Todo.query.get(1)
    assert edited_todo.description == original_todo.description
    assert response.json == "Error: Your todo description must be 250 characters or fewer."
