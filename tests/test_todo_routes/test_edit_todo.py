import copy

import pytest


from todoApp.models.Todo import *
from tests.conftest import *

EDITED_DATA = {"title": "Edited Todo", "description": "Edited Description"}


def assert_record_edited(todo, original_values, edited_data):
    # id should never change
    assert todo.id == original_values["id"]
    for key, value in original_values.items():
        # original data unaltered if no new value set
        if key not in edited_data.keys():
            assert getattr(todo, key) == value
        # original data edited if new value sent
        else:
            assert getattr(todo, key) == edited_data[key]



def assert_successful_response_edit_todo(response, original_values, edited_data):
    # expected response is original data overwritten with any values sent in edited data
    expected_values = copy.copy(original_values)
    expected_values.update(edited_data)
    # We always explicitly expect to receive the original ID
    expected_values["id"] = original_values["id"]
    # do not expect to receive any None values
    expected_response = remove_null_values(expected_values)
    assert_successful_response_generic(response, 200, expected_response)


def assert_unsuccessful_response_edit_todo(response, expected_status_code, error_message):
    assert response.status_code == expected_status_code
    assert error_message in response.json


@pytest.mark.parametrize(
    "edited_data",
    [
        pytest.param(EDITED_DATA,
                     id="title_and_description"
                     ),
        pytest.param({"title": "Edited Title"},
                     id="description_field_not_present"
                     ),
        pytest.param({"title": "Edited Title", "description": None},
                     id="description_field_null"
                     )

    ]
)
def test_successful_edit_todo_single_todo_in_database(client, edited_data, create_todo):

    todo = create_todo()
    original_values = get_original_values_todo(todo)

    response = client.patch(f"/todos/{original_values['id']}", json=edited_data)

    if client.authenticated:
        assert_record_edited(todo, original_values, edited_data)
        assert_successful_response_edit_todo(response, original_values, edited_data)
    else:
        assert_record_unchanged(todo, original_values)
        assert_unauthenticated_response(client, response)


@pytest.mark.parametrize("todo_index", [0, 1, 2])
def test_successful_edit_todo_multiple_todos_in_database(client, multiple_sample_todos, todo_index):

    todo = multiple_sample_todos[todo_index]
    original_values = get_original_values_todo(todo)
    original_id = todo.id

    response = client.patch(f"/todos/{original_values['id']}", json=EDITED_DATA)

    if client.authenticated:
        assert_successful_response_edit_todo(response, original_values, EDITED_DATA)
        for todo in multiple_sample_todos:
            original_values = get_original_values_todo(todo)
            if todo.id == original_id:
                assert_record_edited(todo, original_values, EDITED_DATA)
            else:
                assert_record_unchanged(todo, original_values)
    else:
        for todo in multiple_sample_todos:
            original_values = get_original_values_todo(todo)
            assert_record_unchanged(todo, original_values)
        assert_unauthenticated_response(client, response)


# Trying to alter non-existent records
def test_cannot_edit_non_existent_todo_empty_database(client):

    nonexistant_id = 1

    response = client.patch(f"/todos/{nonexistant_id}")

    if client.authenticated:
        assert_no_result_found_response(response, nonexistant_id)
    else:
        assert_unauthenticated_response(client, response)


def test_cannot_edit_non_existent_todo_multiple_todos_in_database(client, multiple_sample_todos):

    nonexistant_id = 4

    response = client.patch(f"/todos/{nonexistant_id}")

    if client.authenticated:
        assert_no_result_found_response(response, nonexistant_id)
    else:
        assert_unauthenticated_response(client, response)


def test_cannot_use_invalid_route_parameter_type(client):
    invalid_id = "a"
    response = client.patch(f"/todos/{invalid_id}")
    if client.authenticated:
        assert_bad_parameter_response(response)
    else:
        assert_unauthenticated_response(client, response)


# Parameters check for attempt to edit to either pre-existing on non-existing ID
@pytest.mark.parametrize("id", [1, 3])
def test_cannot_manually_change_id_attribute(client, id, multiple_sample_todos):
    old_id = id
    new_id = id + 1
    todo = multiple_sample_todos[old_id - 1]
    original_values = get_original_values_todo(todo)

    response = client.patch(f"/todos/{old_id}", json={**EDITED_DATA, "id": new_id})

    if client.authenticated:
        assert_record_unchanged(todo, original_values)
        assert_unsuccessful_response_generic(response, 400, "Error: Todo IDs cannot be edited.")
    else:
        assert_record_unchanged(todo, original_values)
        assert_unauthenticated_response(client, response)


# Validation errors

@pytest.mark.parametrize(
    "data, error_message",
    [
        pytest.param(
            {"title": "Test Title"},
            "Error: Your todo must have a unique title.",
            id="non_unique_title"
        ),
        pytest.param(
            {"description": "Domestic cats, with their graceful charms and independent natures, "
                            "enchant as beloved companions. Playful antics and soothing purrs "
                            "make them universal darlings, seamlessly integrating into diverse "
                            "households and leaving lasting impressions on hearts."},
            "Error: Your todo description must be 250 characters or fewer.",
            id="description_too_long"
        )
    ]
)
def test_cannot_edit_to_invalid_title_or_description(client, data, error_message, multiple_sample_todos):
    todo = multiple_sample_todos[1]
    original_values = get_original_values_todo(todo)
    original_id = todo.id

    response = client.patch(f"/todos/{original_id}", json=data)

    if client.authenticated:
        assert_record_unchanged(todo, original_values)
        assert_unsuccessful_response_generic(response, 400, error_message)
    else:
        assert_record_unchanged(todo, original_values)
        assert_unauthenticated_response(client, response)


def test_cannot_edit_todo_deleted_user(client, create_todo):

    todo = create_todo()
    original_values = get_original_values_todo(todo)

    if hasattr(client, "current_user"):
        user_to_delete = client.current_user
        db.session.delete(user_to_delete)
        db.session.commit()

    response = client.patch(f"/todos/{original_values['id']}", json=EDITED_DATA)

    if client.authenticated:
        # Deleting user should delete owned todos
        assert db.session.scalars(db.select(Todo).filter_by(id=original_values['id'])).first() is None
        assert_unsuccessful_response_generic(response, 404, "Error: User not found.")
    else:
        assert_unauthenticated_response(client, response)