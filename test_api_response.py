#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试API端点的响应格式"""
import requests
import json

BASE_URL = "http://127.0.0.1:5001"

# 要测试的API端点
api_endpoints = [
    "/analytics/api/get_time_analysis",
    "/analytics/api/get_cluster",
    "/analytics/api/get_access_pattern",
    "/analytics/api/get_canteen_analysis",
    "/analytics/api/get_overview"
]

print("开始测试API端点响应格式...\n")

for endpoint in api_endpoints:
    url = BASE_URL + endpoint
    print(f"测试端点: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应头Content-Type: {response.headers.get('Content-Type', '未设置')}")
        
        # 尝试解析JSON
        try:
            data = response.json()
            print(f"响应格式: JSON (有效)")
            print(f"包含success字段: {'success' in data}")
            if 'success' in data:
                print(f"success值: {data['success']}")
            print(f"响应数据结构: {list(data.keys())}")
        except json.JSONDecodeError:
            print(f"响应格式: 不是有效的JSON")
            print(f"响应内容前100字符: {response.text[:100]}...")
        except Exception as e:
            print(f"解析JSON时出错: {e}")
            
    except requests.exceptions.Timeout:
        print(f"请求超时")
    except requests.exceptions.ConnectionError:
        print(f"连接错误，请确保服务器正在运行")
    except Exception as e:
        print(f"请求出错: {e}")
    
    print("-" * 60)

print("API测试完成！")