from flask import Blueprint

from app.grid import services

api = Blueprint('grid', __name__)


@api.route("/hello", methods=['GET'])
def hello():
    return services.code_rules
