import jwt
import pytest
from flask import current_app

from tests.conftest import unauthenticated_client, app, create_user_flex
from todoApp import db
from todoApp.models.User import User


def test_successful_login(unauthenticated_client, create_user_flex):
    create_user_flex()
    response = unauthenticated_client.post('/login', auth=("janwest", "Password123"))
    logged_in_user = db.session.scalars(db.select(User).filter_by(username="janwest")).first()
    public_id = logged_in_user.public_id
    assert response.status_code == 200
    token = response.json["token"]
    assert jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])["sub"] == public_id


def test_user_not_found(unauthenticated_client):
    response = unauthenticated_client.post('/login', auth=("janwest", "Password123"))
    assert response.status_code == 404
    assert response.json == "Error: User not found."


def test_no_username(unauthenticated_client):
    response = unauthenticated_client.post('/login', auth=("", "Password123"))
    assert response.status_code == 401
    assert response.json == "Error: Username and password required."
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_no_password(unauthenticated_client):
    response = unauthenticated_client.post('/login', auth=("janwest", ""))
    assert response.status_code == 401
    assert response.json == "Error: Username and password required."
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_wrong_password(unauthenticated_client, create_user_flex):
    create_user_flex()
    response = unauthenticated_client.post('/login', auth=("janwest", "Password1234"))
    assert response.status_code == 401
    assert response.json == "Error: Incorrect password."
    assert response.headers["WWW-Authenticate"] == "Basic"
