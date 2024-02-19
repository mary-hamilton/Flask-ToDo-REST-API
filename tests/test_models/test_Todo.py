import pytest
from todoApp.models.Todo import *
from tests.conftest import *
from todoApp.utils.serialize_function import serialize_model


def test_successful_todo(app):
    todo = Todo(title="Test Title", user_id=1, description="Test Description")
    assert todo is not None
    assert todo.title == "Test Title"
    assert todo.description == "Test Description"


def test_successful_todo_no_description(app):
    todo = Todo(title="Test Title", user_id=1)
    assert todo is not None
    assert todo.title == "Test Title"
    assert todo.description is None


def test_incorrect_data_type(app):
    with pytest.raises(ValidationException) as exception_info:
        test_todo = Todo(title="Test Title", description=1234, user_id=1)
        assert test_todo is None
        assert "Your description must be a string" in exception_info.value


def test_no_title(app):
    with pytest.raises(ValidationException) as exception_info:
        test_todo = Todo(title=None, description="Test Description", user_id=1)
        assert test_todo is None
        assert "Your todo must have a title" in exception_info.value


def test_incorrect_title_length(app):
    with pytest.raises(ValidationException) as exception_info:
        test_todo = Todo(title="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARGH", description="Test Description", user_id=1)
        assert test_todo is None
        assert "Your todo title must be 40 characters or fewer" in exception_info.value


def test_incorrect_description_length(app):
    with pytest.raises(ValidationException) as exception_info:
        test_todo = Todo(title="Test Title", description="Domestic cats, with their graceful charms and independent "
                                                         "natures, enchant as beloved companions. Playful antics and "
                                                         "soothing purrs make them universal darlings, seamlessly "
                                                         "integrating into diverse households and leaving lasting "
                                                         "impressions on hearts.", user_id=1)
        assert test_todo is None
        assert "Your todo description must be 250 characters or fewer" in exception_info.value


def test_serialize_function_without_ID(app):
    test_todo = Todo(title="Test Title", description="Test Description", user_id=1)
    serialized_test_todo = serialize_todo(test_todo)
    assert serialized_test_todo == {"title": "Test Title", "description": "Test Description", "user_id": 1, "checked": False}


def test_serialize_function_with_ID(app):
    test_todo = Todo(title="Test Title", description="Test Description", user_id=1)
    test_todo.id = 123
    serialized_test_todo = serialize_todo(test_todo)
    assert serialized_test_todo == {"title": "Test Title", "description": "Test Description", "id": 123, "user_id": 1, "checked": False}


def test_serialize_function_WITH_CHILDREN_parent_todo(app):

    # Need to manually add an id for the parent and manually add the child to the
    # parent's children list because the database isn't doing it for us
    parent_todo = Todo(title="Parent Todo", user_id=1)
    parent_todo.id = 123
    child_todo = Todo(title="Child Todo", user_id=1, parent_id=parent_todo.id)
    parent_todo.children.append(child_todo)

    expected_data_parent = {"title": "Parent Todo", "user_id": 1, "id": 123, "checked": False}
    expected_data_child = {"title": "Child Todo", "user_id": 1, "parent_id": parent_todo.id, "checked": False}

    serialized_todo_with_children = serialize_todo_with_children(parent_todo)

    assert serialized_todo_with_children == {**expected_data_parent, "children": [expected_data_child]}


