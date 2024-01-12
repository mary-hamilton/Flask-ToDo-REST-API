import pytest
from todoApp.models.Todo import *


def test_serialize_function_without_ID():
    test_todo = Todo(title="Test Title", description="Test Description")
    serialized_test_todo = serialize_todo(test_todo)
    assert serialized_test_todo == {"title": "Test Title", "description": "Test Description"}


def test_serialize_function_with_ID():
    test_todo = Todo(title="Test Title", description="Test Description")
    test_todo.id = 123
    serialized_test_todo = serialize_todo(test_todo)
    assert serialized_test_todo == {"title": "Test Title", "description": "Test Description", "id": 123}
