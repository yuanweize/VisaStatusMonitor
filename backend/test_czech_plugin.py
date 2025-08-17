#!/usr/bin/env python3
"""
捷克插件专项测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量避免配置文件依赖
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-that-is-at-least-32-characters-long-for-validation')
os.environ.setdefault('DEBUG', 'true')

from app.plugins.czech_plugin import CzechPlugin

# 简化的日志设置
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_czech_plugin_comprehensive():
    """全面测试捷克插件"""
    print("=" * 60)
    print("捷克移民局插件全面测试")
    print("=" * 60)
    
    # 创建插件实例
    plugin = CzechPlugin()
    
    # 测试基本信息
    print("\n1. 基本信息测试")
    print("-" * 30)
    print(f"国家代码: {plugin.get_country_code()}")
    print(f"国家名称: {plugin.get_country_name()}")
    print(f"支持的查询类型: {plugin.get_supported_query_types()}")
    
    # 测试查询类型信息
    print("\n2. 查询类型详细信息")
    print("-" * 30)
    for query_type_info in plugin.get_query_type_info():
        print(f"类型: {query_type_info['type']}")
        print(f"  名称: {query_type_info['name']}")
        print(f"  描述: {query_type_info['description']}")
        print(f"  格式: {query_type_info['format']}")
        print(f"  示例: {query_type_info['example']}")
        print()
    
    # 测试查询代码验证
    print("3. 查询代码验证测试")
    print("-" * 30)
    
    test_cases = [
        ("PRG123456789", "visa", True),
        ("PR12345678", "residence", True),
        ("CZ123456", "passport", True),
        ("INVALID123", "visa", False),
        ("PRG12345", "visa", False),
    ]
    
    for query_code, query_type, expected in test_cases:
        result = plugin.validate_query_code(query_code, query_type)
        status = "✓" if result == expected else "✗"
        print(f"{status} {query_code} ({query_type}): {result}")
    
    # 测试连接
    print("\n4. 连接测试")
    print("-" * 30)
    connection_result = plugin.test_connection()
    print(f"连接状态: {'成功' if connection_result else '失败'}")
    
    # 测试查询功能
    print("\n5. 查询功能测试")
    print("-" * 30)
    
    test_queries = [
        ("PRG123456781", "visa"),
        ("PRG123456784", "visa"),
        ("PR12345671", "residence"),
    ]
    
    for query_code, query_type in test_queries:
        print(f"\n查询 {query_code} ({query_type}):")
        try:
            result = plugin.query_status(query_code, query_type)
            print(f"  状态: {result.status}")
            print(f"  申请状态: {result.application_status}")
            print(f"  详情: {result.details}")
            print(f"  响应时间: {result.response_time_ms}ms")
            
        except Exception as e:
            print(f"  查询失败: {e}")


if __name__ == "__main__":
    try:
        test_czech_plugin_comprehensive()
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()