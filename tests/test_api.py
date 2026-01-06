"""
API 端点测试
"""
from unittest.mock import patch, MagicMock
import pandas as pd


def test_list_functions_whitelist_disabled(client):
    """测试函数列表（白名单禁用）"""
    response = client.get('/api/')
    assert response.status_code == 200

    data = response.get_json()
    assert 'message' in data
    assert 'hint' in data


def test_list_functions_whitelist_enabled(app, client):
    """测试函数列表（白名单启用）"""
    app.config['ENABLE_FUNCTION_WHITELIST'] = True
    app.config['ALLOWED_FUNCTIONS'] = {'stock_zh_a_hist', 'fund_etf_hist_em'}

    response = client.get('/api/')
    assert response.status_code == 200

    data = response.get_json()
    assert 'available_functions' in data
    assert data['count'] == 2


def test_invalid_function_name(client):
    """测试无效函数名"""
    response = client.get('/api/invalid-name!')
    assert response.status_code == 400

    data = response.get_json()
    assert data['error'] is True
    assert data['error_code'] == 'INVALID_PARAMETER'


def test_private_function_blocked(client):
    """测试私有函数被阻止"""
    response = client.get('/api/_private_func')
    assert response.status_code == 400

    data = response.get_json()
    assert data['error'] is True
    assert 'private' in data['message'].lower()


def test_function_not_found(client):
    """测试函数不存在"""
    response = client.get('/api/nonexistent_function_12345')
    assert response.status_code == 404

    data = response.get_json()
    assert data['error'] is True
    assert data['error_code'] == 'FUNCTION_NOT_FOUND'


def test_function_not_allowed(app, client):
    """测试函数不在白名单中"""
    app.config['ENABLE_FUNCTION_WHITELIST'] = True
    app.config['ALLOWED_FUNCTIONS'] = {'stock_zh_a_hist'}

    response = client.get('/api/fund_etf_hist_em')
    assert response.status_code == 403

    data = response.get_json()
    assert data['error'] is True
    assert data['error_code'] == 'FUNCTION_NOT_ALLOWED'


@patch('app.api.views.ak')
def test_successful_api_call(mock_ak, client):
    """测试成功的 API 调用"""
    # 模拟 akshare 函数返回
    mock_df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'value': [100, 200]
    })
    mock_func = MagicMock(return_value=mock_df)
    mock_ak.test_func = mock_func

    # 确保 hasattr 返回 True
    type(mock_ak).test_func = mock_func

    response = client.get('/api/test_func?param1=value1')
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2


@patch('app.api.views.ak')
def test_api_call_with_empty_result(mock_ak, client):
    """测试返回空 DataFrame"""
    mock_df = pd.DataFrame()
    mock_func = MagicMock(return_value=mock_df)
    mock_ak.empty_func = mock_func
    type(mock_ak).empty_func = mock_func

    response = client.get('/api/empty_func')
    assert response.status_code == 200

    data = response.get_json()
    assert data == []


@patch('app.api.views.ak')
def test_api_call_type_error(mock_ak, client):
    """测试参数错误"""
    mock_func = MagicMock(side_effect=TypeError("missing required argument"))
    mock_ak.error_func = mock_func
    type(mock_ak).error_func = mock_func

    response = client.get('/api/error_func')
    assert response.status_code == 400

    data = response.get_json()
    assert data['error'] is True
    assert data['error_code'] == 'INVALID_PARAMETER'


@patch('app.api.views.ak')
def test_api_call_runtime_error(mock_ak, client):
    """测试运行时错误"""
    mock_func = MagicMock(side_effect=RuntimeError("network error"))
    mock_ak.network_func = mock_func
    type(mock_ak).network_func = mock_func

    response = client.get('/api/network_func')
    assert response.status_code == 500

    data = response.get_json()
    assert data['error'] is True
    assert data['error_code'] == 'DATA_FETCH_ERROR'
