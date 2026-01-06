"""
测试配置和固定装置
"""
import pytest

from app import create_app
from app.config import TestingConfig


@pytest.fixture
def app():
    """创建测试应用实例"""
    app = create_app(TestingConfig)
    yield app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建 CLI 测试运行器"""
    return app.test_cli_runner()
