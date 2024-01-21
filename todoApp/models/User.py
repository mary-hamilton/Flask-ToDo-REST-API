import re
from typing import Optional
from sqlalchemy.orm import validates, Mapped
from werkzeug.security import generate_password_hash, check_password_hash

from todoApp.exceptions.validation_exception import ValidationException
from todoApp.extensions.db import db
from todoApp.utils.serialize_function import serialize_model
from todoApp.utils.validation_utils import *


class User(db.Model):
    id: Mapped[int] = db.mapped_column(db.Integer, primary_key=True)
    first_name: Mapped[str] = db.mapped_column(db.String(50))
    last_name: Mapped[str] = db.mapped_column(db.String(50))
    username: Mapped[str] = db.mapped_column(db.String(50), unique=True)
    _password: Mapped[str] = db.mapped_column(db.String(128))

    def __init__(self, first_name, last_name, username, password_plaintext):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.set_password(password_plaintext)

    def set_password(self, password_plaintext):
        validate_presence("password", password_plaintext)
        validate_data_type("password", password_plaintext, str)
        validate_length("password", password_plaintext, 50)
        check_valid_password_string(password_plaintext)
        self._password = generate_password_hash(password_plaintext, method='pbkdf2')

    def check_password(self, password_plaintext):
        return check_password_hash(self._password, password_plaintext)

    @validates("first_name", "last_name", "username")
    def validate_all(self, key, value):
        validate_presence(key, value)
        validate_data_type(key, value, str)
        max_length = 50
        validate_length(key, value, max_length)
        return value


def serialize_user(user_to_serialize):
    return serialize_model(user_to_serialize, User)


