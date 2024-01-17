import json
import re

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import OperationalError, NoResultFound, IntegrityError

from .exceptions.validation_exception import ValidationException
from .extensions.db import db
from .models.Todo import Todo, serialize_todo
from .utils.validation_utils import validate_todo_route_param

todos = Blueprint('todos', __name__)


@todos.post('/todos')
def add_todo():
    # get relevant data from request
    data = request.get_json()
    title, description = data.get('title'), data.get('description')

    try:
        if db.session.scalars(db.select(Todo).filter_by(title=title)).first():
            raise ValidationException('Your todo must have a unique title')

        # create instance of To*do model
        todo_to_add = Todo(title=title, description=description)

        # add new instance to SQLAlchemy session and schedule it for insertion into db
        db.session.add(todo_to_add)

        # commits scheduled changes to db and EXPIRES SESSION OBJECT (it's empty now)
        db.session.commit()

        # actual magic here
        # gets todo_to_add out of the identity map for the previous session and then refreshes it with the current
        # values from the db - so now our data is back and we have an id!
        added_todo = db.session.scalars(db.select(Todo).filter_by(id=todo_to_add.id)).one()
        return jsonify(serialize_todo(added_todo)), 201

    except ValidationException as exception_message:
        error = exception_message
        return jsonify('Error: {}.'.format(error)), 400


@todos.get('/todos')
def get_all_todos():
    found_todos = db.session.scalars(db.select(Todo)).all()
    serialized_todos = [serialize_todo(found_todo) for found_todo in found_todos]
    return jsonify(serialized_todos)


@todos.get('/todos/<todo_id>')
def get_todo(todo_id):
    try:
        validate_todo_route_param(todo_id)
        found_todo = db.session.scalars(db.select(Todo).filter_by(id=todo_id)).one()
        return jsonify(serialize_todo(found_todo))
    except ValidationException as error:
        return jsonify('Error: {}.'.format(error)), 400
    except NoResultFound:
        error = "No result found for todo ID {}".format(todo_id)
        return jsonify('Error: {}.'.format(error)), 404


@todos.delete('/todos/<todo_id>')
def delete_todo(todo_id):
    try:
        validate_todo_route_param(todo_id)
        todo_to_delete = db.session.scalars(db.select(Todo).filter_by(id=todo_id)).one()
        db.session.delete(todo_to_delete)
        db.session.commit()
        return jsonify("Todo successfully deleted.")
    except ValidationException as error:
        return jsonify('Error: {}.'.format(error)), 400
    except NoResultFound:
        error = "Cannot delete todo, no result found for todo ID {}".format(todo_id)
        return jsonify('Error: {}.'.format(error)), 404


@todos.patch('/todos/<todo_id>')
def edit_todo(todo_id):
    try:
        validate_todo_route_param(todo_id)
        todo_to_edit = db.session.scalars(db.select(Todo).filter_by(id=todo_id)).one()
        data = request.get_json()

        # this method of updating assumes that client will either send back the original data unaltered for any
        # attribute they do not want to edit, or they will not send that attribute at all: any attribute that is
        # returned with a null value is intended to delete any existing value for that attribute in the database.
        # if a key is not included in the request, the database for that attribute will not be altered,
        # but if a key is included and its value is null, the value of the attribute will be set to None.

        # Explicit attribute names rather than a loop to ensure data integrity
        if "title" in data:
            if todo_to_edit.title != data.get("title") and db.session.scalars(db.select(Todo).filter_by(title=data.get("title"))).first():
                raise ValidationException('Your todo must have a unique title')
            setattr(todo_to_edit, "title", data.get("title"))
        if "description" in data:
            setattr(todo_to_edit, "description", data.get("description"))
        db.session.commit()
        edited_todo = db.session.scalars(db.select(Todo).filter_by(id=todo_id)).one()
        return jsonify(serialize_todo(edited_todo))
    except ValidationException as error:
        return jsonify('Error: {}.'.format(error)), 400
    except NoResultFound:
        error = "Cannot edit todo, no result found for todo ID {}".format(todo_id)
        return jsonify('Error: {}.'.format(error)), 404

