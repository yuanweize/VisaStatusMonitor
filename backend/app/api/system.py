"""
系统状态API路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_user_locale
from app.core.i18n import get_i18n_manager
from app.plugins.plugin_manager import get_plugin_manager
from app.services.query_engine import QueryEngine
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/countries")
async def get_supported_countries(
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """获取支持的国家列表"""
    try:
        query_engine = QueryEngine(db)
        countries = query_engine.get_supported_countries()
        
        return {
            "success": True,
            "message": i18n.get_text("system.countriesLoaded", locale),
            "data": countries
        }
        
    except Exception as e:
        logger.error(f"Failed to get supported countries: {e}")
        return {
            "success": False,
            "error": i18n.get_text("system.countriesLoadFailed", locale)
        }


@router.get("/plugins")
async def get_plugins_info(
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """获取插件信息"""
    try:
        plugin_manager = get_plugin_manager()
        plugins_info = plugin_manager.get_all_plugins_info()
        stats = plugin_manager.get_plugin_stats()
        
        return {
            "success": True,
            "message": i18n.get_text("system.pluginsLoaded", locale),
            "data": {
                "plugins": plugins_info,
                "statistics": stats
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get plugins info: {e}")
        return {
            "success": False,
            "error": i18n.get_text("system.pluginsLoadFailed", locale)
        }


@router.get("/plugins/{country_code}")
async def get_plugin_info(
    country_code: str,
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """获取指定国家的插件信息"""
    try:
        plugin_manager = get_plugin_manager()
        plugin_info = plugin_manager.get_plugin_info(country_code)
        
        if not plugin_info:
            return {
                "success": False,
                "error": i18n.get_text("system.pluginNotFound", locale)
            }
        
        return {
            "success": True,
            "data": plugin_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get plugin info for {country_code}: {e}")
        return {
            "success": False,
            "error": i18n.get_text("system.pluginInfoFailed", locale)
        }


@router.post("/plugins/{country_code}/test")
async def test_plugin_connection(
    country_code: str,
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """测试插件连接"""
    try:
        plugin_manager = get_plugin_manager()
        result = plugin_manager.test_plugin_connection(country_code)
        
        return {
            "success": result,
            "message": i18n.get_text(
                "system.connectionTestSuccess" if result else "system.connectionTestFailed",
                locale
            ),
            "data": {"connected": result}
        }
        
    except Exception as e:
        logger.error(f"Plugin connection test failed for {country_code}: {e}")
        return {
            "success": False,
            "error": i18n.get_text("system.connectionTestError", locale)
        }


@router.get("/statistics")
async def get_system_statistics(
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """获取系统统计信息"""
    try:
        query_engine = QueryEngine(db)
        stats = query_engine.get_query_statistics()
        
        return {
            "success": True,
            "message": i18n.get_text("system.statisticsLoaded", locale),
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get system statistics: {e}")
        return {
            "success": False,
            "error": i18n.get_text("system.statisticsLoadFailed", locale)
        }