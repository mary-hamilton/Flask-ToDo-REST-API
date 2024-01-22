import json
import re
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import NoResultFound

from todoApp.exceptions.validation_exception import ValidationException
from todoApp.extensions.db import db
from todoApp.models.User import User, serialize_user

users = Blueprint('users', __name__)


def make_token(username):
    payload = {"sub": username, "iat": datetime.utcnow(), "exp": datetime.utcnow() + timedelta(hours=2)}
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")


def decode_token(token):
    payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    return payload["sub"]


@users.post('/signup')
def create_user():
    data = request.get_json()
    first_name, last_name, username, password_plaintext, confirm_password = data.get("first_name"), data.get("last_name"), data.get("username"), data.get("password_plaintext"), data.get("confirm_password")
    try:
        if db.session.scalars(db.select(User).filter_by(username=username)).first():
            raise ValidationException("Username is already taken")
        if password_plaintext and (not confirm_password or password_plaintext != confirm_password):
            raise ValidationException("Passwords must match")
        user_to_add = User(first_name=first_name, last_name=last_name, username=username, password_plaintext=password_plaintext)
        db.session.add(user_to_add)
        db.session.commit()
        added_user = db.session.scalars(db.select(User).filter_by(id=user_to_add.id)).one()
        token = make_token(added_user.username)
        return jsonify({"token": token, "user": serialize_user(added_user)}), 201
    except ValidationException as error:
        return jsonify(f"Error: {error}."), 400


@users.post('/login')
def login_user():
    data = request.authorization
    username, password_plaintext = data.get("username"), data.get("password")
    try:
        if not username or not password_plaintext:
            raise ValidationException("Username and password required")
        found_user = db.session.scalars(db.select(User).filter_by(username=username)).first()
        if found_user is None:
            raise NoResultFound("User not found")
        if found_user.check_password(password_plaintext) is False:
            raise ValidationException("Incorrect password")
        token = make_token(username)
        return jsonify({"token": token}), 200
    except ValidationException as error:
        return jsonify(f"Error: {error}."), 401, {"WWW-Authenticate": "Basic"}
    except NoResultFound as error:
        return jsonify(f"Error: {error}."), 404
