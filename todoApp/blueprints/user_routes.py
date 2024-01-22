import json
import re

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import NoResultFound

from todoApp.exceptions.validation_exception import ValidationException
from todoApp.extensions.db import db
from todoApp.models.User import User, serialize_user

users = Blueprint('users', __name__)


@users.post('/signup')
def create_user():
    data = request.get_json()
    first_name, last_name, username, password_plaintext, confirm_password = data.get("first_name"), data.get("last_name"), data.get("username"), data.get("password_plaintext"), data.get("confirm_password")
    try:
        if password_plaintext:
            if not confirm_password or password_plaintext != confirm_password:
                raise ValidationException("Passwords must match")
        if db.session.scalars(db.select(User).filter_by(username=username)).first():
            raise ValidationException("Username is already taken")
        user_to_add = User(first_name=first_name, last_name=last_name, username=username, password_plaintext=password_plaintext)
        db.session.add(user_to_add)
        db.session.commit()
        added_user = db.session.scalars(db.select(User).filter_by(id=user_to_add.id)).one()
        return jsonify(serialize_user(added_user)), 201
    except ValidationException as error:
        return jsonify(f"Error: {error}."), 400

