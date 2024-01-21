import pytest

from tests.fixtures import client, app, create_user
from todoApp import db
from todoApp.models.User import User


SAMPLE_SIGNUP_DATA = {"first_name": "Steven", "last_name": "Puff", "username": "steviep", "password_plaintext": "Password123"}


def test_successful_signup(client):
    response = client.post("/signup", json=SAMPLE_SIGNUP_DATA)
    assert response is not None
    assert response.status_code == 201
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is not None
    assert added_user.first_name == "Steven"
    assert added_user.last_name == "Puff"
    assert added_user.username == "steviep"
    assert added_user.check_password("Password123") is True
    assert response.json.get("first_name") == "Steven"
    assert response.json.get("last_name") == "Puff"
    assert response.json.get("username") == "steviep"
    assert response.json.get("password_plaintext") is None


def test_username_already_taken(client, create_user):
    create_user(username="steviep")
    response = client.post("/signup", json=SAMPLE_SIGNUP_DATA)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=2)).first()
    assert added_user is None
    assert response.json == "Error: Username is already taken."


# bad password string
# missing data