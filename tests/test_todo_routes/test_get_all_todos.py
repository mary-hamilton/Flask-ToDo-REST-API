import json

import pytest

from tests.conftest import *


def test_returns_empty_if_no_todos_exist(authenticated_client):
    response = authenticated_client.get('/todos')
    assert response.status_code == 200
    assert response.json == []


def test_returns_single_todo(authenticated_client, create_todo):
    create_todo()
    response = authenticated_client.get('/todos')
    response_data = response.json
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response_data[0].get('title') == 'Test Title'
    assert response_data[0].get('description') == 'Test Description'
    assert response_data[0].get('id') == 1


def test_returns_list_of_multiple_todos(authenticated_client, multiple_sample_todos):
    response = authenticated_client.get("/todos")
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

