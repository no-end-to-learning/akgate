import json

import akshare as ak

with open("./assets/code_rules.json", "r") as f:
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
