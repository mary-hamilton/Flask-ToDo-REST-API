import pytest
from todoApp.__init__ import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(dict(TESTING=True))
    with app.app_context():
        yield app


@pytest.fixture()
def client(app):
    return app.test_client()
