import pytest

from todoApp.models.Todo import *
from tests.conftest import *


MISSING_TITLE_ERROR = "Error: Your todo needs a title."
DUPLICATE_TITLE_ERROR = "Error: Your todo title must be unique."


def assert_database_correct_add_todo(response, expected_response_data, current_user, todo_id):
    todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=todo_id)).first()
    assert todo is not None
    for key, value in expected_response_data.items():
        assert getattr(todo, key) == value
    for key, value in response.json.items():
        assert getattr(todo, key) == value


def assert_successful_response_add_todo(response, expected_response_data):
    assert response.status_code == 201
    assert response.json == expected_response_data



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
def test_add_to_empty_database(authenticated, client, data):

    expected_id = 1
    response = client.post('/todos', json=data)

    if authenticated:
        current_user = client.current_user
        expected_response_data = {**data, "user_id": current_user.id, "id": expected_id}
        assert_successful_response_add_todo(response, expected_response_data)
        assert_database_correct_add_todo(response, expected_response_data, current_user, expected_id)
    else:
        assert_unauthenticated_response(response)


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {"title": "Test Title 4", "description": "Test Description"},
            id="with_description"),
        pytest.param(
            {"title": "Test Title 4"},
            id="without_description"
        )
    ]
)
def test_add_to_populated_database(authenticated, client, data, multiple_sample_todos):

    expected_id = 4
    response = client.post('/todos', json=data)

    if authenticated:
        current_user = client.current_user
        expected_response_data = {**data, "user_id": current_user.id, "id": expected_id}
        assert_successful_response_add_todo(response, expected_response_data)
        assert_database_correct_add_todo(response, expected_response_data, current_user, expected_id)
    else:
        assert_unauthenticated_response(response)


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
def test_cannot_add_todo_validation_errors(authenticated, client, data, error_message):
    expected_id = 1
    response = client.post('/todos', json=data)

    if authenticated:
        current_user = client.current_user
        added_todo = db.session.scalars(
            db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=expected_id)).first()
        assert added_todo is None
        assert_unsuccessful_response(response, 400, error_message)
    else:
        assert_unauthenticated_response(response)



def test_cannot_add_todo_with_duplicate_title(authenticated, client, create_todo):

    expected_id = 2
    data = {"title": "Test Title", "description": "Test Description"}
    create_todo(**data)

    response = client.post('/todos', json=data)

    if authenticated:
        current_user = client.current_user
        added_todo = db.session.scalars(
            db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=expected_id)).first()
        assert added_todo is None
        assert_unsuccessful_response(response, 400, DUPLICATE_TITLE_ERROR)
    else:
        assert_unauthenticated_response(response)
