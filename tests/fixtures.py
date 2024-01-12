import pytest
from todoApp.__init__ import create_app
from todoApp.config import *

@pytest.fixture()
def app():
    test_app = create_app(TestConfig)
    print(f"Using database URI: {test_app.config['SQLALCHEMY_DATABASE_URI']}")
    with test_app.app_context():
        yield test_app


@pytest.fixture()
def client(app):
    return app.test_client()
