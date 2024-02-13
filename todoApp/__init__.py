from flask import Flask

from .blueprints.user_routes import users
from .extensions.db import db
from .models.Todo import Todo, serialize_todo
from todoApp.blueprints.todo_routes import todos
from .config import *


# Do not try and initialise with a default config and then overwrite it elsewhere, IT DOES NOT WORK!
# "The issue might be related to the fact that configuration settings, once set in the create_app function,
# are essentially fixed for the lifetime of the Flask application object. When you call create_app in your
# test file and try to override the configuration, you might be encountering limitations in how Flask handles
# these configurations."
def create_app(config_class=DevelopmentConfig):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(todos)


    with app.app_context():
        # development only
        db.drop_all()
        db.create_all()

    return app


todooo = Todo(title='Todo', description='Blah', user_id=2)

print(todooo.children)
print(todooo.children is None)
