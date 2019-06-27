# Initialize the flask app and have the entity of the flask app object

from flask import Flask
from pytweet_social.database import init_db
from pytweet_social.config import Config
import os
import pytweet_social.models


def create_app():
    # built instance
    _app = Flask(__name__)
    # Process of Flask's config reading config file
    _app.config.from_object(Config)

    # set up DB
    _app.secret_key = os.urandom(24)
    init_db(_app)

    return _app


app = create_app()
