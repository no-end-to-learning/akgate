"""
异常处理模块

定义自定义异常和全局异常处理器
"""
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    """API 基础异常类"""

    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or 'API_ERROR'

    def to_dict(self):
        return {
            'error': True,
            'error_code': self.error_code,
            'message': self.message,
        }


class FunctionNotFoundError(APIError):
    """函数不存在异常"""

    def __init__(self, func_name: str):
        super().__init__(
            message=f"Function '{func_name}' not found in akshare",
            status_code=404,
            error_code='FUNCTION_NOT_FOUND'
        )


class FunctionNotAllowedError(APIError):
    """函数不在白名单异常"""

    def __init__(self, func_name: str):
        super().__init__(
            message=f"Function '{func_name}' is not allowed",
            status_code=403,
            error_code='FUNCTION_NOT_ALLOWED'
        )


class InvalidParameterError(APIError):
    """参数无效异常"""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            error_code='INVALID_PARAMETER'
        )


class DataFetchError(APIError):
    """数据获取异常"""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500,
            error_code='DATA_FETCH_ERROR'
        )


def register_error_handlers(app):
    """
    注册全局异常处理器

    Args:
        app: Flask 应用实例
    """
    from app.logging_config import get_logger
    logger = get_logger('error_handler')

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """处理自定义 API 异常"""
        logger.warning(f"API Error: {error.error_code} - {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """处理 HTTP 异常"""
        logger.warning(f"HTTP Error: {error.code} - {error.description}")
        response = jsonify({
            'error': True,
            'error_code': 'HTTP_ERROR',
            'message': error.description,
        })
        response.status_code = error.code
        return response

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """处理未捕获的异常"""
        logger.error(f"Unhandled Exception: {type(error).__name__} - {str(error)}", exc_info=True)

        # 在调试模式下返回详细错误信息
        if current_app.debug:
            message = f"{type(error).__name__}: {str(error)}"
        else:
            message = "Internal server error"

        response = jsonify({
            'error': True,
            'error_code': 'INTERNAL_ERROR',
            'message': message,
        })
        response.status_code = 500
        return response
