import pytest
from sqlalchemy.exc import NoResultFound

from todoApp.models.Todo import *
from tests.conftest import *


def assert_successful_response_get_todo_by_id(response, original_values):
    assert_successful_response_generic(response, 200, original_values)


def test_successful_get_todo_when_single_todo_in_database(client, create_todo):

    todo = create_todo()
    original_values = get_original_values_todo(todo)

    response = client.get(f"/todos/{original_values['id']}")

    if client.authenticated:
        assert_successful_response_get_todo_by_id(response, original_values)
        assert_record_unchanged(todo, original_values)
    else:
        assert_unauthenticated_response(client, response)
        assert_record_unchanged(todo, original_values)



@pytest.mark.parametrize("index", [0, 1, 2])
def test_successful_get_todo_when_multiple_todos_in_database(client, index, multiple_sample_todos):

    todo = multiple_sample_todos[index]
    original_values = get_original_values_todo(todo)

    response = client.get(f"/todos/{original_values['id']}")

    if client.authenticated:
        assert_successful_response_get_todo_by_id(response, original_values)
        assert_record_unchanged(todo, original_values)
    else:
        assert_unauthenticated_response(client, response)
        assert_record_unchanged(todo, original_values)


def test_successful_get_todo_with_child_todos(client, create_todo):
    parent_todo = create_todo(title="Parent Todo")
    create_todo(title="Child Todo 1", parent_id=parent_todo.id)
    create_todo(title="Child Todo 2", parent_id=parent_todo.id)

    parent_original_values = get_original_values_todo_with_children(parent_todo)

    response = client.get(f"/todos/{parent_original_values['id']}")

    if client.authenticated:
        assert_successful_response_get_todo_by_id(response, parent_original_values)
        assert_record_unchanged(parent_todo, parent_original_values)
    else:
        assert_unauthenticated_response(client, response)
        assert_record_unchanged(parent_todo, parent_original_values)


def test_todo_not_found_when_database_empty(client):

    nonexistant_id = 1

    response = client.get(f"/todos/{nonexistant_id}")

    if client.authenticated:
        assert_no_result_found_response(response, nonexistant_id)
    else:
        assert_unauthenticated_response(client, response)


def test_todo_not_found_when_multiple_todos_in_database(client, multiple_sample_todos):

    nonexistant_id = 4

    response = client.get(f"/todos/{nonexistant_id}")

    if client.authenticated:
        assert_no_result_found_response(response, nonexistant_id)
    else:
        assert_unauthenticated_response(client, response)


def test_cannot_use_invalid_route_parameter_type(client):

    invalid_id = "a"

    response = client.get(f"/todos/{invalid_id}")

    if client.authenticated:
        assert_bad_parameter_response(response)
    else:
        assert_unauthenticated_response(client, response)


def test_cannot_get_todo_deleted_user(client, create_todo):

    todo = create_todo()
    original_values = get_original_values_todo(todo)

    if hasattr(client, "current_user"):
        user_to_delete = client.current_user
        db.session.delete(user_to_delete)
        db.session.commit()

    response = client.get(f"/todos/{original_values['id']}")

    if client.authenticated:
        # Deleting user should delete owned todos
        assert db.session.get(Todo, original_values['id']) is None
        assert_unsuccessful_response_generic(response, 404, "Error: User not found.")
    else:
        assert_unauthenticated_response(client, response)