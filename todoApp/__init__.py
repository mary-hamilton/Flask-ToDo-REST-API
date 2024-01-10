import os
from flask import Flask
from dotenv import load_dotenv
from .extensions.db import db

load_dotenv()


def create_app(test_config=None):

    db_host = os.environ.get("DB_HOST")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")

    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/flask_todo_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()

    @app.get('/')
    def hello_world():
        return "Hello World!"

    return app
