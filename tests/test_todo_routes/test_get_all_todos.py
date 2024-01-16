import pytest

from tests.fixtures import *


def test_returns_empty_if_no_todos_exist(client):
    response = client.get('/todos')
    assert response.status_code == 200
    assert response.json == []


def test_returns_single_todo(client, create_todo):
    create_todo()
    response = client.get('/todos')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0] == {"title": 'Test Title', "description": 'Test Description', "id": 1}


def test_returns_list_of_multiple_todos(client, multiple_sample_todos):
    response = client.get("/todos")
    response_data = response.json
    assert response.status_code == 200
    assert len(response_data) == 3
    assert response_data[0].get('title') == 'Test Title'
    assert response_data[0].get('description') == 'Test Description'
    assert response_data[0].get('id') == 1
    assert response_data[1].get('title') == 'Test Title 2'
    assert response_data[1].get('description') == 'Test Description'
    assert response_data[1].get('id') == 2
    assert response_data[2].get('title') == 'Test Title 3'
    assert response_data[2].get('description') is None
    assert response_data[2].get('id') == 3
