"""
插件管理器
"""

import importlib
import pkgutil
from typing import Dict, List, Optional, Type, Any
from pathlib import Path

from app.plugins.base_plugin import BasePlugin, QueryResult
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """加载所有插件"""
        logger.info("Loading plugins...")
        
        # 获取插件目录
        plugins_dir = Path(__file__).parent
        
        # 遍历插件目录中的所有Python文件
        for finder, name, ispkg in pkgutil.iter_modules([str(plugins_dir)]):
            if name.startswith('_') or name in ['base_plugin', 'plugin_manager']:
                continue
            
            try:
                # 动态导入插件模块
                module_name = f"app.plugins.{name}"
                module = importlib.import_module(module_name)
                
                # 查找插件类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # 检查是否是BasePlugin的子类（但不是BasePlugin本身）
                    if (isinstance(attr, type) and 
                        issubclass(attr, BasePlugin) and 
                        attr != BasePlugin):
                        
                        try:
                            # 实例化插件
                            plugin_instance = attr()
                            country_code = plugin_instance.get_country_code()
                            
                            # 注册插件
                            self.plugins[country_code] = plugin_instance
                            self.plugin_classes[country_code] = attr
                            
                            logger.info(f"Loaded plugin: {plugin_instance}")
                            
                        except Exception as e:
                            logger.error(f"Failed to instantiate plugin {attr_name}: {e}")
                
            except Exception as e:
                logger.error(f"Failed to load plugin module {name}: {e}")
        
        logger.info(f"Loaded {len(self.plugins)} plugins: {list(self.plugins.keys())}")
    
    def get_plugin(self, country_code: str) -> Optional[BasePlugin]:
        """
        获取指定国家的插件
        
        Args:
            country_code: 国家代码
            
        Returns:
            插件实例或None
        """
        return self.plugins.get(country_code.upper())
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        获取所有插件
        
        Returns:
            插件字典
        """
        return self.plugins.copy()
    
    def get_supported_countries(self) -> List[str]:
        """
        获取支持的国家代码列表
        
        Returns:
            国家代码列表
        """
        return list(self.plugins.keys())
    
    def is_country_supported(self, country_code: str) -> bool:
        """
        检查是否支持指定国家
        
        Args:
            country_code: 国家代码
            
        Returns:
            是否支持
        """
        return country_code.upper() in self.plugins
    
    def get_plugin_info(self, country_code: str) -> Optional[Dict[str, Any]]:
        """
        获取插件信息
        
        Args:
            country_code: 国家代码
            
        Returns:
            插件信息或None
        """
        plugin = self.get_plugin(country_code)
        return plugin.get_plugin_info() if plugin else None
    
    def get_all_plugins_info(self) -> List[Dict[str, Any]]:
        """
        获取所有插件信息
        
        Returns:
            插件信息列表
        """
        return [plugin.get_plugin_info() for plugin in self.plugins.values()]
    
    def get_query_types(self, country_code: str) -> List[str]:
        """
        获取指定国家支持的查询类型
        
        Args:
            country_code: 国家代码
            
        Returns:
            查询类型列表
        """
        plugin = self.get_plugin(country_code)
        return plugin.get_supported_query_types() if plugin else []
    
    def get_query_type_info(self, country_code: str) -> List[Dict[str, str]]:
        """
        获取指定国家的查询类型信息
        
        Args:
            country_code: 国家代码
            
        Returns:
            查询类型信息列表
        """
        plugin = self.get_plugin(country_code)
        return plugin.get_query_type_info() if plugin else []
    
    def validate_query_code(self, country_code: str, query_code: str, query_type: str) -> bool:
        """
        验证查询代码
        
        Args:
            country_code: 国家代码
            query_code: 查询代码
            query_type: 查询类型
            
        Returns:
            验证结果
        """
        plugin = self.get_plugin(country_code)
        if not plugin:
            logger.warning(f"Plugin not found for country: {country_code}")
            return False
        
        return plugin.validate_query_code(query_code, query_type)
    
    def query_status(self, country_code: str, query_code: str, query_type: str) -> QueryResult:
        """
        查询申请状态
        
        Args:
            country_code: 国家代码
            query_code: 查询代码
            query_type: 查询类型
            
        Returns:
            查询结果
        """
        plugin = self.get_plugin(country_code)
        if not plugin:
            logger.error(f"Plugin not found for country: {country_code}")
            return QueryResult(
                status='error',
                error=f'No plugin available for country: {country_code}'
            )
        
        return plugin.safe_query_status(query_code, query_type)
    
    def test_plugin_connection(self, country_code: str) -> bool:
        """
        测试插件连接
        
        Args:
            country_code: 国家代码
            
        Returns:
            连接测试结果
        """
        plugin = self.get_plugin(country_code)
        if not plugin:
            return False
        
        return plugin.test_connection()
    
    def test_all_connections(self) -> Dict[str, bool]:
        """
        测试所有插件连接
        
        Returns:
            连接测试结果字典
        """
        results = {}
        for country_code, plugin in self.plugins.items():
            results[country_code] = plugin.test_connection()
        return results
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """
        获取插件统计信息
        
        Returns:
            统计信息
        """
        return {
            'total_plugins': len(self.plugins),
            'supported_countries': list(self.plugins.keys()),
            'plugins_info': self.get_all_plugins_info()
        }
    
    def reload_plugin(self, country_code: str) -> bool:
        """
        重新加载指定插件
        
        Args:
            country_code: 国家代码
            
        Returns:
            重新加载是否成功
        """
        try:
            if country_code.upper() not in self.plugin_classes:
                logger.error(f"Plugin class not found for country: {country_code}")
                return False
            
            # 重新实例化插件
            plugin_class = self.plugin_classes[country_code.upper()]
            new_instance = plugin_class()
            
            # 更新插件实例
            self.plugins[country_code.upper()] = new_instance
            
            logger.info(f"Reloaded plugin for country: {country_code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload plugin for {country_code}: {e}")
            return False
    
    def reload_all_plugins(self) -> bool:
        """
        重新加载所有插件
        
        Returns:
            重新加载是否成功
        """
        try:
            self.plugins.clear()
            self.plugin_classes.clear()
            self._load_plugins()
            logger.info("All plugins reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reload all plugins: {e}")
            return False


# 创建全局插件管理器实例
plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """获取插件管理器实例（用于依赖注入）"""
    return plugin_manager