"""
通知相关Pydantic模式
"""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class NotificationResponse(BaseModel):
    """通知响应模式"""
    id: int
    application_id: int
    notification_type: str
    recipient: str
    subject: Optional[str]
    message: str
    status: str
    sent_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """通知创建模式"""
    application_id: int
    notification_type: str
    recipient: str
    subject: Optional[str] = None
    message: str
    
    @validator('notification_type')
    def validate_notification_type(cls, v):
        if v not in ['email', 'telegram', 'web']:
            raise ValueError('Invalid notification type')
        return v


class NotificationSettings(BaseModel):
    """通知设置模式"""
    global_notification_method: str = "email"
    telegram_chat_id: Optional[str] = None
    email_address: Optional[str] = None
    global_query_interval: str = "1h"
    
    @validator('global_notification_method')
    def validate_global_method(cls, v):
        if v not in ['email', 'telegram', 'web', 'none']:
            raise ValueError('Invalid notification method')
        return v