#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单测试脚本，检查服务器基本功能"""
import requests
import time

def test_basic_endpoints():
    """测试基本端点"""
    endpoints = [
        ("根路径", "http://127.0.0.1:5000/"),
        ("登录页面", "http://127.0.0.1:5000/login"),
        ("API状态", "http://127.0.0.1:5000/api/status"),
    ]
    
    print("开始测试基本端点...")
    for name, url in endpoints:
        try:
            print(f"\n测试 {name}: {url}")
            response = requests.get(url, allow_redirects=False)
            print(f"状态码: {response.status_code}")
            print(f"重定向到: {response.headers.get('Location', '无')}")
            
            # 如果响应内容较小，打印部分内容
            if len(response.content) < 1000:
                print(f"响应内容前100字符: {response.text[:100]}...")
            else:
                print(f"响应内容长度: {len(response.content)} 字节")
                print(f"响应内容前100字符: {response.text[:100]}...")
                
        except Exception as e:
            print(f"测试 {name} 时出错: {str(e)}")
    
    print("\n基本端点测试完成")
    
    # 测试analytics蓝图中的一些端点
    print("\n" + "="*50)
    print("测试analytics蓝图端点...")
    
    analytics_endpoints = [
        ("Analytics仪表板", "http://127.0.0.1:5000/analytics/"),
        ("消费行为聚类API", "http://127.0.0.1:5000/api/get_cluster"),
    ]
    
    for name, url in analytics_endpoints:
        try:
            print(f"\n测试 {name}: {url}")
            response = requests.get(url, allow_redirects=False)
            print(f"状态码: {response.status_code}")
            print(f"重定向到: {response.headers.get('Location', '无')}")
        except Exception as e:
            print(f"测试 {name} 时出错: {str(e)}")

if __name__ == "__main__":
    test_basic_endpoints()