from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.settings')
    register_grid(app)
    return app


def register_grid(flask_app):
    from app.grid import api
    flask_app.register_blueprint(api, url_prefix='/grid')
