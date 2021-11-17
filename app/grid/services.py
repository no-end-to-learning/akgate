import json
import logging
import os

import akshare as ak

logger = logging.getLogger("grid")

code_rules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './assets/code_rules.json'))
with open(code_rules_path, 'r') as f:
    code_rules = json.loads(f.read())


def get_kline(code):
    code_info = get_code_info(code)
    symbol = (code_info['exchange'] + code_info['code']).lower()

    # 可转债
    if code_info['type'] == 'CB':
        return ak.bond_zh_hs_daily(symbol=symbol)

    # ETF
    if code_info['type'] == 'ETF':
        return ak.fund_etf_hist_sina(symbol=symbol)

    raise Exception("Unknown code type")


def get_code_info(code):
    if not code.isnumeric():
        raise Exception("code is not a number")

    for k, v in code_rules.items():
        if not code.startswith(k):
            continue

        return {
            'code': code,
            'type': v['type'],
            'exchange': v['exchange']
        }

    raise Exception("Unknown code")


def get_grid_band(grid_count, grid_step):
    grid_band = []
    for i in range(grid_count):
        grid_band.append((i - round(grid_count / 2, 0)) * grid_step + 1)
    return grid_band


def get_grid_amount(init_volume, grid_count, current_price, round_n):
    return round(init_volume / grid_count / current_price, round_n)


def calculate(klines, init_volume, base_price, price_decimals, grid_count, grid_step):
    shift = 0
    profit_grid = 0
    remain_volume = init_volume
    orders = []
    buy_stack = []

    grid_band = get_grid_band(grid_count, grid_step)
    buy_price_band = [round(base_price * rate, price_decimals) for rate in reversed(grid_band)]
    sell_price_band = [round(base_price * (rate + grid_step), price_decimals) for rate in reversed(grid_band)]

    logger.debug('%s %s %s' % (grid_band, buy_price_band, sell_price_band))

    for row in klines:
        # 开盘价 买入
        while shift < grid_count and buy_price_band[shift] >= row.get('open'):
            logger.debug('%s 开盘价 买入 当前价格 %.3f 网格价格 %.3f %s' % (
                row.get('date'), row.get('open'), buy_price_band[shift], shift + 1))
            buy_order = {
                'date': row.get('date'),
                'type': 'buy',
                'price': row.get('open'),
                'amount': round(init_volume / grid_count / row.get('open'), -2)
            }
            orders.append(buy_order)
            buy_stack.append(buy_order)
            remain_volume -= buy_order['price'] * buy_order['amount']
            shift += 1

        # 开盘价 卖出
        while shift > 0 and sell_price_band[shift - 1] <= row.get('open'):
            logger.debug('%s 开盘价 卖出 当前价格 %.3f 网格价格 %.3f %s' % (
                row.get('date'), row.get('open'), sell_price_band[shift - 1], shift - 1))
            buy_order = buy_stack.pop()
            sell_order = {
                'date': row.get('date'),
                'type': 'sell',
                'price': row.get('open'),
                'amount': buy_order['amount']
            }
            orders.append(sell_order)
            remain_volume += sell_order['price'] * sell_order['amount']
            profit_grid += (sell_order['price'] - buy_order['price']) * sell_order['amount']
            shift -= 1

        # 最低价 买入
        while shift < grid_count and buy_price_band[shift] >= row.get('low'):
            logger.debug('%s 下跌   买入 当前价格 %.3f 网格价格 %.3f %s' % (
                row.get('date'), row.get('low'), buy_price_band[shift], shift + 1))
            buy_order = {
                'date': row.get('date'),
                'type': 'buy',
                'price': buy_price_band[shift],
                'amount': round(init_volume / grid_count / buy_price_band[shift], -2)
            }
            orders.append(buy_order)
            buy_stack.append(buy_order)
            remain_volume -= buy_order['price'] * buy_order['amount']
            shift += 1

        # 最高价 卖出
        while shift > 0 and sell_price_band[shift - 1] <= row.get('high'):
            logger.debug('%s 上涨   卖出 当前价格 %.3f 网格价格 %.3f %s' % (
                row.get('date'), row.get('high'), sell_price_band[shift - 1], shift - 1))
            buy_order = buy_stack.pop()
            sell_order = {
                'date': row.get('date'),
                'type': 'sell',
                'price': sell_price_band[shift - 1],
                'amount': buy_order['amount']
            }
            orders.append(sell_order)
            remain_volume += sell_order['price'] * sell_order['amount']
            profit_grid += (sell_order['price'] - buy_order['price']) * sell_order['amount']
            shift -= 1

        # 收盘价 买入
        while shift < grid_count and buy_price_band[shift] >= row.get('close'):
            logger.debug('%s 下跌   买入 当前价格 %.3f 网格价格 %.3f %s' % (
                row.get('date'), row.get('close'), buy_price_band[shift], shift + 1))
            buy_order = {
                'date': row.get('date'),
                'type': 'buy',
                'price': buy_price_band[shift],
                'amount': round(init_volume / grid_count / buy_price_band[shift], -2)
            }
            orders.append(buy_order)
            buy_stack.append(buy_order)
            remain_volume -= buy_order['price'] * buy_order['amount']
            shift += 1

    start_date = klines[0].get('date')
    end_date = klines[-1].get('date')

    position_amount = sum(order['amount'] for order in buy_stack)
    position_volume = position_amount * klines[-1].get('close')
    profit_total = position_volume + remain_volume - init_volume
    profit_postion = profit_total - profit_grid

    return {
        'start_date': start_date,
        'end_date': end_date,
        'init_volume': init_volume,
        'base_price': base_price,
        'grid_count': grid_count,
        'grid_step': grid_step,
        'position_amount': position_amount,
        'position_volume': position_volume,
        'remain_volume': remain_volume,
        'profit_grid': profit_grid,
        'profit_postion': profit_postion,
        'profit_total': profit_total,
        'buy_stack': buy_stack,
        'orders': orders
    }
