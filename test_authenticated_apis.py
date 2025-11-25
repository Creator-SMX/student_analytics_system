#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""带认证的API端点测试"""
import requests
import json

def test_authenticated_apis():
    print("=== 带认证的API端点测试 ===\n")
    
    base_url = 'http://localhost:5000'
    
    # 1. 首先登录获取会话Cookie
    print("🔐 正在登录系统...")
    login_url = f'{base_url}/auth/login'
    login_data = {
        'username': 'admin',
        'password': '123456',
        'user_type': 'admin'
    }
    
    try:
        # 使用POST方法登录，设置正确的Content-Type
        headers = {'Content-Type': 'application/json'}
        login_response = requests.post(login_url, json=login_data, headers=headers, allow_redirects=True)
        
        if login_response.status_code == 200 or login_response.status_code == 302:
            print("✅ 登录成功!")
            cookies = login_response.cookies
            print(f"📋 获得的Cookie: {dict(cookies)}")
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"响应内容: {login_response.text[:500]}...")
            return
    except Exception as e:
        print(f"❌ 登录过程出错: {str(e)}")
        return
    
    # 2. 测试analytics仪表板页面
    print("\n" + "="*50)
    print("📊 测试 Analytics仪表板")
    try:
        dashboard_url = f'{base_url}/analytics/'
        dashboard_response = requests.get(dashboard_url, cookies=cookies)
        print(f"状态码: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("✅ 仪表板访问成功")
            print(f"响应内容长度: {len(dashboard_response.text)} 字节")
            # 检查是否包含报告相关内容
            if '报告' in dashboard_response.text:
                print("✅ 仪表板包含报告内容")
        else:
            print(f"❌ 仪表板访问失败: {dashboard_response.status_code}")
            print(f"响应内容前200字符: {dashboard_response.text[:200]}...")
    except Exception as e:
        print(f"❌ 仪表板访问出错: {str(e)}")
    
    # 3. 测试消费行为聚类API
    print("\n" + "="*50)
    print("🔍 测试 消费行为聚类API")
    try:
        cluster_url = f'{base_url}/analytics/api/get_cluster'
        print(f"访问URL: {cluster_url}")
        cluster_response = requests.get(cluster_url, cookies=cookies)
        print(f"状态码: {cluster_response.status_code}")
        
        if cluster_response.status_code == 200:
            print("✅ API访问成功")
            try:
                data = cluster_response.json()
                print(f"返回数据类型: {type(data).__name__}")
                print(f"数据键: {list(data.keys())}")
                
                # 显示数据内容
                print("\n📊 数据内容:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
                    
                # 检查是否有有效的聚类数据
                if 'labels' in data and 'counts' in data:
                    print(f"\n🎯 聚类数量: {len(data['labels'])}")
                    print(f"👥 总消费者数: {data.get('total_consumers', 0)}")
                    
                    # 计算总数检查
                    total_count = sum(data['counts']) if isinstance(data['counts'], list) else 0
                    print(f"🔢 计算的总数: {total_count}")
                    
                    if total_count > 0:
                        print("✅ 成功获取到实际的聚类数据")
                    else:
                        print("⚠️  聚类数据计数为零，可能存在问题")
                else:
                    print("❌ 聚类数据不完整")
            except json.JSONDecodeError:
                print(f"❌ JSON解析失败，响应内容: {cluster_response.text[:200]}...")
        else:
            print(f"❌ API访问失败: {cluster_response.status_code}")
            print(f"响应内容: {cluster_response.text[:200]}...")
    except Exception as e:
        print(f"❌ API访问出错: {str(e)}")
    
    # 4. 测试其他关键API端点
    print("\n" + "="*50)
    print("🚀 测试其他关键API端点")
    
    other_endpoints = [
        '/analytics/api/get_overview',
        '/analytics/api/get_time_analysis',
        '/analytics/api/get_canteen_analysis'
    ]
    
    for endpoint in other_endpoints:
        url = f'{base_url}{endpoint}'
        print(f"\n测试 {endpoint}:")
        try:
            response = requests.get(url, cookies=cookies)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("  ✅ 访问成功")
            else:
                print(f"  ❌ 访问失败")
        except Exception as e:
            print(f"  ⚠️  异常: {str(e)}")
    
    print("\n" + "="*50)
    print("🎉 测试完成!")

if __name__ == '__main__':
    test_authenticated_apis()