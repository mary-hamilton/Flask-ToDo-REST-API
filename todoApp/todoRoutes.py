from flask import Blueprint, jsonify, request
from .extensions.db import db
from .models.Todo import Todo, serialize_todo

todos = Blueprint('todos', __name__)


@todos.post('/todos')
def addTodo():
    data = request.get_json()
    title = data['title']
    description = data['description']
    todo_to_add = Todo(title=title, description=description)
    db.session.add(todo_to_add)
    db.session.commit()
    return jsonify(serialize_todo(todo_to_add))

