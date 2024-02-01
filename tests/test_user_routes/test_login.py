import jwt
import pytest
from flask import current_app

from tests.conftest import *
from todoApp import db
from todoApp.models.User import User


def test_successful_login(client, create_user):
    user = create_user
    username = user.username
    public_id = user.public_id
    password = "Password123"

    response = client.post('/login', auth=(username, password))

    assert response.status_code == 200
    token = response.json["token"]
    assert jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])["sub"] == public_id


def test_username_does_not_exist(not_logged_in_client):

    nonexistant_username = "sillycat"

    response = not_logged_in_client.post('/login', auth=(nonexistant_username, "Password123"))

    assert response.status_code == 404
    assert response.json == "Error: User not found."


def test_no_username(not_logged_in_client):
    response = not_logged_in_client.post('/login', auth=("", "Password123"))
    assert response.status_code == 401
    assert response.json == "Error: Username and password required."
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_no_password(not_logged_in_client):
    response = not_logged_in_client.post('/login', auth=("janwest", ""))
    assert response.status_code == 401
    assert response.json == "Error: Username and password required."
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_wrong_password(not_logged_in_client, create_user):
    response = not_logged_in_client.post('/login', auth=("janwest", "Password1234"))
    assert response.status_code == 401
    assert response.json == "Error: Incorrect password."
    assert response.headers["WWW-Authenticate"] == "Basic"
