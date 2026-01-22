"""
用户相关Pydantic模式
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模式"""
    username: str
    email: EmailStr
    preferred_language: Optional[str] = "en"
    timezone: Optional[str] = "UTC"


class UserCreate(UserBase):
    """用户创建模式"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('Username must contain only letters and numbers')
        return v


class UserUpdate(BaseModel):
    """用户更新模式"""
    email: Optional[EmailStr] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应模式"""
    id: int
    username: str
    email: str
    preferred_language: str
    timezone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """令牌响应模式"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse