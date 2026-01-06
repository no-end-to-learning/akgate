"""
健康检查端点测试
"""


def test_health_check(client):
    """测试基本健康检查"""
    response = client.get('/health')
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'akgate'


def test_health_detail(client):
    """测试详细健康检查"""
    response = client.get('/health/detail')
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] in ('healthy', 'degraded')
    assert data['service'] == 'akgate'
    assert 'dependencies' in data
    assert 'akshare' in data['dependencies']
