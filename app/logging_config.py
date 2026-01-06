"""
日志配置模块
"""
import logging
import sys


def setup_logging(log_level: str = 'INFO', log_format: str = None):
    """
    配置应用日志

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: 日志格式字符串
    """
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # 获取日志级别
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # 配置根日志器
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # 设置第三方库的日志级别（减少噪音）
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器

    Args:
        name: 日志器名称

    Returns:
        Logger 实例
    """
    return logging.getLogger(name)
