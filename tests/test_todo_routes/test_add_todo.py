import pytest

from tests.test_todo_routes.test_toggle_parent import assert_current_parent_relationship
from todoApp.models.Todo import *
from tests.conftest import *


MISSING_TITLE_ERROR = "Error: Your todo needs a title."
DUPLICATE_TITLE_ERROR = "Error: Your todo title must be unique."


# CHANGE THIS
def assert_todo_added_to_database(expected_values, todo_id):
    todo = db.session.scalars(db.session.query(Todo).filter_by(id=todo_id)).one()
    assert todo is not None
    for key, value in expected_values.items():
        assert getattr(todo, key) == value



def assert_todo_not_added_to_database(expected_id):
    added_todo = db.session.get(Todo, expected_id)
    assert added_todo is None


def assert_successful_response_add_todo(response, expected_values):
    assert_successful_response_generic(response, 201, expected_values)



@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {"title": "Test Title", "description": "Test Description"},
            id="with_description"),
        pytest.param(
            {"title": "Test Title"},
            id="without_description"
        )
    ]
)
def test_add_to_empty_database(client, data):

    expected_id = 1

    response = client.post('/todos', json=data)

    if client.authenticated:
        current_user = client.current_user
        expected_values = {**data, "user_id": current_user.id, "id": expected_id, "checked": False}
        assert_successful_response_add_todo(response, expected_values)
        assert_todo_added_to_database(expected_values, expected_id)
    else:
        assert_todo_not_added_to_database(expected_id)
        assert_unauthenticated_response(client, response)


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {"title": "Test Title 4", "description": "Test Description"},
            id="with_description"),
        pytest.param(
            {"title": "Test Title 4"},
            id="without_description"
        ),
    ]
)
def test_add_to_populated_database(client, data, multiple_sample_todos):

    expected_id = 4

    response = client.post('/todos', json=data)

    if client.authenticated:
        current_user = client.current_user
        expected_values = {**data, "user_id": current_user.id, "id": expected_id, "checked": False}
        assert_successful_response_add_todo(response, expected_values)
        assert_todo_added_to_database(expected_values, expected_id)
    else:
        assert_todo_not_added_to_database(expected_id)
        assert_unauthenticated_response(client, response)


def test_add_with_parent_todo(client, create_todo):

    expected_id = 2
    parent_todo = create_todo(title="Parent Todo")
    data = {"title": "Child Todo", "parent_id": parent_todo.id}

    response = client.post('/todos', json=data)

    if client.authenticated:
        current_user = client.current_user
        expected_values = {**data, "user_id": current_user.id, "id": expected_id, "parent_id": parent_todo.id, "checked": False}
        assert_successful_response_add_todo(response, expected_values)
        assert_todo_added_to_database(expected_values, expected_id)
        added_todo = db.session.get(Todo, expected_id)
        assert_current_parent_relationship(added_todo, parent_todo)
    else:
        assert_todo_not_added_to_database(expected_id)
        assert_unauthenticated_response(client, response)





    # Validation tests

@pytest.mark.parametrize(
    "data,error_message",
    [
        pytest.param(
            {"title": "Test Title", "description": 1234},
            "Error: Your description must be a string.",
            id="invalid_data_type"
        ),
        pytest.param(
            {"title": None, "description": "Test Description"},
            MISSING_TITLE_ERROR,
            id="null_title"
        ),
        pytest.param(
            {"description": "Test Description"},
            MISSING_TITLE_ERROR,
            id="missing_title"
        ),
        pytest.param(
            {"title": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARGH"},
            "Error: Your todo title must be 40 characters or fewer.",
            id="title_over_40_characters"
        ),
        pytest.param(
            {"title": "Test Title", "description": "Domestic cats, with their graceful charms and independent natures, "
                                                   "enchant as beloved companions. Playful antics and soothing purrs "
                                                   "make them universal darlings, seamlessly integrating into diverse "
                                                   "households and leaving lasting impressions on hearts."},
            "Error: Your todo description must be 250 characters or fewer.",
            id="description_over_250_characters"
        )
    ]
)
def test_cannot_add_todo_validation_errors(client, data, error_message):

    expected_id = 1

    response = client.post('/todos', json=data)

    if client.authenticated:
        assert_todo_not_added_to_database(expected_id)
        assert_unsuccessful_response_generic(response, 400, error_message)
    else:
        assert_todo_not_added_to_database(expected_id)
        assert_unauthenticated_response(client, response)



def test_cannot_add_todo_with_duplicate_title(client, create_todo):

    expected_id = 2
    data = {"title": "Test Title", "description": "Test Description"}
    existing_todo = create_todo(**data)
    existing_values = get_original_values_todo(existing_todo)

    response = client.post('/todos', json=data)

    if client.authenticated:
        assert_record_unchanged(existing_todo, existing_values)
        assert_todo_not_added_to_database(expected_id)
        assert_unsuccessful_response_generic(response, 400, DUPLICATE_TITLE_ERROR)
    else:
        assert_todo_not_added_to_database(expected_id)
        assert_unauthenticated_response(client, response)


def test_cannot_add_todo_deleted_user(client):

    expected_id = 1
    data = {"title": "Test Title", "description": "Test Description"}

    if hasattr(client, "current_user"):
        user_to_delete = client.current_user
        db.session.delete(user_to_delete)
        db.session.commit()

    response = client.post('/todos', json=data)

    if client.authenticated:
        assert_todo_not_added_to_database(expected_id)
        assert_unsuccessful_response_generic(response, 404, "Error: User not found.")
    else:
        assert_todo_not_added_to_database(expected_id)
        assert_unauthenticated_response(client, response)

