import pytest
from todoApp.__init__ import create_app
from todoApp.config import *
from todoApp.extensions.db import db


@pytest.fixture()
def app():
    test_app = create_app(TestConfig)
    with test_app.app_context():
        yield test_app


@pytest.fixture()
def client(app):
    return app.test_client()
