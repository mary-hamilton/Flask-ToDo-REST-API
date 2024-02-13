import pytest

from tests.conftest import *

def assert_current_parent_relationship(baby_todo, parent_todo):
    assert baby_todo.parent_id == parent_todo.id
    assert baby_todo in parent_todo.children

def assert_new_parent_relationship_created(baby_todo, parent_todo, baby_original_values):
    assert baby_original_values["parent_id"] is not parent_todo.id
    assert_current_parent_relationship(baby_todo, parent_todo)


def assert_successful_response_add_parent(response, baby_original_values, parent_todo):
    expected_values = {**baby_original_values, "parent_id": parent_todo.id}
    expected_json = remove_null_values(expected_values)
    assert_successful_response_generic(response, 200, expected_json)


def confirm_original_parent_relationship(baby_todo, parent_original_values):
    # Eh do not like this
    return any(child.id == baby_todo.id for child in parent_original_values["children"])

def assert_existing_parent_relationship_removed(baby_todo, parent_todo, baby_original_values, parent_original_values):
    assert baby_original_values["parent_id"] is parent_todo.id
    assert baby_todo.parent_id is not parent_todo.id
    assert confirm_original_parent_relationship(baby_todo, parent_original_values)
    assert baby_todo not in parent_todo.children


def assert_successful_response_remove_parent(response, baby_original_values):
    expected_values = {**baby_original_values, "parent_id": None}
    expected_json = remove_null_values(expected_values)
    assert_successful_response_generic(response, 200, expected_json)


def test_add_parent_todo_to_existing_todo(client, create_todo):

    parent_todo = create_todo(title="Parent Todo")
    baby_todo = create_todo(title="Baby Todo")

    parent_original_values = get_original_values_todo(parent_todo)
    baby_original_values = get_original_values_todo(baby_todo)

    response = client.patch(f"/todos/{baby_todo.id}/toggle_parent", json={"parent_id": parent_todo.id})

    if client.authenticated:
        assert_new_parent_relationship_created(baby_todo, parent_todo, baby_original_values)
        assert_successful_response_add_parent(response, baby_original_values, parent_todo)
    else:
        assert_record_unchanged(baby_todo, baby_original_values)
        assert_record_unchanged(parent_todo, parent_original_values)
        assert_unauthenticated_response(client, response)

def test_remove_parent_todo_from_existing_todo(client, create_todo):

    parent_todo = create_todo(title="Parent Todo")
    baby_todo = create_todo(title="Baby Todo", parent_id=parent_todo.id)

    parent_original_values = get_original_values_todo(parent_todo)
    baby_original_values = get_original_values_todo(baby_todo)

    response = client.patch(f"/todos/{baby_todo.id}/toggle_parent", json={"parent_id": None})

    if client.authenticated:
        assert_existing_parent_relationship_removed(baby_todo, parent_todo, baby_original_values, parent_original_values)
        assert_successful_response_remove_parent(response, baby_original_values)
    else:
        assert_record_unchanged(baby_todo, baby_original_values)
        assert_record_unchanged(parent_todo, parent_original_values)
        assert_unauthenticated_response(client, response)


def test_replace_parent_todo_on_existing_todo(client, create_todo):

    parent_todo = create_todo(title="Parent Todo")
    new_parent_todo = create_todo(title="New Parent Todo")
    baby_todo = create_todo(title="Baby Todo", parent_id=parent_todo.id)

    parent_original_values = get_original_values_todo(parent_todo)
    new_parent_original_values = get_original_values_todo(new_parent_todo)
    baby_original_values = get_original_values_todo(baby_todo)

    response = client.patch(f"/todos/{baby_todo.id}/toggle_parent", json={"parent_id": new_parent_todo.id})

    if client.authenticated:
        assert_existing_parent_relationship_removed(baby_todo, parent_todo, baby_original_values, parent_original_values)
        assert_new_parent_relationship_created(baby_todo, new_parent_todo, baby_original_values)
        assert_successful_response_add_parent(response, baby_original_values, new_parent_todo)
    else:
        assert_record_unchanged(baby_todo, baby_original_values)
        assert_record_unchanged(parent_todo, parent_original_values)
        assert_record_unchanged(new_parent_todo, new_parent_original_values)
        assert_unauthenticated_response(client, response)


def test_cannot_create_relationship_nonexistent_parent(client, create_todo):

    nonexistent_id = 5
    baby_todo = create_todo(title="Baby Todo")

    baby_original_values = get_original_values_todo(baby_todo)

    response = client.patch(f"/todos/{baby_todo.id}/toggle_parent", json={"parent_id": nonexistent_id})

    if client.authenticated:
        assert_record_unchanged(baby_todo, baby_original_values)
        assert_unsuccessful_response_generic(response, 404, "Error: Parent or child todo does not exist.")
    else:
        assert_record_unchanged(baby_todo, baby_original_values)
        assert_unauthenticated_response(client, response)


def test_cannot_create_relationship_nonexistent_child(client, create_todo):

    nonexistent_id = 5
    parent_todo = create_todo(title="Parent Todo")

    parent_original_values = get_original_values_todo(parent_todo)

    response = client.patch(f"/todos/{nonexistent_id}/toggle_parent", json={"parent_id": parent_todo.id})

    if client.authenticated:
        assert_record_unchanged(parent_todo, parent_original_values)
        assert_unsuccessful_response_generic(response, 404, "Error: Parent or child todo does not exist.")
    else:
        assert_record_unchanged(parent_todo, parent_original_values)
        assert_unauthenticated_response(client, response)


def test_cannot_create_relationship_with_self(client, create_todo):

    baby_todo = create_todo(title="Baby Todo")

    baby_original_values = get_original_values_todo(baby_todo)

    response = client.patch(f"/todos/{baby_todo.id}/toggle_parent", json={"parent_id":baby_todo.id})

    if client.authenticated:
        assert_record_unchanged(baby_todo, baby_original_values)
        assert_unsuccessful_response_generic(response, 400, "Error: Todo cannot be its own parent.")
    else:
        assert_record_unchanged(baby_todo, baby_original_values)
        assert_unauthenticated_response(client, response)

