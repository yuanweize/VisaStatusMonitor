"""
通用Pydantic模式
"""

from pydantic import BaseModel
from typing import Any, Optional, List, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class ResponseModel(BaseModel):
    """标准API响应模式"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模式"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str
    version: str
    details: Optional[dict] = None