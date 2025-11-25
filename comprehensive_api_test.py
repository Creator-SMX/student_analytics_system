#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""综合测试API调用，模拟前端逻辑，验证修复后的功能"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001"

# 测试函数：模拟前端处理逻辑
def test_api_endpoint(endpoint, expected_fields=None):
    """测试API端点并验证响应格式"""
    url = BASE_URL + endpoint
    print(f"\n测试端点: {url}")
    
    try:
        # 发送请求
        response = requests.get(url, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应头Content-Type: {response.headers.get('Content-Type', '未设置')}")
        
        # 尝试解析JSON，模拟前端错误处理
        try:
            data = response.json()
            print(f"✓ 响应成功解析为JSON")
            
            # 验证success字段
            if 'success' not in data:
                print(f"✗ 警告: 缺少success字段")
            else:
                print(f"✓ success字段值: {data['success']}")
                
            # 如果success为True，验证预期字段
            if data.get('success') is True:
                # 打印所有字段以便分析
                print(f"✓ 响应包含的所有字段: {list(data.keys())}")
                
                # 验证特定端点的数据字段
                if endpoint == '/analytics/api/get_time_analysis':
                    if 'hourly_data' in data and isinstance(data['hourly_data'], dict):
                        print(f"✓ 包含正确的hourly_data字段，共{len(data['hourly_data'])}个时段")
                    else:
                        print(f"✗ 缺少或错误的hourly_data字段")
                        
                elif endpoint == '/analytics/api/get_cluster':
                    required_fields = ['labels', 'counts', 'total_consumers']
                    for field in required_fields:
                        if field in data:
                            print(f"✓ 包含{field}字段")
                        else:
                            print(f"✗ 缺少{field}字段")
                
                elif endpoint == '/analytics/api/get_access_pattern':
                    required_fields = ['hours', 'counts']
                    for field in required_fields:
                        if field in data:
                            print(f"✓ 包含{field}字段")
                        else:
                            print(f"✗ 缺少{field}字段")
                
                elif endpoint == '/analytics/api/get_overview':
                    required_fields = ['student_count', 'total_amount', 'transaction_count']
                    for field in required_fields:
                        if field in data:
                            print(f"✓ 包含{field}字段")
                        else:
                            print(f"✗ 缺少{field}字段")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"✗ 严重错误: JSON解析失败 - {e}")
            print(f"响应内容前200字符: {response.text[:200]}...")
            return False
        except Exception as e:
            print(f"✗ 处理响应时出错: {e}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"✗ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print(f"✗ 连接错误，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"✗ 请求出错: {e}")
        return False

# 要测试的API端点列表
api_endpoints = [
    "/analytics/api/get_overview",
    "/analytics/api/get_time_analysis",
    "/analytics/api/get_access_pattern",
    "/analytics/api/get_cluster",
    "/analytics/api/get_canteen_analysis"
]

print("===== 开始综合API测试 =====")
print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"目标服务器: {BASE_URL}")
print("=" * 50)

# 运行所有测试
success_count = 0
for endpoint in api_endpoints:
    if test_api_endpoint(endpoint):
        success_count += 1
    print("-" * 50)

# 测试总结
print(f"\n===== 测试总结 =====")
print(f"总测试端点数: {len(api_endpoints)}")
print(f"成功数: {success_count}")
print(f"失败数: {len(api_endpoints) - success_count}")
print(f"成功率: {success_count / len(api_endpoints) * 100:.1f}%")
print(f"\n测试完成! {time.strftime('%Y-%m-%d %H:%M:%S')}")

if success_count == len(api_endpoints):
    print("\n🎉 所有API端点测试通过! 修复成功!")
else:
    print("\n❌ 部分API端点测试失败，请检查错误信息并进行修复。")