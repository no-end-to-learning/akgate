"""
JSON 编码器测试
"""
from datetime import date, datetime
import pandas as pd
import math


def test_json_date_encoding(app, client):
    """测试日期编码"""
    from app.encoder import CustomJSONProvider

    provider = CustomJSONProvider(app)

    # 测试 date 对象
    result = provider.dumps({'date': date(2024, 1, 15)})
    assert '2024-01-15' in result


def test_json_datetime_encoding(app, client):
    """测试时间戳编码"""
    from app.encoder import CustomJSONProvider

    provider = CustomJSONProvider(app)

    # 测试 datetime 对象 - 转换为毫秒时间戳
    dt = datetime(2024, 1, 15, 12, 30, 45)
    result = provider.dumps({'datetime': dt})
    # 验证是数字时间戳
    assert str(int(dt.timestamp() * 1000)) in result


def test_json_nan_encoding(app, client):
    """测试 NaN 值编码"""
    from app.encoder import CustomJSONProvider

    provider = CustomJSONProvider(app)

    # 测试 NaN 值 - 应转换为 null
    result = provider.dumps({'value': float('nan')})
    assert 'null' in result


def test_json_chinese_encoding(app, client):
    """测试中文编码"""
    from app.encoder import CustomJSONProvider

    provider = CustomJSONProvider(app)

    # 测试中文字符 - 不应该被转义
    result = provider.dumps({'name': '中国股票'})
    assert '中国股票' in result
    assert '\\u' not in result
