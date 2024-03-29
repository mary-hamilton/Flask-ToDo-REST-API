import jwt
import pytest
from flask import current_app

from tests.conftest import not_logged_in_client, app, create_user_flex
from todoApp import db
from todoApp.models.User import User

SAMPLE_SIGNUP_DATA = {"first_name": "Steven", "last_name": "Puff", "username": "steviep",
                      "password_plaintext": "Password123", "confirm_password": "Password123"}
INVALID_PASSWORD_STRING_EXCEPTION = "Password must contain at least one capital letter and at least one digit and must not contain spaces"


def test_successful_signup(not_logged_in_client):
    response = not_logged_in_client.post("/signup", json=SAMPLE_SIGNUP_DATA)
    assert response is not None
    assert response.status_code == 201
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is not None
    assert added_user.first_name == "Steven"
    assert added_user.last_name == "Puff"
    assert added_user.username == "steviep"
    assert added_user.check_password("Password123") is True
    public_id = added_user.public_id
    assert response.json["user"].get("first_name") == "Steven"
    assert response.json["user"].get("last_name") == "Puff"
    assert response.json["user"].get("username") == "steviep"
    assert response.json["user"].get("password_plaintext") is None
    token = response.json["token"]
    assert jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])["sub"] == public_id


def test_username_already_taken(not_logged_in_client, create_user_flex):
    create_user_flex(username="steviep")
    response = not_logged_in_client.post("/signup", json=SAMPLE_SIGNUP_DATA)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=2)).first()
    assert added_user is None
    assert response.json == "Error: Username is already taken."


def test_non_matching_passwords(not_logged_in_client):
    bad_password_data = {**SAMPLE_SIGNUP_DATA, "confirm_password": "Password1234"}
    response = not_logged_in_client.post("/signup", json=bad_password_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == "Error: Passwords must match."


def test_bad_password_length(not_logged_in_client):
    bad_password_data = {**SAMPLE_SIGNUP_DATA, "password_plaintext": "Pass123", "confirm_password": "Pass123"}
    response = not_logged_in_client.post("/signup", json=bad_password_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == "Error: Password must be at least 8 characters long."


def test_bad_password_no_digit(not_logged_in_client):
    bad_password_data = {**SAMPLE_SIGNUP_DATA, "password_plaintext": "Password", "confirm_password": "Password"}
    response = not_logged_in_client.post("/signup", json=bad_password_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == f"Error: {INVALID_PASSWORD_STRING_EXCEPTION}."


def test_bad_password_no_capital(not_logged_in_client):
    bad_password_data = {**SAMPLE_SIGNUP_DATA, "password_plaintext": "password123", "confirm_password": "password123"}
    response = not_logged_in_client.post("/signup", json=bad_password_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == f"Error: {INVALID_PASSWORD_STRING_EXCEPTION}."


def test_bad_password_spaces(not_logged_in_client):
    bad_password_data = {**SAMPLE_SIGNUP_DATA, "password_plaintext": "Password 123", "confirm_password": "Password 123"}
    response = not_logged_in_client.post("/signup", json=bad_password_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == f"Error: {INVALID_PASSWORD_STRING_EXCEPTION}."


def test_no_username(not_logged_in_client):
    bad_data = {**SAMPLE_SIGNUP_DATA, "username": None}
    response = not_logged_in_client.post("/signup", json=bad_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == "Error: Your user needs a username."


def test_no_first_name(not_logged_in_client):
    bad_data = {**SAMPLE_SIGNUP_DATA, "first_name": None}
    response = not_logged_in_client.post("/signup", json=bad_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == "Error: Your user needs a first name."


def test_no_last_name(not_logged_in_client):
    bad_data = {**SAMPLE_SIGNUP_DATA, "last_name": None}
    response = not_logged_in_client.post("/signup", json=bad_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == "Error: Your user needs a last name."


def test_no_password(not_logged_in_client):
    bad_data = {**SAMPLE_SIGNUP_DATA, "password_plaintext": None}
    response = not_logged_in_client.post("/signup", json=bad_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == "Error: Your user needs a password."


def test_no_confirm_password(not_logged_in_client):
    bad_data = {**SAMPLE_SIGNUP_DATA, "confirm_password": None}
    response = not_logged_in_client.post("/signup", json=bad_data)
    assert response.status_code == 400
    added_user = db.session.scalars(db.select(User).filter_by(id=1)).first()
    assert added_user is None
    assert response.json == "Error: Passwords must match."
