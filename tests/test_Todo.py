import pytest
from todoApp.models.Todo import *
from tests.fixtures import app


def test_serialize_function_without_ID(app):
    test_todo = Todo(title="Test Title", description="Test Description")
    serialized_test_todo = serialize_todo(test_todo)
    assert serialized_test_todo == {"title": "Test Title", "description": "Test Description"}


def test_serialize_function_with_ID(app):
    test_todo = Todo(title="Test Title", description="Test Description")
    test_todo.id = 123
    serialized_test_todo = serialize_todo(test_todo)
    assert serialized_test_todo == {"title": "Test Title", "description": "Test Description", "id": 123}
