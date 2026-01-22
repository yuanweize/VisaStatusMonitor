"""
日志配置工具
"""

import os
import sys
from loguru import logger
from datetime import datetime

from app.core.config import settings


def setup_logger(name: str = None):
    """设置日志配置"""
    
    # 移除默认处理器
    logger.remove()
    
    # 确保日志目录存在
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    # 控制台输出格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件输出格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # 添加文件处理器 - 应用日志
    today = datetime.now().strftime("%Y-%m-%d")
    app_log_file = os.path.join(settings.LOG_DIR, f"app_{today}.log")
    
    logger.add(
        app_log_file,
        format=file_format,
        level=settings.LOG_LEVEL,
        rotation="1 day",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    # 添加错误日志文件
    error_log_file = os.path.join(settings.LOG_DIR, f"error_{today}.log")
    
    logger.add(
        error_log_file,
        format=file_format,
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    return logger