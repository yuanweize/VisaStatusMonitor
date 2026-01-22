# 插件开发指南

## 概述

VisaStatusMonitor 使用插件化架构来支持不同国家的签证状态查询。每个国家的查询逻辑都封装在独立的插件中，便于维护和扩展。

## 插件架构

### 基础插件类

所有插件都必须继承 `BasePlugin` 类：

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BasePlugin(ABC):
    @abstractmethod
    def get_country_code(self) -> str:
        """返回国家代码（ISO 3166-1 alpha-2）"""
        pass
    
    @abstractmethod
    def get_supported_query_types(self) -> List[str]:
        """返回支持的查询类型列表"""
        pass
    
    @abstractmethod
    def query_status(self, query_code: str, query_type: str) -> Dict[str, Any]:
        """查询申请状态"""
        pass
    
    @abstractmethod
    def validate_query_code(self, query_code: str, query_type: str) -> bool:
        """验证查询代码格式"""
        pass
```

### 返回数据格式

`query_status` 方法必须返回以下格式的字典：

```python
{
    'status': 'success|error',
    'data': {
        'application_status': str,  # 申请状态
        'last_update': str,         # 最后更新时间
        'details': str,             # 详细信息
        'raw_response': str         # 原始响应（可选）
    },
    'error': str  # 错误信息（仅在status为error时）
}
```

## 开发新插件

### 1. 创建插件文件

在 `backend/app/plugins/` 目录下创建新的插件文件，例如 `us_plugin.py`：

```python
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import re

from .base_plugin import BasePlugin

class USPlugin(BasePlugin):
    """美国移民局查询插件"""
    
    BASE_URL = "https://egov.uscis.gov/casestatus/mycasestatus.do"
    
    def get_country_code(self) -> str:
        return "US"
    
    def get_supported_query_types(self) -> List[str]:
        return ["receipt_number"]
    
    def validate_query_code(self, query_code: str, query_type: str) -> bool:
        """验证美国移民局收据号格式"""
        if query_type == "receipt_number":
            # 美国收据号格式：3个字母 + 10个数字
            pattern = r'^[A-Z]{3}\d{10}$'
            return bool(re.match(pattern, query_code))
        return False
    
    def query_status(self, query_code: str, query_type: str) -> Dict[str, Any]:
        try:
            # 发送查询请求
            response = self._make_request(query_code)
            
            # 解析响应
            parsed_data = self._parse_response(response)
            
            return {
                'status': 'success',
                'data': parsed_data
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _make_request(self, query_code: str) -> requests.Response:
        """发送HTTP请求"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        data = {
            'appReceiptNum': query_code,
            'caseStatusSearchBtn': 'CHECK STATUS'
        }
        
        response = requests.post(
            self.BASE_URL,
            data=data,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """解析HTML响应"""
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找状态信息
        status_div = soup.find('div', class_='current-status-sec')
        if not status_div:
            raise ValueError("无法找到状态信息")
        
        status_text = status_div.get_text(strip=True)
        
        return {
            'application_status': status_text,
            'last_update': '',  # 如果网站提供更新时间
            'details': status_text,
            'raw_response': response.text
        }
```

### 2. 注册插件

在 `backend/app/services/plugin_manager.py` 中注册新插件：

```python
from app.plugins.us_plugin import USPlugin

class PluginManager:
    def __init__(self):
        self.plugins = {
            'CZ': CzechPlugin(),
            'US': USPlugin(),  # 添加新插件
        }
```

### 3. 测试插件

创建测试文件 `backend/tests/test_us_plugin.py`：

```python
import pytest
from app.plugins.us_plugin import USPlugin

def test_us_plugin_country_code():
    plugin = USPlugin()
    assert plugin.get_country_code() == "US"

def test_us_plugin_validate_query_code():
    plugin = USPlugin()
    
    # 有效的收据号
    assert plugin.validate_query_code("MSC1234567890", "receipt_number")
    
    # 无效的收据号
    assert not plugin.validate_query_code("invalid", "receipt_number")

@pytest.mark.asyncio
async def test_us_plugin_query_status():
    plugin = USPlugin()
    
    # 使用模拟数据测试
    # 实际测试时应该使用mock来避免真实的网络请求
    pass
```

## 最佳实践

### 1. 错误处理

- 使用适当的异常处理
- 提供有意义的错误消息
- 区分网络错误和解析错误

### 2. 网络请求

- 设置合理的超时时间
- 使用适当的User-Agent
- 遵守目标网站的robots.txt
- 实现重试机制

### 3. 数据解析

- 使用BeautifulSoup或类似库解析HTML
- 处理网站结构变化的情况
- 保存原始响应用于调试

### 4. 性能优化

- 缓存不变的数据
- 避免过于频繁的请求
- 使用连接池

### 5. 安全考虑

- 验证输入数据
- 避免SQL注入和XSS
- 不在日志中记录敏感信息

## 调试技巧

### 1. 日志记录

```python
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def query_status(self, query_code: str, query_type: str) -> Dict[str, Any]:
    logger.info(f"Querying status for {query_code}")
    try:
        # 查询逻辑
        pass
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise
```

### 2. 响应保存

在开发阶段，保存原始响应用于分析：

```python
def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
    # 保存响应用于调试
    with open(f'debug_response_{int(time.time())}.html', 'w') as f:
        f.write(response.text)
    
    # 解析逻辑
    pass
```

### 3. 单元测试

使用mock来测试网络请求：

```python
from unittest.mock import patch, Mock

@patch('requests.post')
def test_query_with_mock(self, mock_post):
    mock_response = Mock()
    mock_response.text = '<html>mock response</html>'
    mock_post.return_value = mock_response
    
    plugin = USPlugin()
    result = plugin.query_status("MSC1234567890", "receipt_number")
    
    assert result['status'] == 'success'
```

## 贡献插件

1. Fork项目仓库
2. 创建新的分支
3. 开发和测试插件
4. 提交Pull Request
5. 等待代码审查

### Pull Request要求

- 包含完整的插件代码
- 提供单元测试
- 更新文档
- 遵循代码规范

## 支持

如果在开发插件过程中遇到问题：

1. 查看现有插件的实现
2. 阅读API文档
3. 提交Issue寻求帮助
4. 参与社区讨论