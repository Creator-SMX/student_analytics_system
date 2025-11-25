#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# 设置请求URL和会话
BASE_URL = 'http://127.0.0.1:5000'

# 创建一个会话来保持cookie
session = requests.Session()

# 先登录获取会话
login_data = {
    'username': 'admin',  # 假设的管理员用户名
    'password': 'admin123'  # 假设的管理员密码
}

print("正在登录...")
login_response = session.post(f"{BASE_URL}/login", data=login_data)
print(f"登录状态码: {login_response.status_code}")

# 测试获取食堂分析数据的API
print("\n测试 /analytics/api/get_canteen_analysis API...")
try:
    response = session.get(f"{BASE_URL}/analytics/api/get_canteen_analysis")
    print(f"API响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        # 尝试解析JSON
        try:
            data = response.json()
            print("\nAPI返回数据:")
            print(f"位置列表: {data.get('locations', [])}")
            print(f"计数列表: {data.get('counts', [])}")
            print(f"金额列表: {data.get('amounts', [])}")
            print(f"百分比列表: {data.get('percentages', [])}")
            
            # 打印详细的食堂消费数据
            print("\n详细食堂消费数据:")
            if 'locations' in data and 'counts' in data and 'percentages' in data:
                for i, (loc, cnt, pct) in enumerate(zip(data['locations'], data['counts'], data['percentages'])):
                    print(f"{i+1}. {loc}: {cnt}人次 ({pct}%)")
            
        except json.JSONDecodeError:
            print("错误: 返回的不是有效的JSON格式")
            print(f"响应内容: {response.text[:500]}...")
    else:
        print(f"错误: API调用失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}...")
        
        # 检查是否需要登录
        if "login" in response.text.lower() or response.status_code == 401:
            print("可能需要登录，请检查用户名和密码是否正确")
            
        # 检查是否有错误信息
        try:
            error_data = response.json()
            print(f"错误信息: {error_data.get('message', '无详细错误信息')}")
        except:
            pass
            
except Exception as e:
    print(f"请求过程中出错: {str(e)}")

# 测试兼容的旧版API端点
print("\n测试 /api/get_canteen_data API...")
try:
    response = session.get(f"{BASE_URL}/api/get_canteen_data")
    print(f"旧版API响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"旧版API返回数据长度: locations={len(data.get('locations', []))}个")
        except:
            print("旧版API返回的不是有效的JSON")
except Exception as e:
    print(f"请求旧版API时出错: {str(e)}")