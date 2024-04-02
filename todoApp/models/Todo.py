from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import validates, Mapped

from ..exceptions.validation_exception import ValidationException
from ..extensions.db import db
from ..utils.serialize_function import serialize_model


class Todo(db.Model):
    id: Mapped[int] = db.mapped_column(primary_key=True)
    title: Mapped[str] = db.mapped_column(db.String(40))
    description: Mapped[Optional[str]] = db.mapped_column(db.String(250))
    checked: Mapped[bool] = db.mapped_column(db.Boolean)
    user_id: Mapped[int] = db.mapped_column(ForeignKey('user.id'))
    user: Mapped["User"] = db.relationship(back_populates="todos")
    parent_id: Mapped[Optional[int]] = db.mapped_column(ForeignKey('todo.id'))
    children: Mapped[List["Todo"]] = db.relationship("Todo", cascade="all, delete")

    def __init__(self, title, user_id, parent_id=None, description=None):
        self.title = title
        self.description = description
        self.user_id = user_id
        self.parent_id = parent_id
        self.checked = False


    # Equality method for testing purposes
    def __eq__(self, other):
        # Fix this
        self_public_values = {}
        other_public_values = {}
        for key, value in self.__dict__.items():
            if (not key.startswith("_")):
                self_public_values[key] = value
        for key, value in other.__dict__.items():
            if (not key.startswith("_")):
                other_public_values[key] = value
        return self_public_values == other_public_values


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


def serialize_todo_with_children(todo_to_serialize):
    serialized_todo = {**serialize_model(todo_to_serialize, Todo)}
    serialized_todo['children'] = todo_to_serialize.children
    return {**serialize_model(todo_to_serialize, Todo)}


def serialize_todo(todo_to_serialize):
    # TODO change this so I can get some sort of indication of how many
    #  children and (maybe) their checked status
    serialized_todo = {**serialize_model(todo_to_serialize, Todo)}
    return serialized_todo

