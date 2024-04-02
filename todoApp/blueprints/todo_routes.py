import json
import re

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import NoResultFound

from todoApp.blueprints.user_routes import require_token
from todoApp.exceptions.validation_exception import ValidationException
from todoApp.extensions.db import db
from todoApp.models.Todo import Todo, serialize_todo, serialize_todo_with_children
from todoApp.utils.cascading_functions import apply_todo_tree, make_todo_checked, make_todo_matcher
from todoApp.utils.validation_utils import validate_todo_route_param

todos = Blueprint('todos', __name__)


@todos.post('/todos')
@require_token
def add_todo(current_user):
    # get relevant data from request
    data = request.get_json()
    title, description, parent_id = data.get('title'), data.get('description'), data.get('parent_id')

    try:
        if parent_id:
            # checking that parent_todo actually exists; throw error if not
            db.session.scalars(db.session.query(Todo).filter_by(user_id=current_user.id, id=parent_id)).one()

        # If am only imposing unique title constraint on top-level parent todos, need to filter this by whether
        # a parent_id has been sent in the request
        if parent_id is None and db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id, title=title)).first():
            raise ValidationException("Your todo title must be unique")

        # create instance of To*do model
        todo_to_add = Todo(title=title, description=description, user_id=current_user.id, parent_id=parent_id)

        # add new instance to SQLAlchemy session and schedule it for insertion into db
        db.session.add(todo_to_add)

        # commits scheduled changes to db and EXPIRES SESSION OBJECT (it's empty now)
        db.session.commit()

        # actual magic here
        # gets todo_to_add out of the identity map for the session and then refreshes it with the current
        # values from the db
        db.session.refresh(todo_to_add)
        return jsonify(serialize_todo(todo_to_add)), 201

    except ValidationException as exception_message:
        error = exception_message
        return jsonify(f"Error: {error}."), 400
    except NoResultFound:
        return jsonify(f"Error: Parent todo does not exist."), 404



@todos.get('/todos')
@require_token
def get_all_todos(current_user):
    # Change so found todos is a list of top-level todos only. Can fetch subtodos from
    # database on click.
    found_todos = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id
                                                               , parent_id=None
                                                               )).all()
    serialized_todos = [serialize_todo(found_todo) for found_todo in found_todos]
    return jsonify(serialized_todos)


@todos.get('/todos/<todo_id>')
@require_token
def get_todo(current_user, todo_id):
    try:
        validate_todo_route_param(todo_id)
        found_todo = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id, id=todo_id)).one()
        return jsonify(serialize_todo_with_children(found_todo))
    except ValidationException as error:
        return jsonify(f"Error: {error}."), 400
    except NoResultFound:
        error = f"No result found for todo ID {todo_id}"
        return jsonify(f"Error: {error}."), 404


@todos.delete('/todos/<todo_id>')
@require_token
def delete_todo(current_user, todo_id):
    try:
        validate_todo_route_param(todo_id)
        todo_to_delete = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id, id=todo_id)).one()
        db.session.delete(todo_to_delete)
        db.session.commit()
        return jsonify("Todo successfully deleted.")
    except ValidationException as error:
        return jsonify(f"Error: {error}."), 400
    except NoResultFound:
        error = f"Cannot delete todo, no result found for todo ID {todo_id}"
        return jsonify(f"Error: {error}."), 404


@todos.patch('/todos/<todo_id>')
@require_token
def edit_todo(current_user, todo_id):
    try:
        validate_todo_route_param(todo_id)
        todo_to_edit = db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id, id=todo_id)).one()
        data = request.get_json()
        # Hacky, change this
        if "id" in data and data.get("id") != todo_id:
            raise ValidationException("Todo IDs cannot be edited")

        # this method of updating assumes that client will either send back the original data unaltered for any
        # attribute they do not want to edit, or they will not send that attribute at all: any attribute that is
        # returned with a null value is intended to delete any existing value for that attribute in the database.
        # if a key is not included in the request, the database for that attribute will not be altered,
        # but if a key is included and its value is null, the value of the attribute will be set to None.

        # Explicit attribute names rather than a loop to ensure data integrity
        if "title" in data:
            if todo_to_edit.title != data.get("title") and db.session.scalars(db.select(Todo).filter_by(user_id=current_user.id, title=data.get("title"))).first():
                raise ValidationException('Your todo must have a unique title')
            setattr(todo_to_edit, "title", data.get("title"))
        if "description" in data:
            setattr(todo_to_edit, "description", data.get("description"))
        db.session.commit()
        edited_todo = db.session.get(Todo, todo_id)
        return jsonify(serialize_todo(edited_todo))
    except ValidationException as error:
        return jsonify(f"Error: {error}."), 400
    except NoResultFound:
        error = f"No result found for todo ID {todo_id}"
        return jsonify(f"Error: {error}."), 404


@todos.patch('/todos/<todo_id>/toggle_parent')
@require_token
def toggle_parent(current_user, todo_id):
    data = request.get_json()
    parent_id_to_add = data.get("parent_id")
    try:
        validate_todo_route_param(todo_id)
        child_todo = db.session.scalars(db.session.query(Todo).filter_by(user_id=current_user.id, id=todo_id)).one()

        if parent_id_to_add is not None:
            if parent_id_to_add == int(todo_id):
                raise ValidationException('Todo cannot be its own parent')
            # checking that parent_todo actually exists; throw error if not
            parent_todo = db.session.scalars(db.session.query(Todo).filter_by(user_id=current_user.id, id=parent_id_to_add)).one()

            # check that we're not trying to create a circular relationship anywhere in the tree
            todo_matcher = make_todo_matcher(parent_todo)
            if apply_todo_tree(child_todo, todo_matcher, return_result=True):
                raise ValidationException('Cannot create circular parent-child relationship')

        child_todo.parent_id = parent_id_to_add
        db.session.commit()
        updated_child_todo = db.session.get(Todo, todo_id)
        return jsonify(serialize_todo(updated_child_todo))
    except ValidationException as error:
        return jsonify(f"Error: {error}."), 400
    except NoResultFound:
        return jsonify(f"Error: Parent or child todo does not exist."), 404

@todos.patch('/todos/<todo_id>/check')
@require_token
def check_todo(current_user, todo_id):
    data = request.get_json()
    checked = data.get("checked")
    try:
        validate_todo_route_param(todo_id)
        todo_to_update = db.session.scalars(db.session.query(Todo).filter_by(user_id=current_user.id, id=todo_id)).one()

        # Unchecking a to*do only affects that to*do
        if checked is False:
            todo_to_update.checked = checked
        # Checking a to*do also checks all children
        if checked is True:
            apply_todo_tree(todo_to_update, make_todo_checked)
        # Behavior for todos with parents
        if todo_to_update.parent_id is not None:
            todo_parent = db.session.scalars(db.session.query(Todo).filter_by(user_id=current_user.id, id=todo_to_update.parent_id)).one()
            # Unchecking a sub to*do also unchecks its parent
            if checked is False:
                todo_parent.checked = False
            # If there are no remaining unchecked children, check the parent
            # if checked is True:
            #     unchecked_sibling_flag = False
            #     for child in todo_parent.children:
            #         if child.checked is False:
            #             unchecked_sibling_flag = True
            #             break
            #     if not unchecked_sibling_flag:
            #         todo_parent.checked = True
        db.session.commit()
        db.session.refresh(todo_to_update)
        return jsonify(serialize_todo(todo_to_update))
    except ValidationException as error:
        return jsonify(f"Error: {error}."), 400
    except NoResultFound:
        return jsonify(f"Error: Todo does not exist."), 404

