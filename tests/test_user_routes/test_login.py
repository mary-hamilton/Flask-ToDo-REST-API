import jwt
import pytest
from flask import current_app

from tests.fixtures import client, app, create_user


def test_successful_login(client, create_user):
    create_user()
    response = client.post('/login', auth=("janwest", "Password123"))
    assert response.status_code == 200
    token = response.json["token"]
    assert jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])["sub"] == "janwest"


def test_user_not_found(client):
    response = client.post('/login', auth=("janwest", "Password123"))
    assert response.status_code == 404
    assert response.json == "Error: User not found."


def test_no_username(client):
    response = client.post('/login', auth=("", "Password123"))
    assert response.status_code == 401
    assert response.json == "Error: Username and password required."
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_no_password(client):
    response = client.post('/login', auth=("janwest", ""))
    assert response.status_code == 401
    assert response.json == "Error: Username and password required."
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_wrong_password(client, create_user):
    create_user()
    response = client.post('/login', auth=("janwest", "Password1234"))
    assert response.status_code == 401
    assert response.json == "Error: Incorrect password."
    assert response.headers["WWW-Authenticate"] == "Basic"
