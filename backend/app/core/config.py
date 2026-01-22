"""
应用配置管理
"""

from pydantic_settings import BaseSettings
from pydantic import validator, Field
from typing import List, Optional
import os
import secrets


class Settings(BaseSettings):
    """应用设置"""
    
    # 基本配置
    APP_NAME: str = "VisaStatusMonitor"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 安全配置
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/visa_checker.db"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"
    
    # 邮件配置
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_ADDRESS: Optional[str] = None
    
    # Telegram配置
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # 查询配置
    DEFAULT_QUERY_INTERVAL: str = "1h"
    MAX_APPLICATIONS_PER_USER: int = 10
    QUERY_TIMEOUT_SECONDS: int = 30
    
    # 国际化配置
    DEFAULT_LOCALE: str = "en"
    SUPPORTED_LOCALES: List[str] = ["zh-CN", "en"]
    
    @validator('CORS_ORIGINS', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @property
    def email_configured(self) -> bool:
        """检查邮件是否配置完整"""
        return all([
            self.SMTP_SERVER,
            self.SMTP_USERNAME,
            self.SMTP_PASSWORD,
            self.SMTP_FROM_ADDRESS
        ])
    
    @property
    def telegram_configured(self) -> bool:
        """检查Telegram是否配置完整"""
        return bool(self.TELEGRAM_BOT_TOKEN)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """获取设置实例（支持依赖注入）"""
    return Settings()


# 创建全局设置实例
settings = get_settings()