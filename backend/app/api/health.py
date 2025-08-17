"""
健康检查和系统状态API
"""

from fastapi import APIRouter, Header, Depends
from datetime import datetime
import psutil
import os
from typing import Optional

from app.core.config import settings
from app.core.scheduler import scheduler
from app.core.database import get_database_info, check_database_connection
from app.core.i18n import get_i18n_manager

router = APIRouter()


def get_user_locale(accept_language: Optional[str] = Header(None)) -> str:
    """从请求头获取用户语言偏好"""
    if accept_language:
        # 解析 Accept-Language 头
        languages = accept_language.split(',')
        for lang in languages:
            lang_code = lang.split(';')[0].strip()
            if lang_code in settings.SUPPORTED_LOCALES:
                return lang_code
            # 处理简化的语言代码 (如 zh 匹配 zh-CN)
            if lang_code == 'zh':
                return 'zh-CN'
    return settings.DEFAULT_LOCALE


@router.get("/health")
async def health_check(
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """基础健康检查"""
    return {
        "status": i18n.get_text("system.healthy", locale),
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """详细健康检查"""
    try:
        # 系统信息
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        db_info = get_database_info()
        
        return {
            "status": i18n.get_text("system.healthy", locale),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "app_name": settings.APP_NAME,
            "debug_mode": settings.DEBUG,
            "i18n": {
                "current_locale": locale,
                "supported_locales": settings.SUPPORTED_LOCALES,
                "default_locale": settings.DEFAULT_LOCALE
            },
            "scheduler": {
                "status": i18n.get_text("system.schedulerRunning" if scheduler.running else "system.schedulerStopped", locale),
                "running": scheduler.running,
                "jobs_count": len(scheduler.scheduler.get_jobs()) if scheduler.running else 0
            },
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            },
            "database": {
                **db_info,
                "status": i18n.get_text("system.databaseConnected" if db_info.get("connected") else "system.databaseDisconnected", locale)
            }
        }
    except Exception as e:
        return {
            "status": i18n.get_text("system.unhealthy", locale),
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/version")
async def get_version():
    """获取版本信息"""
    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "build_time": "2024-01-01T00:00:00Z",  # TODO: 从构建时设置
        "git_commit": "unknown"  # TODO: 从构建时设置
    }


