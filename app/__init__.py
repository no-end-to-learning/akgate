"""
AKGate - akshare REST API Gateway

Flask 应用工厂模块
"""
import warnings

from flask import Flask

from .config import get_config
from .encoder import CustomJSONProvider
from .exceptions import register_error_handlers
from .logging_config import setup_logging

# 过滤 akshare/pandas 的 FutureWarning（链式赋值警告）
warnings.filterwarnings('ignore', category=FutureWarning, module='akshare')


def create_app(config_class=None):
    """
    创建 Flask 应用实例

    Args:
        config_class: 配置类，默认根据环境变量自动选择

    Returns:
        Flask 应用实例
    """
    # 获取配置
    if config_class is None:
        config_class = get_config()

    # 初始化日志
    setup_logging(
        log_level=config_class.LOG_LEVEL,
        log_format=config_class.LOG_FORMAT,
    )

    # 创建 Flask 应用
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config_class)

    # 配置自定义 JSON 提供者
    app.json = CustomJSONProvider(app)

    # 注册异常处理器
    register_error_handlers(app)

    # 注册蓝图
    register_blueprints(app)

    return app


def register_blueprints(app):
    """
    注册所有蓝图

    Args:
        app: Flask 应用实例
    """
    from app.api import api
    from app.health import health

    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(health)
