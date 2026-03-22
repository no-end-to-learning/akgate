"""
API 视图模块

提供 akshare 函数的 REST API 接口
"""
import akshare as ak
import pandas as pd
import requests.exceptions
from flask import Blueprint, jsonify, request, current_app

from app.logging_config import get_logger
from app.exceptions import (
    FunctionNotFoundError,
    FunctionNotAllowedError,
    InvalidParameterError,
    DataFetchError,
)

logger = get_logger('api')

api = Blueprint('api', __name__)


def validate_function_name(func_name: str) -> None:
    """
    验证函数名称的合法性

    Args:
        func_name: 函数名称

    Raises:
        InvalidParameterError: 函数名称不合法
    """
    # 检查函数名是否为空
    if not func_name:
        raise InvalidParameterError("Function name cannot be empty")

    # 检查函数名是否只包含合法字符（字母、数字、下划线）
    if not func_name.replace('_', '').isalnum():
        raise InvalidParameterError(f"Invalid function name: {func_name}")

    # 防止访问私有函数或特殊函数
    if func_name.startswith('_'):
        raise InvalidParameterError("Cannot access private functions")


def check_function_allowed(func_name: str) -> None:
    """
    检查函数是否在白名单中

    Args:
        func_name: 函数名称

    Raises:
        FunctionNotAllowedError: 函数不在白名单中
    """
    config = current_app.config

    # 如果未启用白名单，跳过检查
    if not config.get('ENABLE_FUNCTION_WHITELIST', False):
        return

    allowed_functions = config.get('ALLOWED_FUNCTIONS', set())
    if func_name not in allowed_functions:
        logger.warning(f"Function not allowed: {func_name}")
        raise FunctionNotAllowedError(func_name)


def get_akshare_function(func_name: str):
    """
    获取 akshare 函数

    Args:
        func_name: 函数名称

    Returns:
        akshare 函数对象

    Raises:
        FunctionNotFoundError: 函数不存在
    """
    if not hasattr(ak, func_name):
        raise FunctionNotFoundError(func_name)

    return getattr(ak, func_name)


def convert_result(result) -> list | dict | None:
    """
    将结果转换为可序列化的格式

    Args:
        result: akshare 函数返回值

    Returns:
        转换后的数据
    """
    if result is None:
        return None

    if isinstance(result, pd.DataFrame):
        if result.empty:
            return []
        return result.to_dict('records')

    if isinstance(result, pd.Series):
        return result.to_dict()

    if isinstance(result, (list, dict, str, int, float, bool)):
        return result

    # 尝试转换为字符串
    return str(result)


@api.route("/<func_name>", methods=['GET'])
def call_function(func_name: str):
    """
    调用 akshare 函数

    Args:
        func_name: 函数名称

    Query Parameters:
        任意 akshare 函数支持的参数

    Returns:
        JSON 格式的函数返回数据
    """
    # 验证函数名
    validate_function_name(func_name)

    # 检查白名单
    check_function_allowed(func_name)

    # 获取函数
    func = get_akshare_function(func_name)

    # 调用函数
    try:
        # 将参数转换为普通字典，并对布尔值字符串做类型转换
        # （URL 参数全为字符串，'True'/'False' 需还原为 bool 以匹配 akshare 函数签名）
        params = {
            k: (True if v.lower() == 'true' else False if v.lower() == 'false' else v)
            for k, v in request.args.items()
        }
        logger.info(f"API call: {func_name} - params: {params}")
        result = func(**params)
    except TypeError as e:
        logger.warning(f"Parameter error: {func_name} - {str(e)}")
        raise InvalidParameterError(f"Invalid parameters: {str(e)}")
    except requests.exceptions.ConnectionError:
        logger.warning(f"Connection error: {func_name} - remote closed connection")
        raise DataFetchError("Upstream service unavailable, please retry later", status_code=503)
    except Exception as e:
        logger.error(f"Data fetch error: {func_name} - {str(e)}", exc_info=True)
        raise DataFetchError(f"Failed to fetch data: {str(e)}")

    # 转换结果
    data = convert_result(result)

    record_count = len(data) if isinstance(data, list) else 1
    logger.info(f"API success: {func_name} - records: {record_count}")

    return jsonify(data)


@api.route("/", methods=['GET'])
def list_functions():
    """
    列出可用的函数

    当启用白名单时，只返回白名单中的函数
    否则返回提示信息
    """
    config = current_app.config

    if config.get('ENABLE_FUNCTION_WHITELIST', False):
        allowed_functions = sorted(config.get('ALLOWED_FUNCTIONS', set()))
        return jsonify({
            'available_functions': allowed_functions,
            'count': len(allowed_functions),
        })

    return jsonify({
        'message': 'Function whitelist is disabled. All akshare functions are available.',
        'hint': 'Use /api/<function_name> to call any akshare function.',
        'documentation': 'https://akshare.akfamily.xyz/',
    })
