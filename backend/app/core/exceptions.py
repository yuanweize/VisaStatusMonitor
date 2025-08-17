"""
自定义异常类
"""

from fastapi import HTTPException


class ConfigurationError(Exception):
    """配置错误"""
    pass


class DatabaseError(Exception):
    """数据库错误"""
    pass


class PluginError(Exception):
    """插件错误"""
    pass


class QueryError(Exception):
    """查询错误"""
    pass


class NotificationError(Exception):
    """通知错误"""
    pass


# HTTP异常
class BadRequestException(HTTPException):
    def __init__(self, detail: str = "请求参数错误"):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "未授权访问"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "禁止访问"):
        super().__init__(status_code=403, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "资源未找到"):
        super().__init__(status_code=404, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "资源冲突"):
        super().__init__(status_code=409, detail=detail)


class ValidationException(HTTPException):
    def __init__(self, detail: str = "数据验证失败"):
        super().__init__(status_code=422, detail=detail)


class InternalServerException(HTTPException):
    def __init__(self, detail: str = "服务器内部错误"):
        super().__init__(status_code=500, detail=detail)