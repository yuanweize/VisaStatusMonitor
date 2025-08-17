"""
国际化管理器
"""

import json
import os
from typing import Dict, Optional, Any
from pathlib import Path

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class I18nManager:
    """国际化管理器"""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.default_locale = settings.DEFAULT_LOCALE
        self.supported_locales = settings.SUPPORTED_LOCALES
        self.load_translations()
    
    def load_translations(self):
        """加载所有翻译文件"""
        locales_dir = Path("app/locales")
        
        # 确保locales目录存在
        locales_dir.mkdir(exist_ok=True)
        
        for locale in self.supported_locales:
            file_path = locales_dir / f"{locale}.json"
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[locale] = json.load(f)
                    logger.info(f"Loaded translations for locale: {locale}")
                except Exception as e:
                    logger.error(f"Failed to load translations for {locale}: {e}")
            else:
                logger.warning(f"Translation file not found: {file_path}")
                # 创建空的翻译字典
                self.translations[locale] = {}
    
    def get_text(self, key: str, locale: str = None, **kwargs) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键，支持点分隔的嵌套键 (e.g., "auth.login.title")
            locale: 语言代码，如果为None则使用默认语言
            **kwargs: 用于格式化文本的参数
            
        Returns:
            翻译后的文本，如果找不到则返回键本身
        """
        locale = locale or self.default_locale
        
        # 尝试获取指定语言的翻译
        text = self._get_nested_value(self.translations.get(locale, {}), key)
        if text:
            return self._format_text(text, **kwargs)
        
        # 回退到默认语言
        if locale != self.default_locale:
            text = self._get_nested_value(
                self.translations.get(self.default_locale, {}), key
            )
            if text:
                return self._format_text(text, **kwargs)
        
        # 如果都没找到，返回key本身
        logger.warning(f"Translation not found for key: {key}, locale: {locale}")
        return key
    
    def _get_nested_value(self, data: dict, key: str) -> Optional[str]:
        """获取嵌套字典的值"""
        if not isinstance(data, dict):
            return None
            
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value if isinstance(value, str) else None
    
    def _format_text(self, text: str, **kwargs) -> str:
        """格式化文本"""
        if not kwargs:
            return text
        
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.warning(f"Failed to format text '{text}' with kwargs {kwargs}: {e}")
            return text
    
    def is_supported_locale(self, locale: str) -> bool:
        """检查是否支持指定的语言"""
        return locale in self.supported_locales
    
    def get_supported_locales(self) -> list:
        """获取支持的语言列表"""
        return self.supported_locales.copy()
    
    def reload_translations(self):
        """重新加载翻译文件"""
        self.translations.clear()
        self.load_translations()
        logger.info("Translations reloaded")


# 创建全局国际化管理器实例
i18n_manager = I18nManager()


def get_i18n_manager() -> I18nManager:
    """获取国际化管理器实例（用于依赖注入）"""
    return i18n_manager