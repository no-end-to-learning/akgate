from io import BytesIO

import numpy as np
import pandas as pd
from flask import Blueprint, request, send_file
from pre_request import pre, Rule

from app.z import services

api = Blueprint('z', __name__)

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
    'init_volume': Rule(type=int, required=False),
    'base_price': Rule(type=float, required=True),
    'price_decimals': Rule(type=int, required=False),
    'grid_count': Rule(type=int, required=True),
    'grid_step': Rule(type=float, required=True)
})
def calculate():
    kline = services.get_kline(request.args['code'])

    return services.calculate(
        kline,
        int(request.args.get('init_volume', DEFAULT_VOLUME_INIT)),
        float(request.args.get('base_price')),
        float(request.args.get('price_decimals', DEFAULT_PRICE_DECIMAL)),
        int(request.args.get('grid_count')),
        float(request.args.get('grid_step'))
    )
    return services.code_rules


@api.route('/stat', methods=['GET'])
@pre.catch({
    'code': Rule(type=str, required=True),
    'init_volume': Rule(type=int, required=False),
    'price_decimals': Rule(type=int, required=False),
})
def stat():
    code = request.args.get('code')
    init_volume = int(request.args.get('init_volume', DEFAULT_VOLUME_INIT))
    price_decimals = int(request.args.get('price_decimals', DEFAULT_PRICE_DECIMAL))

    result = []
    kline_df = services.get_kline(code)[-211:]
    avg_price = kline_df.mean().get('close')
    kline = kline_df.to_dict('records')
    for base_price_rate in np.arange(DEFAULT_BASE_PRICE_RATE_MIN, DEFAULT_BASE_PRICE_RATE_MAX + DEFAULT_BASE_PRICE_RATE_INTERVAL, DEFAULT_BASE_PRICE_RATE_INTERVAL):
        for grid_count in range(DEFAULT_GRID_COUNT_MIN, DEFAULT_GRID_COUNT_MAX + 1):
            for grid_step in np.arange(DEFAULT_GRID_STEP_MIN, DEFAULT_GRID_STEP_MAX + DEFAULT_GRID_STEP_INTERVAL, DEFAULT_GRID_STEP_INTERVAL):
                base_price = round(avg_price * base_price_rate, price_decimals)
                item = services.calculate(kline, init_volume, base_price, price_decimals, grid_count, grid_step)
                result.append({
                    '开始日期': item['start_date'],
                    '结束日期': item['end_date'],
                    '初始资产': round(item['init_volume'],0),
                    '单笔金额': round(item['init_volume'] / item['grid_count'], 0),
                    '价格中枢': item['base_price'],
                    '网格数量': item['grid_count'],
                    '网格间隔': item['grid_step'],
                    '买卖次数': len(item['orders']),
                    '结束时未平仓数量': round(item['position_amount'], 0),
                    '结束时未平仓金额': round(item['position_volume'], 0),
                    '结束时可用金额': round(item['remain_volume'], 0),
                    '网格收益': round(item['profit_grid'], 0),
                    '网格收益率': round(item['profit_grid'] / item['init_volume'], 4), 
                    '总收益': round(item['profit_total'], 0),
                    '总收益率': round(item['profit_total'] / item['init_volume'], 4)
                })

    result_df = pd.DataFrame(result)
    result_buffer = BytesIO()
    result_df.to_excel(result_buffer)
    result_buffer.seek(0)

    return send_file(
        result_buffer,
        as_attachment=True,
        attachment_filename=f'grid_trading_backtest_{code}.xlsx',
        mimetype='application/vnd.ms-excel'
    )
