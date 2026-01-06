"""
应用配置模块

支持通过环境变量覆盖默认配置
"""
import os


class Config:
    """基础配置类"""

    # Flask 配置
    DEBUG = False
    TESTING = False

    # API 配置
    API_PREFIX = '/api'

    # 安全配置：是否启用函数白名单限制
    # 设置为 False 时允许调用所有 akshare 函数（不推荐用于生产环境）
    ENABLE_FUNCTION_WHITELIST = os.getenv('ENABLE_FUNCTION_WHITELIST', 'false').lower() == 'true'

    # 函数白名单（仅当 ENABLE_FUNCTION_WHITELIST=True 时生效）
    # 可通过环境变量 ALLOWED_FUNCTIONS 设置，用逗号分隔
    ALLOWED_FUNCTIONS = set(
        os.getenv('ALLOWED_FUNCTIONS', '').split(',')
    ) if os.getenv('ALLOWED_FUNCTIONS') else {
        # 股票数据
        'stock_zh_a_hist',
        'stock_zh_a_spot_em',
        'stock_zh_a_hist_min_em',
        'stock_info_a_code_name',
        # ETF 数据
        'fund_etf_hist_em',
        'fund_etf_spot_em',
        # 期货数据
        'futures_zh_daily_sina',
        'futures_main_sina',
        # 指数数据
        'index_zh_a_hist',
        'index_stock_cons',
        # 宏观经济
        'macro_china_cpi',
        'macro_china_ppi',
    }

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 生产环境建议启用白名单
    ENABLE_FUNCTION_WHITELIST = os.getenv('ENABLE_FUNCTION_WHITELIST', 'true').lower() == 'true'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True


# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}


def get_config():
    """根据环境变量获取配置类"""
    env = os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, config_map['default'])
