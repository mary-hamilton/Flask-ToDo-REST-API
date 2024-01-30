import pytest
from sqlalchemy.exc import NoResultFound

from todoApp.models.Todo import *
from tests.conftest import *


def make_get_todo_json(expected_values, current_user):
    expected_json = {**expected_values, "user_id": current_user.id}
    expected_json = remove_null_values(expected_json)
    return expected_json

def assert_successful_response_get_todo_by_id(response, original_values, current_user):
    expected_json = make_get_todo_json(original_values, current_user)
    assert_successful_response_generic(response, 200, expected_json)

def test_successful_get_todo_when_single_todo_in_database(client, create_todo):

    todo = create_todo()
    original_values = get_original_values(todo)

    response = client.get(f"/todos/{original_values['id']}")

    if client.authenticated:
        current_user = client.current_user
        assert_successful_response_get_todo_by_id(response, original_values, current_user)
        assert_record_unchanged(todo, original_values)
    else:
        assert_unauthenticated_response(response)
        assert_record_unchanged(todo, original_values)



@pytest.mark.parametrize("index", [0, 1, 2])
def test_successful_get_todo_when_multiple_todos_in_database(client, index, multiple_sample_todos):

    todo = multiple_sample_todos[index]
    original_values = get_original_values(todo)

    response = client.get(f"/todos/{original_values['id']}")

    if client.authenticated:
        current_user = client.current_user
        assert_successful_response_get_todo_by_id(response, original_values, current_user)
        assert_record_unchanged(todo, original_values)
    else:
        assert_unauthenticated_response(response)
        assert_record_unchanged(todo, original_values)


def test_todo_not_found_when_database_empty(client):

    nonexistant_id = 1

    response = client.get(f"/todos/{nonexistant_id}")

    if client.authenticated:
        assert_no_result_found_response(response, nonexistant_id)
    else:
        assert_unauthenticated_response(response)


def test_todo_not_found_when_multiple_todos_in_database(client, multiple_sample_todos):

    nonexistant_id = 4

    response = client.get(f"/todos/{nonexistant_id}")

    if client.authenticated:
        assert_no_result_found_response(response, nonexistant_id)
    else:
        assert_unauthenticated_response(response)


def test_cannot_use_invalid_route_parameter_type(client):

    invalid_id = "a"

    response = client.get(f"/todos/{invalid_id}")

    if client.authenticated:
        assert_bad_parameter_response(response)
    else:
        assert_unauthenticated_response(response)
