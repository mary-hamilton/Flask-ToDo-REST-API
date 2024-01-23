import pytest

from todoApp.models.Todo import *
from tests.conftest import authenticated_client


def test_successful_add_todo(authenticated_client):
    current_user = authenticated_client.current_user
    data = {"title": "Test Title", "description": "Test Description"}
    expected_response_data = {**data, "user_id" : current_user.id, "id": 1}
    response = authenticated_client.post('/todos', json=data)
    added_todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=1)).first()
    assert response.status_code == 201
    assert added_todo is not None
    assert added_todo.title == data["title"]
    assert added_todo.description == data["description"]
    assert serialize_todo(added_todo) == expected_response_data
    assert response.json == expected_response_data


def test_successful_add_todo_without_description(authenticated_client):
    current_user = authenticated_client.current_user
    data = {"title": "Test Title", "user_id": 1}
    expected_response_data = {**data, "user_id" : current_user.id, "id": 1}
    response = authenticated_client.post('/todos', json=data)
    added_todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=1)).first()
    assert response.status_code == 201
    assert added_todo is not None
    assert added_todo.title == data["title"]
    assert added_todo.description is None
    assert serialize_todo(added_todo) == expected_response_data
    assert response.json == expected_response_data


    # Validation tests

def test_cannot_add_todo_with_invalid_data_type(authenticated_client):
    current_user = authenticated_client.current_user
    data = {"title": "Test Title", "description": 1234}
    response = authenticated_client.post('/todos', json=data)
    added_todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=1)).first()
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your description must be a string."


def test_cannot_add_todo_null_title(authenticated_client):
    current_user = authenticated_client.current_user
    data = {"title": None, "description": "Test Description"}
    response = authenticated_client.post('/todos', json=data)
    added_todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=1)).first()
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo needs a title."


def test_cannot_add_todo_no_title_key(authenticated_client):
    current_user = authenticated_client.current_user
    data = {"description": "Test Description"}
    response = authenticated_client.post('/todos', json=data)
    added_todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=1)).first()
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo needs a title."


def test_cannot_add_todo_title_over_40_characters(authenticated_client):
    current_user = authenticated_client.current_user
    data = {"title": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARGH"}
    response = authenticated_client.post('/todos', json=data)
    added_todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=1)).first()
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo title must be 40 characters or fewer."


def test_cannot_add_todo_description_over_250_characters(authenticated_client):
    current_user = authenticated_client.current_user
    data = {"title": "Test Title", "description": "Domestic cats, with their graceful charms and independent natures, "
                                                  "enchant as beloved companions. Playful antics and soothing purrs "
                                                  "make them universal darlings, seamlessly integrating into diverse "
                                                  "households and leaving lasting impressions on hearts."}
    response = authenticated_client.post('/todos', json=data)
    added_todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=1)).first()
    assert response.status_code == 400
    assert added_todo is None
    assert response.json == "Error: Your todo description must be 250 characters or fewer."


def test_cannot_add_todo_with_duplicate_title(authenticated_client):
    current_user = authenticated_client.current_user
    data = {"title": "Test Title", "description": "Test Description"}
    authenticated_client.post('/todos', json=data)
    response = authenticated_client.post('/todos', json=data)
    first_added_todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=1)).first()
    second_added_todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id).filter_by(id=2)).first()
    assert response.status_code == 400
    assert serialize_todo(first_added_todo) == {**data, "user_id" : current_user.id, "id": 1}
    assert second_added_todo is None
    assert response.json == "Error: Your todo must have a unique title."


