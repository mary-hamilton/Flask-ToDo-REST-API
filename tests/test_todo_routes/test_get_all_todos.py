import json

import pytest

from tests.conftest import *


def assert_successful_response_get_all_todos(response, todo_values_list=[]):
    assert_successful_response_generic(response, 200, todo_values_list)

def test_returns_empty_if_no_todos_exist(client):

    response = client.get('/todos')

    if client.authenticated:
        assert_successful_response_get_all_todos(response)
    else:
        assert_unauthenticated_response(client, response)


def test_returns_single_todo(client, create_todo):

    todo = create_todo()
    original_values_list = [get_original_values_todo(todo)]

    response = client.get('/todos')

    if client.authenticated:
        assert_successful_response_get_all_todos(response, original_values_list)
    else:
        assert_unauthenticated_response(client, response)

def test_returns_list_of_multiple_todos(client, multiple_sample_todos):

    todos = multiple_sample_todos
    original_values_list = [get_original_values_todo(todo) for todo in todos]

    response = client.get("/todos")

    if client.authenticated:
        assert_successful_response_get_all_todos(response, original_values_list)
    else:
        assert_unauthenticated_response(client, response)


def test_does_not_return_child_todos(client, create_todo):

    parent_todo = create_todo(title="Parent Todo")
    child_todo_1 = create_todo(title="Child Todo 1", parent_id=parent_todo.id)
    child_todo_2 = create_todo(title="Child Todo 2", parent_id=parent_todo.id)

    parent_todo_original_values = get_original_values_todo(parent_todo)
    child_todo_1_original_values = get_original_values_todo(child_todo_1)
    child_todo_2_original_values = get_original_values_todo(child_todo_2)

    expected_values_list = [parent_todo_original_values]

    response = client.get("/todos")

    response_json = response.json

    if client.authenticated:
        assert_successful_response_get_all_todos(response, expected_values_list)
        assert len(response_json) == len(expected_values_list)
        assert parent_todo_original_values in response_json
        assert child_todo_1_original_values not in response_json
        assert child_todo_2_original_values not in response_json
    else:
        assert_unauthenticated_response(client, response)



def test_cannot_get_all_todos_deleted_user(client, multiple_sample_todos):

    if hasattr(client, "current_user"):
        user_to_delete = client.current_user
        db.session.delete(user_to_delete)
        db.session.commit()

    response = client.get('/todos')

    if client.authenticated:
        # Deleting user should delete their todos
        for todo in multiple_sample_todos:
            assert db.session.get(Todo, todo.id) is None
        assert_unsuccessful_response_generic(response, 404, "Error: User not found.")
    else:
        assert_unauthenticated_response(client, response)