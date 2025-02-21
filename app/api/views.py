import logging

import akshare as ak
from flask import Blueprint, jsonify, request

logger = logging.getLogger("api")

api = Blueprint('api', __name__)


@api.route("/<func_name>", methods=['GET'])
def magic_func(func_name):
    func = getattr(ak, func_name)
    df = func(**request.args)
    records = df.to_dict('records')
    return jsonify(records)
