"""
应用启动时的初始化和验证
"""

import os
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ConfigurationError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_configuration():
    """验证应用配置"""
    logger.info("Validating application configuration...")
    
    errors = []
    
    # 验证必需的目录
    required_dirs = ['logs', 'data']
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")
            except Exception as e:
                errors.append(f"Cannot create directory {dir_path}: {e}")
    
    # 验证数据库配置
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is required")
    
    # 验证SECRET_KEY
    if len(settings.SECRET_KEY) < 32:
        errors.append("SECRET_KEY must be at least 32 characters long")
    
    # 验证CORS配置
    if not settings.CORS_ORIGINS:
        logger.warning("CORS_ORIGINS not configured, using default")
    
    # 检查通知配置
    if not settings.email_configured and not settings.telegram_configured:
        logger.warning("No notification methods configured (email or telegram)")
    
    if settings.email_configured:
        logger.info("Email notifications configured")
    
    if settings.telegram_configured:
        logger.info("Telegram notifications configured")
    
    # 如果有错误，抛出异常
    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
        logger.error(error_msg)
        raise ConfigurationError(error_msg)
    
    logger.info("Configuration validation passed")


def create_default_config():
    """创建默认配置文件（如果不存在）"""
    env_file = Path(".env")
    
    if not env_file.exists():
        logger.info("Creating default .env file...")
        
        default_config = f"""# VisaStatusMonitor Configuration

# 基本配置
DEBUG=false
LOG_LEVEL=INFO

# 安全配置
SECRET_KEY={settings.SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL=sqlite:///./data/visa_monitor.db

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 邮件配置（可选）
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# SMTP_FROM_ADDRESS=your-email@gmail.com

# Telegram配置（可选）
# TELEGRAM_BOT_TOKEN=your-bot-token

# 查询配置
DEFAULT_QUERY_INTERVAL=1h
MAX_APPLICATIONS_PER_USER=10
QUERY_TIMEOUT_SECONDS=30
"""
        
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(default_config)
            logger.info(f"Default configuration created at {env_file}")
            logger.warning("Please review and update the configuration file before running in production")
        except Exception as e:
            logger.error(f"Failed to create default configuration: {e}")


def initialize_application():
    """初始化应用"""
    logger.info("Initializing VisaStatusMonitor application...")
    
    try:
        # 创建默认配置（如果需要）
        create_default_config()
        
        # 验证配置
        validate_configuration()
        
        logger.info("Application initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise