import pytest

from todoApp.models.Todo import *
from tests.conftest import *

# Arguably; should be checking that .checked is being set to the sent value, rather than just the
# opposite of what it was before
def assert_todo_check_toggled(todo, original_values):
    assert todo.checked != original_values["checked"]

def assert_todo_check_not_toggled(todo, original_values):
    assert todo.checked == original_values["checked"]

def assert_successful_response_toggle_check(response, original_values):

    expected_json = {**original_values, "checked": not original_values["checked"]}
    assert_successful_response_generic(response, 200, expected_json)


def test_check_unchecked_todo(client, create_todo):

    todo = create_todo()

    original_values = get_original_values_todo(todo)

    response = client.patch(f"/todos/{todo.id}/check", json={"checked": True})

    if client.authenticated:
        assert_successful_response_toggle_check(response, original_values)
        assert_todo_check_toggled(todo, original_values)
    else:
        assert_todo_check_not_toggled(todo, original_values)
        assert_unauthenticated_response(client, response)


def test_uncheck_checked_todo(client, create_todo):

    todo = create_todo(checked=True)

    original_values = get_original_values_todo(todo)

    response = client.patch(f"/todos/{todo.id}/check", json={"checked": False})

    if client.authenticated:
        assert_successful_response_toggle_check(response, original_values)
        assert_todo_check_toggled(todo, original_values)
    else:
        assert_todo_check_not_toggled(todo, original_values)
        assert_unauthenticated_response(client, response)


def test_check_parent_todo_cascade(client, create_todo):

    # Parent and all children start out unchecked
    parent_todo = create_todo(title="Parent Todo")
    baby_todo_1 = create_todo(title="Baby Todo 1", parent_id=parent_todo.id)
    baby_todo_2 = create_todo(title="Baby Todo 2", parent_id=parent_todo.id)
    baby_todo_3 = create_todo(title="Baby Todo 3", parent_id=parent_todo.id)
    baby_todos = [baby_todo_1, baby_todo_2, baby_todo_3]

    parent_original_values = get_original_values_todo(parent_todo)
    baby_original_values_list = [get_original_values_todo(baby) for baby in baby_todos]

    response = client.patch(f"/todos/{parent_todo.id}/check", json={"checked": True})

    if client.authenticated:
        assert_successful_response_toggle_check(response, parent_original_values)
        assert_todo_check_toggled(parent_todo, parent_original_values)
        for baby, baby_original_values in zip(baby_todos, baby_original_values_list):
            assert_todo_check_toggled(baby, baby_original_values)
    else:
        assert_unauthenticated_response(client, response)
        assert_todo_check_not_toggled(parent_todo, parent_original_values)
        for baby, baby_original_values in zip(baby_todos, baby_original_values_list):
            assert_todo_check_not_toggled(baby, baby_original_values)



# def test_check_last_non_matching_child_checks_parent(client, create_todo):
#
#     parent_todo = create_todo(title="Parent Todo")
#     # all but one child to*do is checked
#     create_todo(title="Baby Todo 1", parent_id=parent_todo.id, checked=True)
#     create_todo(title="Baby Todo 2", parent_id=parent_todo.id, checked=True)
#     baby_todo_3 = create_todo(title="Baby Todo 3", parent_id=parent_todo.id)
#
#     parent_original_values = get_original_values_todo(parent_todo)
#     baby_todo_3_original_values = get_original_values_todo(baby_todo_3)
#
#     response = client.patch(f"/todos/{baby_todo_3.id}/check", json={"checked": True})
#
#     if client.authenticated:
#         assert_successful_response_toggle_check(response, baby_todo_3_original_values)
#         assert_todo_check_toggled(baby_todo_3, baby_todo_3_original_values)
#         assert_todo_check_toggled(parent_todo, parent_original_values)
#     else:
#         assert_todo_check_not_toggled(baby_todo_3, baby_todo_3_original_values)
#         assert_todo_check_not_toggled(parent_todo, parent_original_values)
#         assert_unauthenticated_response(client, response)



def test_uncheck_last_non_matching_child_unchecks_parent(client, create_todo):

    # parent and all children checked
    parent_todo = create_todo(title="Parent Todo", checked=True)
    create_todo(title="Baby Todo 1", parent_id=parent_todo.id, checked=True)
    create_todo(title="Baby Todo 2", parent_id=parent_todo.id, checked=True)
    baby_todo_3 = create_todo(title="Baby Todo 3", parent_id=parent_todo.id, checked=True)

    parent_original_values = get_original_values_todo(parent_todo)
    baby_todo_3_original_values = get_original_values_todo(baby_todo_3)

    response = client.patch(f"/todos/{baby_todo_3.id}/check", json={"checked": False})

    if client.authenticated:
        assert_successful_response_toggle_check(response, baby_todo_3_original_values)
        assert_todo_check_toggled(baby_todo_3, baby_todo_3_original_values)
        assert_todo_check_toggled(parent_todo, parent_original_values)
    else:
        assert_todo_check_not_toggled(baby_todo_3, baby_todo_3_original_values)
        assert_todo_check_not_toggled(parent_todo, parent_original_values)
        assert_unauthenticated_response(client, response)


# def test_check_penultimate_non_matching_child_does_not_check_parent(client, create_todo):
#
#     # one child to*do checked and two unchecked
#     parent_todo = create_todo(title="Parent Todo")
#     baby_todo_1 = create_todo(title="Baby Todo 1", parent_id=parent_todo.id, checked=True)
#     baby_todo_2 = create_todo(title="Baby Todo 2", parent_id=parent_todo.id)
#     baby_todo_3 = create_todo(title="Baby Todo 3", parent_id=parent_todo.id)
#
#     parent_original_values = get_original_values_todo(parent_todo)
#     baby_todo_1_original_values = get_original_values_todo(baby_todo_1)
#     baby_todo_2_original_values = get_original_values_todo(baby_todo_2)
#     baby_todo_3_original_values = get_original_values_todo(baby_todo_3)
#
#     response = client.patch(f"/todos/{baby_todo_3.id}/check", json={"checked": True})
#
#     if client.authenticated:
#         assert_successful_response_toggle_check(response, baby_todo_3_original_values)
#         assert_todo_check_toggled(baby_todo_3, baby_todo_3_original_values)
#         assert_todo_check_not_toggled(parent_todo, parent_original_values)
#         assert_todo_check_not_toggled(baby_todo_1, baby_todo_1_original_values)
#         assert_todo_check_not_toggled(baby_todo_2, baby_todo_2_original_values)
#     else:
#         assert_todo_check_not_toggled(baby_todo_3, baby_todo_3_original_values)
#         assert_todo_check_not_toggled(parent_todo, parent_original_values)
#         assert_todo_check_not_toggled(baby_todo_1, baby_todo_1_original_values)
#         assert_todo_check_not_toggled(baby_todo_2, baby_todo_2_original_values)
#         assert_unauthenticated_response(client, response)
