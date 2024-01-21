import pytest

from tests.fixtures import client, app, create_user
from todoApp import db
from todoApp.models.User import User


SAMPLE_SIGNUP_DATA = {"first_name": "Steven", "last_name": "Puff", "username": "steviep", "password_plaintext": "Password123"}
INVALID_PASSWORD_STRING_EXCEPTION = "Password must contain at least one capital letter and at least one digit and must not contain spaces"


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
def test_bad_password_length(client):
    bad_password_data = {**SAMPLE_SIGNUP_DATA, "password_plaintext": "Pass123"}
    response = client.post("/signup", json=bad_password_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == "Error: Password must be at least 8 characters long."


def test_bad_password_no_digit(client):
        bad_password_data = {**SAMPLE_SIGNUP_DATA, "password_plaintext": "Password"}
        response = client.post("/signup", json=bad_password_data)
        assert response.status_code == 400
        added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
        assert added_user is None
        assert response.json == f"Error: {INVALID_PASSWORD_STRING_EXCEPTION}."


def test_bad_password_no_capital(client):
    bad_password_data = {**SAMPLE_SIGNUP_DATA, "password_plaintext": "password123"}
    response = client.post("/signup", json=bad_password_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == f"Error: {INVALID_PASSWORD_STRING_EXCEPTION}."


def test_bad_password_spaces(client):
    bad_password_data = {**SAMPLE_SIGNUP_DATA, "password_plaintext": "Password 123"}
    response = client.post("/signup", json=bad_password_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == f"Error: {INVALID_PASSWORD_STRING_EXCEPTION}."


def test_no_username(client):
    bad_data = {**SAMPLE_SIGNUP_DATA, "username": None}
    response = client.post("/signup", json=bad_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == f"Error: Your user needs a username."


def test_no_first_name(client):
    bad_data = {**SAMPLE_SIGNUP_DATA, "first_name": None}
    response = client.post("/signup", json=bad_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == f"Error: Your user needs a first name."


def test_no_last_name(client):
    bad_data = {**SAMPLE_SIGNUP_DATA, "last_name": None}
    response = client.post("/signup", json=bad_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == f"Error: Your user needs a last name."


def test_no_password(client):
    bad_data = {**SAMPLE_SIGNUP_DATA, "password_plaintext": None}
    response = client.post("/signup", json=bad_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == f"Error: Your user needs a password."