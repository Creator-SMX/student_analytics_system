#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复验证测试脚本"""
import json
import logging
import requests
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:5000/analytics"

def test_api_endpoint(endpoint, expected_keys=None):
    """测试API端点是否正常返回数据"""
    url = f"{BASE_URL}{endpoint}"
    logger.info(f"测试API端点: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 解析JSON响应
        data = response.json()
        logger.info(f"✅ API {endpoint} 响应成功")
        
        # 检查返回数据的基本结构
        if 'success' not in data:
            logger.warning(f"⚠️ API {endpoint} 未返回success标志")
        elif not data['success']:
            logger.error(f"❌ API {endpoint} 返回失败状态: {data.get('message', '未知错误')}")
            return False
        
        # 检查预期的键是否存在
        if expected_keys:
            for key in expected_keys:
                if key not in data:
                    logger.error(f"❌ API {endpoint} 缺少预期的键: {key}")
                    return False
        
        # 打印部分数据用于验证
        logger.info(f"返回数据示例: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ API {endpoint} 请求失败: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"❌ API {endpoint} 返回的不是有效JSON: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ API {endpoint} 测试时发生未知错误: {str(e)}")
        return False

def test_access_pattern_api():
    """测试门禁模式API"""
    logger.info("===== 测试门禁模式API =====")
    return test_api_endpoint("/api/get_access_pattern", ['hours', 'counts'])

def test_time_analysis_api():
    """测试24小时消费时段分析API"""
    logger.info("===== 测试24小时消费时段分析API =====")
    return test_api_endpoint("/api/get_time_analysis", ['hourly_data'])

def test_overview_api():
    """测试概览数据API"""
    logger.info("===== 测试概览数据API =====")
    return test_api_endpoint("/api/get_overview", ['student_count', 'total_amount', 'avg_consumption'])

def main():
    """主测试函数"""
    logger.info("=== 开始修复验证测试 ===")
    
    # 等待服务器完全启动
    logger.info("等待服务器启动...")
    time.sleep(2)
    
    tests = [
        test_access_pattern_api,
        test_time_analysis_api,
        test_overview_api
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    if all_passed:
        logger.info("🎉 所有API测试通过！")
        logger.info("💡 请刷新浏览器页面验证前端数据显示是否正常")
        return 0
    else:
        logger.error("❌ 部分API测试失败，请检查日志获取详细信息")
        return 1

if __name__ == "__main__":
    exit(main())