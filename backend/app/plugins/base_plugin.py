"""
插件基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class QueryResult:
    """查询结果数据类"""
    
    def __init__(
        self,
        status: str,
        application_status: Optional[str] = None,
        details: Optional[str] = None,
        last_update: Optional[str] = None,
        raw_response: Optional[str] = None,
        error: Optional[str] = None,
        response_time_ms: Optional[int] = None
    ):
        self.status = status  # 'success' or 'error'
        self.application_status = application_status
        self.details = details
        self.last_update = last_update
        self.raw_response = raw_response
        self.error = error
        self.response_time_ms = response_time_ms
        self.query_timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'status': self.status,
            'data': {
                'application_status': self.application_status,
                'details': self.details,
                'last_update': self.last_update,
                'raw_response': self.raw_response,
                'query_timestamp': self.query_timestamp.isoformat()
            } if self.status == 'success' else None,
            'error': self.error,
            'response_time_ms': self.response_time_ms
        }


class BasePlugin(ABC):
    """查询插件基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.logger = setup_logger(f"plugin.{self.get_country_code().lower()}")
    
    @abstractmethod
    def get_country_code(self) -> str:
        """
        返回国家代码（ISO 3166-1 alpha-2）
        
        Returns:
            国家代码，如 'CZ', 'US', 'DE' 等
        """
        pass
    
    @abstractmethod
    def get_country_name(self) -> str:
        """
        返回国家名称
        
        Returns:
            国家名称，如 'Czech Republic', 'United States' 等
        """
        pass
    
    @abstractmethod
    def get_supported_query_types(self) -> List[str]:
        """
        返回支持的查询类型列表
        
        Returns:
            查询类型列表，如 ['visa_application_number', 'passport_number']
        """
        pass
    
    @abstractmethod
    def get_query_type_description(self, query_type: str) -> str:
        """
        返回查询类型的描述
        
        Args:
            query_type: 查询类型
            
        Returns:
            查询类型的描述
        """
        pass
    
    @abstractmethod
    def validate_query_code(self, query_code: str, query_type: str) -> bool:
        """
        验证查询代码格式
        
        Args:
            query_code: 查询代码
            query_type: 查询类型
            
        Returns:
            验证结果
        """
        pass
    
    @abstractmethod
    def query_status(self, query_code: str, query_type: str) -> QueryResult:
        """
        查询申请状态
        
        Args:
            query_code: 查询代码
            query_type: 查询类型
            
        Returns:
            查询结果对象
        """
        pass
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """
        获取插件信息
        
        Returns:
            插件信息字典
        """
        return {
            'name': self.name,
            'country_code': self.get_country_code(),
            'country_name': self.get_country_name(),
            'supported_query_types': self.get_supported_query_types(),
            'version': getattr(self, 'VERSION', '1.0.0'),
            'description': getattr(self, 'DESCRIPTION', ''),
            'author': getattr(self, 'AUTHOR', ''),
            'website': getattr(self, 'WEBSITE', '')
        }
    
    def get_query_type_info(self) -> List[Dict[str, str]]:
        """
        获取查询类型信息
        
        Returns:
            查询类型信息列表
        """
        return [
            {
                'type': query_type,
                'description': self.get_query_type_description(query_type)
            }
            for query_type in self.get_supported_query_types()
        ]
    
    def _measure_response_time(self, func, *args, **kwargs) -> tuple:
        """
        测量响应时间的装饰器辅助方法
        
        Args:
            func: 要测量的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            (结果, 响应时间毫秒)
        """
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            return result, response_time_ms
        except Exception as e:
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            raise e
    
    def safe_query_status(self, query_code: str, query_type: str) -> QueryResult:
        """
        安全的查询状态方法，包含错误处理和性能监控
        
        Args:
            query_code: 查询代码
            query_type: 查询类型
            
        Returns:
            查询结果对象
        """
        self.logger.info(f"Starting query for {query_code} (type: {query_type})")
        
        try:
            # 验证查询代码
            if not self.validate_query_code(query_code, query_type):
                return QueryResult(
                    status='error',
                    error=f'Invalid query code format for type {query_type}'
                )
            
            # 执行查询并测量响应时间
            result, response_time_ms = self._measure_response_time(
                self.query_status, query_code, query_type
            )
            
            # 设置响应时间
            result.response_time_ms = response_time_ms
            
            self.logger.info(
                f"Query completed for {query_code}: {result.status} "
                f"({response_time_ms}ms)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Query failed for {query_code}: {str(e)}")
            return QueryResult(
                status='error',
                error=str(e)
            )
    
    def test_connection(self) -> bool:
        """
        测试插件连接
        
        Returns:
            连接测试结果
        """
        try:
            # 子类可以重写此方法来实现具体的连接测试
            self.logger.info(f"Testing connection for {self.get_country_code()} plugin")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """
        获取速率限制信息
        
        Returns:
            速率限制信息
        """
        # 子类可以重写此方法来提供具体的速率限制信息
        return {
            'requests_per_minute': getattr(self, 'RATE_LIMIT_RPM', 60),
            'requests_per_hour': getattr(self, 'RATE_LIMIT_RPH', 1000),
            'concurrent_requests': getattr(self, 'CONCURRENT_REQUESTS', 5)
        }
    
    def __str__(self) -> str:
        return f"{self.name} ({self.get_country_code()})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(country={self.get_country_code()})>"