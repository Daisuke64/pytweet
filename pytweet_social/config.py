"""Provide Config of Flask"""
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class DevelopmentConfig:

    # Flask
    DEBUG = True

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
        'user': os.environ.get("MYSQL_USER") or "test",
        'password': os.environ.get("MYSQL_PASSWORD") or "test",
        'host': os.environ.get("DB_HOST") or "docker_mysql2",
        'db_name': os.environ.get("MYSQL_DATABASE") or "pytweet_follow",
    })
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SECRET_KEY = os.urandom(24)

    # Upload the image
    IMG_UPLOAD_URL = 'https://api.imgur.com/3/image'
    IMGUR_CLI_ID = os.environ.get("IMGUR_CLI_ID")


Config = DevelopmentConfig
