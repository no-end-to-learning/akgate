"""
健康检查端点
"""
import akshare as ak
from flask import Blueprint, jsonify

health = Blueprint('health', __name__)


@health.route('/health', methods=['GET'])
def health_check():
    """
    健康检查端点

    Returns:
        JSON 格式的健康状态
    """
    return jsonify({
        'status': 'healthy',
        'service': 'akgate',
    })


@health.route('/health/detail', methods=['GET'])
def health_detail():
    """
    详细健康检查端点

    检查 akshare 库是否可用

    Returns:
        JSON 格式的详细健康状态
    """
    akshare_status = 'healthy'
    akshare_version = None

    try:
        akshare_version = ak.__version__
    except Exception:
        akshare_status = 'unhealthy'

    return jsonify({
        'status': 'healthy' if akshare_status == 'healthy' else 'degraded',
        'service': 'akgate',
        'dependencies': {
            'akshare': {
                'status': akshare_status,
                'version': akshare_version,
            }
        }
    })
