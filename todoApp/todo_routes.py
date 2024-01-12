import json

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import OperationalError

from .extensions.db import db
from .models.Todo import Todo, serialize_todo

todos = Blueprint('todos', __name__)


@todos.post('/todos')
def add_todo():
    # get relevant data from request
    data = request.get_json()
    title, description = data.get('title', None), data.get('description', None)

    try:
        # create instance of To*do model
        todo_to_add = Todo(title=title, description=description)

        # add new instance to SQLAlchemy session and schedule it for insertion into db
        db.session.add(todo_to_add)

        # commits scheduled changes to db and EXPIRES SESSION OBJECT
        db.session.commit()

        # actual magic here
        # gets todo_to_add out of the identity map for the previous session and then refreshes it with the current
        # values from the db - so now our data is back and we have an id!
        added_todo = Todo.query.get(todo_to_add.id)
        return jsonify(serialize_todo(added_todo)), 201

    except AssertionError as exception_message:
        error = exception_message
        return jsonify('Error: {}.'.format(error)), 400


@todos.get('/todos')
def get_todos():
    found_todos = Todo.query.all()
    print(found_todos)
    if not found_todos:
        return "", 204
    serialized_todos = [serialize_todo(found_todo) for found_todo in found_todos]
    return jsonify(serialized_todos)
