from io import BytesIO

import numpy as np
import pandas as pd
from flask import Blueprint, request, send_file
from pre_request import pre, Rule

from app.grid import services

api = Blueprint('grid', __name__)

# 网格数量 范围
DEFAULT_GRID_COUNT_MIN = 5
DEFAULT_GRID_COUNT_MAX = 20

# 网格价差 范围
DEFAULT_GRID_STEP_MIN = 0.01
DEFAULT_GRID_STEP_MAX = 0.10
DEFAULT_GRID_STEP_INTERVAL = 0.01

# 价格小数位
DEFAULT_PRICE_DECIMAL = 3

# 基准价格 范围
DEFAULT_BASE_PRICE_RATE_MIN = 0.85
DEFAULT_BASE_PRICE_RATE_MAX = 1.15
DEFAULT_BASE_PRICE_RATE_INTERVAL = 0.005

# 初始资产
DEFAULT_VOLUME_INIT = 1000000


@api.route("/calculate", methods=['GET'])
@pre.catch({
    'code': Rule(type=str, required=True),
    'init_volume': Rule(type=int, required=True),
    'base_price': Rule(type=float, required=True),
    'price_decimals': Rule(type=int, required=False),
    'grid_count': Rule(type=int, required=True),
    'grid_step': Rule(type=float, required=True)
})
def calculate():
    kline = services.get_kline(request.args['code'])

    return services.calculate(
        kline,
        int(request.args.get('init_volume')),
        float(request.args.get('base_price')),
        float(request.args.get('price_decimals', DEFAULT_PRICE_DECIMAL)),
        int(request.args.get('grid_count')),
        float(request.args.get('grid_step'))
    )
    return services.code_rules


@api.route('/stat', methods=['GET'])
@pre.catch({
    'code': Rule(type=str, required=True)
})
def stat():
    result = []
    kline = services.get_kline(request.args['code'])
    avg_price = kline.mean().get('close')
    for base_price_rate in np.arange(DEFAULT_BASE_PRICE_RATE_MIN,
                                     DEFAULT_BASE_PRICE_RATE_MAX + DEFAULT_BASE_PRICE_RATE_INTERVAL,
                                     DEFAULT_BASE_PRICE_RATE_INTERVAL):
        for grid_count in range(DEFAULT_GRID_COUNT_MIN, DEFAULT_GRID_COUNT_MAX + 1):
            for grid_step in np.arange(DEFAULT_GRID_STEP_MIN, DEFAULT_GRID_STEP_MAX + DEFAULT_GRID_STEP_INTERVAL,
                                       DEFAULT_GRID_STEP_INTERVAL):
                base_price = round(avg_price * base_price_rate, DEFAULT_PRICE_DECIMAL)
                item = services.calculate(kline, DEFAULT_VOLUME_INIT, base_price, DEFAULT_PRICE_DECIMAL, grid_count,
                                          grid_step)
                result.append({
                    'start_date': item['start_date'],
                    'end_date': item['end_date'],
                    'base_price': item['base_price'],
                    'grid_count': item['grid_count'],
                    'grid_step': item['grid_step'],
                    'profit_grid': item['profit_grid'],
                    'profit_total': item['profit_total']
                })
            break
        break

    result_df = pd.DataFrame(result)
    result_buffer = BytesIO()
    result_df.to_excel(result_buffer)
    result_buffer.seek(0)
    return send_file(result_buffer, as_attachment=True, attachment_filename='a_file.xlsx',
                     mimetype='application/vnd.ms-excel')
