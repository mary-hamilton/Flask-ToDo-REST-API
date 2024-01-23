from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import validates, Mapped

from ..exceptions.validation_exception import ValidationException
from ..extensions.db import db
from ..utils.serialize_function import serialize_model


class Todo(db.Model):
    id: Mapped[int] = db.mapped_column(primary_key=True)
    title: Mapped[str] = db.mapped_column(db.String(40), unique=True)
    description: Mapped[Optional[str]] = db.mapped_column(db.String(250))
    user_id: Mapped[int] = db.mapped_column(ForeignKey('user.id'))

    def __init__(self, title, user_id, description=None):
        self.title = title
        self.description = description
        self.user_id = user_id

    # <key> parameter is required in validators or they won't work
    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValidationException('Your todo needs a title')
        if not isinstance(title, str):
            raise ValidationException('Your title must be a string')
        if len(title) > 40:
            raise ValidationException('Your todo title must be 40 characters or fewer')
        return title

    @validates('description')
    def validate_description(self, key, description):
        if description:
            if not isinstance(description, str):
                raise ValidationException('Your description must be a string')
            if len(description) > 250:
                raise ValidationException('Your todo description must be 250 characters or fewer')
            return description


def serialize_todo(todo_to_serialize):
    return serialize_model(todo_to_serialize, Todo)


