import json

import pytest

from tests.conftest import *
from tests.test_todo_routes.test_get_todo_by_id import make_get_todo_json

def make_get_all_todos_json(current_user, todo_values_list):
    expected_json = []
    if todo_values_list:
        for values in todo_values_list:
            expected_json.append(make_get_todo_json(values, current_user))
    return expected_json

def assert_successful_response_get_all_todos(response, current_user, todo_values_list=None):
    expected_json = make_get_all_todos_json(current_user, todo_values_list)
    assert_successful_response_generic(response, 200, expected_json)

def test_returns_empty_if_no_todos_exist(client):

    response = client.get('/todos')

    if client.authenticated:
        current_user = client.current_user
        assert_successful_response_get_all_todos(response, current_user)
    else:
        assert_unauthenticated_response(client, response)


def test_returns_single_todo(client, create_todo):

    todo = create_todo()
    original_values_list = [get_original_values_todo(todo)]

    response = client.get('/todos')

    if client.authenticated:
        current_user = client.current_user
        assert_successful_response_get_all_todos(response, current_user, original_values_list)
    else:
        assert_unauthenticated_response(client, response)

def test_returns_list_of_multiple_todos(client, multiple_sample_todos):

    todos = multiple_sample_todos
    original_values_list = [get_original_values_todo(todo) for todo in todos]

    response = client.get("/todos")

    if client.authenticated:
        current_user = client.current_user
        assert_successful_response_get_all_todos(response, current_user, original_values_list)
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
            assert db.session.scalars(db.select(Todo).filter_by(id=todo.id)).first() is None
        assert_unsuccessful_response_generic(response, 404, "Error: User not found.")
    else:
        assert_unauthenticated_response(client, response)