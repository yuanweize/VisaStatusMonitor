"""
查询日志相关Pydantic模式
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QueryLogResponse(BaseModel):
    """查询日志响应模式"""
    id: int
    application_id: int
    status: str
    application_status: Optional[str]
    details: Optional[str]
    error_message: Optional[str]
    query_timestamp: datetime
    response_time_ms: Optional[int]
    
    class Config:
        from_attributes = True


class QueryLogCreate(BaseModel):
    """查询日志创建模式"""
    application_id: int
    status: str
    application_status: Optional[str] = None
    details: Optional[str] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None