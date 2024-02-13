import pytest
from sqlalchemy.exc import NoResultFound

from todoApp.models.Todo import *
from tests.conftest import *



def assert_record_deleted(todo_id):
    assert db.session.get(Todo, todo_id) is None


def assert_successful_response_delete_todo(response):
    assert_successful_response_generic(response, 200, "Todo successfully deleted.")

def test_successful_delete_todo_single_todo_in_database(client, create_todo):

    todo = create_todo()
    original_values = get_original_values_todo(todo)

    response = client.delete(f"/todos/{original_values['id']}")

    if client.authenticated:
        assert_successful_response_delete_todo(response)
        assert_record_deleted(original_values['id'])
    else:
        assert_record_unchanged(todo, original_values)
        assert_unauthenticated_response(client, response)


def test_successful_delete_todo_multiple_todos_in_database(client, multiple_sample_todos):

    todo = multiple_sample_todos[0]
    original_values = get_original_values_todo(todo)

    response = client.delete(f"/todos/{original_values['id']}")

    if client.authenticated:
        assert_successful_response_delete_todo(response)
        assert_record_deleted(original_values['id'])
    else:
        assert_record_unchanged(todo, original_values)
        assert_unauthenticated_response(client, response)


def test_successful_delete_todo_also_deletes_child_todos(client, create_todo):

    parent_todo = create_todo(title="Parent Todo")
    child_todo_1 = create_todo(title="Child Todo 1", parent_id=parent_todo.id)
    child_todo_2 = create_todo(title="Child Todo 2", parent_id=parent_todo.id)
    child_todo_3 = create_todo(title="Child Todo 3", parent_id=parent_todo.id)
    child_todos = [child_todo_1, child_todo_2, child_todo_3]

    parent_original_values = get_original_values_todo(parent_todo)
    child_original_values = [get_original_values_todo(child_todo) for child_todo in child_todos]

    response = client.delete(f"/todos/{parent_todo.id}")

    if client.authenticated:
        assert_record_deleted(parent_todo.id)
        for child_todo in child_todos:
            assert_record_deleted(child_todo.id)
        assert_successful_response_delete_todo(response)
    else:
        assert_record_unchanged(parent_todo, parent_original_values)
        for index, child_todo in enumerate(child_todos):
            assert_record_unchanged(child_todo, child_original_values[index])
        assert_unauthenticated_response(client, response)




def test_cannot_delete_non_existent_todo_empty_database(client):

    nonexistant_id = 1

    response = client.delete(f"/todos/{nonexistant_id}")

    if client.authenticated:
        assert_unsuccessful_response_generic(response, 404, f"Error: Cannot delete todo, no result found for todo ID {nonexistant_id}.")
    else:
        assert_unauthenticated_response(client, response)




def test_cannot_delete_non_existent_todo_multiple_todos_in_database(client, multiple_sample_todos):

    nonexistant_id = 4

    response = client.delete(f"/todos/{nonexistant_id}")

    if client.authenticated:
        assert_unsuccessful_response_generic(response, 404, f"Error: Cannot delete todo, no result found for todo ID {nonexistant_id}.")
    else:
        assert_unauthenticated_response(client, response)


def test_cannot_use_invalid_route_parameter_type(client):

    nonexistant_id = "a"

    response = client.delete(f"/todos/{nonexistant_id}")

    if client.authenticated:
        assert_bad_parameter_response(response)
    else:
        assert_unauthenticated_response(client, response)


