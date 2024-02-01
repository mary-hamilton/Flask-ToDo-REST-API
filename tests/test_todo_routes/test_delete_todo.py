import pytest
from sqlalchemy.exc import NoResultFound

from todoApp.models.Todo import *
from tests.conftest import *



def assert_record_deleted(todo_id):
    assert db.session.scalars(db.select(Todo).filter_by(id=todo_id)).first() is None


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


