#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试get_cluster函数返回的总人数数据"""

import os
import sys
import requests
import json

# 确保中文显示正常
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_cluster_api():
    """测试聚类API返回的数据，特别是total_consumers字段"""
    print("开始测试聚类API...")
    
    # API端点URL
    url = "http://127.0.0.1:5000/analytics/api/get_cluster"
    
    try:
        # 发送GET请求
        print(f"正在请求: {url}")
        response = requests.get(url, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            data = response.json()
            print("\nAPI返回数据:")
            print(f"总消费人数(total_consumers): {data.get('total_consumers', '未找到')}")
            print(f"各类别人数(counts): {data.get('counts', '未找到')}")
            print(f"类别标签(labels): {data.get('labels', '未找到')}")
            print(f"百分比(percentages): {data.get('percentages', '未找到')}")
            
            # 验证各类别人数之和
            if 'counts' in data:
                total_counts = sum(data['counts'])
                print(f"\n各类别人数之和: {total_counts}")
                if 'total_consumers' in data:
                    print(f"是否与total_consumers一致: {total_counts == data['total_consumers']}")
            
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"请求出错: {str(e)}")
        print("请确保Flask服务器正在运行在http://127.0.0.1:5000")

if __name__ == "__main__":
    test_cluster_api()