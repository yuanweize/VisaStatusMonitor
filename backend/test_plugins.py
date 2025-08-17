#!/usr/bin/env python3
"""
插件系统测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量避免配置文件依赖
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-that-is-at-least-32-characters-long-for-validation')
os.environ.setdefault('DEBUG', 'true')

from app.plugins.plugin_manager import get_plugin_manager

# 简化的日志设置
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_plugin_manager():
    """测试插件管理器"""
    print("=" * 50)
    print("测试插件管理器")
    print("=" * 50)
    
    # 获取插件管理器
    plugin_manager = get_plugin_manager()
    
    # 测试基本功能
    print(f"支持的国家: {plugin_manager.get_supported_countries()}")
    print(f"插件数量: {len(plugin_manager.get_all_plugins())}")
    
    # 测试插件信息
    print("\n插件信息:")
    for plugin_info in plugin_manager.get_all_plugins_info():
        print(f"- {plugin_info['country_name']} ({plugin_info['country_code']})")
        print(f"  版本: {plugin_info.get('version', 'N/A')}")
        print(f"  支持的查询类型: {[qt['type'] for qt in plugin_info['supported_query_types']]}")
    
    # 测试捷克插件
    print("\n=" * 50)
    print("测试捷克插件")
    print("=" * 50)
    
    czech_plugin = plugin_manager.get_plugin("CZ")
    if czech_plugin:
        print(f"插件名称: {czech_plugin.get_country_name()}")
        print(f"支持的查询类型: {czech_plugin.get_supported_query_types()}")
        
        # 测试查询代码验证
        test_codes = [
            ("PRG123456789", "visa", True),
            ("PR12345678", "residence", True),
            ("INVALID123", "visa", False),
            ("PRG12345", "visa", False),
        ]
        
        print("\n查询代码验证测试:")
        for code, query_type, expected in test_codes:
            result = czech_plugin.validate_query_code(code, query_type)
            status = "✓" if result == expected else "✗"
            print(f"{status} {code} ({query_type}): {result}")
        
        # 测试连接
        print("\n连接测试:")
        connection_result = czech_plugin.test_connection()
        print(f"连接状态: {'成功' if connection_result else '失败'}")
        
        # 测试查询（使用模拟数据）
        print("\n查询测试:")
        test_query_codes = ["PRG123456781", "PRG123456784", "PRG123456787"]
        
        for query_code in test_query_codes:
            print(f"\n查询 {query_code}:")
            result = czech_plugin.query_status(query_code, "visa")
            print(f"  状态: {result.status}")
            print(f"  申请状态: {result.application_status}")
            print(f"  详情: {result.details}")
            print(f"  响应时间: {result.response_time_ms}ms")
    else:
        print("未找到捷克插件")
    
    # 测试插件统计
    print("\n=" * 50)
    print("插件统计信息")
    print("=" * 50)
    
    stats = plugin_manager.get_plugin_stats()
    print(f"总插件数: {stats['total_plugins']}")
    print(f"支持的国家: {', '.join(stats['supported_countries'])}")


def test_connection_all():
    """测试所有插件连接"""
    print("\n=" * 50)
    print("测试所有插件连接")
    print("=" * 50)
    
    plugin_manager = get_plugin_manager()
    results = plugin_manager.test_all_connections()
    
    for country, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {country}: {'连接成功' if result else '连接失败'}")


if __name__ == "__main__":
    try:
        test_plugin_manager()
        test_connection_all()
        print("\n" + "=" * 50)
        print("所有测试完成")
        print("=" * 50)
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()