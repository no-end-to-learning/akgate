from flask import Flask
from .encoder import CustomJSONEncoder


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.settings')
    app.json_encoder = CustomJSONEncoder
    register_api(app)
    return app


def register_api(flask_app):
    from app.api import api
    flask_app.register_blueprint(api, url_prefix='/api')
