from sqlalchemy.orm import validates
from ..extensions.db import db


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(40), nullable=False, unique=True)
    description = db.Column(db.String(250), nullable=True)

    def __init__(self, title, description):
        self.title = title
        self.description = description

    # <key> parameter is required in validators or they won't work
    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise AssertionError('Your todo needs a title')
        if len(title) > 40:
            raise AssertionError('Your todo title must be 40 characters or fewer')
        if Todo.query.filter_by(title=title).first():
            raise AssertionError('Your todo must have a unique title')
        return title

    @validates('description')
    def validate_description(self, key, description):
        if description:
            if len(description) > 250:
                raise AssertionError('Your todo description must be 250 characters or fewer')
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


