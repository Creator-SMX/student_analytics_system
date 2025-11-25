#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试门禁记录API"""
import requests
import json
import datetime

def test_access_records_api():
    """测试门禁记录API"""
    base_url = "http://localhost:5000"
    endpoint = "/api/access-records"
    
    print(f"开始测试门禁记录API: {base_url}{endpoint}")
    
    # 测试1: 无参数请求
    print("\n=== 测试1: 无参数请求 ===")
    try:
        response = requests.get(f"{base_url}{endpoint}")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        data = response.json()
        print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        if 'data' in data and 'records' in data['data']:
            print(f"返回记录数: {len(data['data']['records'])}")
    except Exception as e:
        print(f"请求失败: {str(e)}")
    
    # 测试2: 限制返回少量记录
    print("\n=== 测试2: 限制返回5条记录 ===")
    try:
        params = {'page': 1, 'per_page': 5}
        response = requests.get(f"{base_url}{endpoint}", params=params)
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        if 'data' in data and 'records' in data['data']:
            print(f"返回记录数: {len(data['data']['records'])}")
    except Exception as e:
        print(f"请求失败: {str(e)}")
    
    # 测试3: 测试特定门禁卡号查询
    print("\n=== 测试3: 查询特定门禁卡号 ===")
    try:
        params = {'access_card_no': '25558880', 'page': 1, 'per_page': 10}
        response = requests.get(f"{base_url}{endpoint}", params=params)
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        if 'data' in data and 'records' in data['data']:
            print(f"返回记录数: {len(data['data']['records'])}")
    except Exception as e:
        print(f"请求失败: {str(e)}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_access_records_api()