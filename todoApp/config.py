import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    TESTING = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_URI')


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_URI')
    TESTING = True
