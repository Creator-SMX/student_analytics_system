#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试API修复是否成功"""
import requests
import json

# API测试函数
def test_api_endpoints():
    print("开始测试API修复效果...\n")
    
    # 测试门禁模式API
    print("1. 测试门禁模式API (/analytics/api/get_access_pattern):")
    try:
        response = requests.get('http://localhost:5000/analytics/api/get_access_pattern')
        response_data = response.json()
        print(f"   响应状态码: {response.status_code}")
        print(f"   响应结构: {list(response_data.keys())}")
        print(f"   success字段: {response_data.get('success')}")
        print(f"   数据长度 - hours: {len(response_data.get('hours', []))}")
        print(f"   数据长度 - counts: {len(response_data.get('counts', []))}")
        print(f"   前5条数据: {list(zip(response_data.get('hours', [])[:5], response_data.get('counts', [])[:5]))}")
    except Exception as e:
        print(f"   测试失败: {str(e)}")
    print()
    
    # 测试概览数据API
    print("2. 测试概览数据API (/analytics/api/get_overview):")
    try:
        response = requests.get('http://localhost:5000/analytics/api/get_overview')
        response_data = response.json()
        print(f"   响应状态码: {response.status_code}")
        print(f"   响应结构: {list(response_data.keys())}")
        print(f"   success字段: {response_data.get('success')}")
        print(f"   学生总数: {response_data.get('student_count')}")
        print(f"   总交易金额: {response_data.get('total_amount')}")
        print(f"   平均消费: {response_data.get('avg_consumption')}")
        print(f"   交易笔数: {response_data.get('transaction_count')}")
        print(f"   消费地点数: {response_data.get('location_count')}")
        print(f"   男生人数: {response_data.get('male_count')}")
        print(f"   女生人数: {response_data.get('female_count')}")
    except Exception as e:
        print(f"   测试失败: {str(e)}")
    print()
    
    # 打印修复总结
    print("修复总结:")
    print("1. 门禁模式API问题 - 已修复前端重复调用API导致的数据处理混乱")
    print("2. 总交易金额和平均消费显示为0问题 - 已修复前端字段名不匹配问题")
    print("   - 从 d.total_money 改为 d.total_amount")
    print("   - 从 d.avg_money 改为 d.avg_consumption")
    print()
    print("请确保服务器正在运行，并访问前端页面验证数据显示是否正常。")

if __name__ == "__main__":
    test_api_endpoints()