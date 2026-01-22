"""
申请相关Pydantic模式
"""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ApplicationBase(BaseModel):
    """申请基础模式"""
    country_code: str
    applicant_name: str
    query_code: str
    query_type: str
    notification_method: Optional[str] = None
    notification_target: Optional[str] = None
    query_interval: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    """申请创建模式"""
    
    @validator('country_code')
    def validate_country_code(cls, v):
        if len(v) != 2:
            raise ValueError('Country code must be 2 characters')
        return v.upper()
    
    @validator('applicant_name')
    def validate_applicant_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Applicant name must be at least 2 characters')
        return v.strip()
    
    @validator('query_code')
    def validate_query_code(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Query code must be at least 3 characters')
        return v.strip()
    
    @validator('notification_method')
    def validate_notification_method(cls, v):
        if v and v not in ['email', 'telegram', 'web', 'none']:
            raise ValueError('Invalid notification method')
        return v
    
    @validator('query_interval')
    def validate_query_interval(cls, v):
        if v and not any(v.endswith(unit) for unit in ['m', 'h', 'd', 'w']):
            raise ValueError('Invalid query interval format')
        return v


class ApplicationUpdate(BaseModel):
    """申请更新模式"""
    applicant_name: Optional[str] = None
    notification_method: Optional[str] = None
    notification_target: Optional[str] = None
    query_interval: Optional[str] = None
    is_active: Optional[bool] = None


class ApplicationResponse(BaseModel):
    """申请响应模式"""
    id: int
    user_id: int
    country_code: str
    applicant_name: str
    query_code: str
    query_type: str
    notification_method: Optional[str]
    notification_target: Optional[str]
    query_interval: Optional[str]
    latest_status: Optional[str]
    latest_details: Optional[str]
    last_checked: Optional[datetime]
    last_status_change: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True