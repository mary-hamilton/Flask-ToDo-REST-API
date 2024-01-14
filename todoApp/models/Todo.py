from typing import Optional

from sqlalchemy.orm import validates, Mapped

from ..exceptions.validation_exception import ValidationException
from ..extensions.db import db


class Todo(db.Model):
    id: Mapped[int] = db.mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = db.mapped_column(db.String(40), unique=True)
    description: Mapped[Optional[str]] = db.mapped_column(db.String(250))

    def __init__(self, title, description=None):
        self.title = title
        self.description = description

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


def serialize_todo(obj):
    # Should handle with and without ID
    if isinstance(obj, Todo):
        data = {}
        for key, value in obj.__dict__.items():
            # handles not returning null values
            # might change this, not sure of best format yet
            if not key.startswith('_') and value is not None:
                data[key] = value
        return data
    raise TypeError(f"Object of type '{type(obj).__name__}' is not JSON serializable")


