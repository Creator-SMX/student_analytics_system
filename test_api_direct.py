#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直接在Flask应用中测试API端点，绕过认证"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analytics.analytics_controller import get_cluster, get_gender_analysis, get_major_analysis
from flask import Flask, request
from werkzeug.test import Client
from werkzeug.wrappers import Response

# 创建一个简单的Flask应用用于测试
app = Flask(__name__)

# 注册我们要测试的函数为路由，绕过认证
app.route('/test_get_cluster')(get_cluster)
app.route('/test_get_gender_analysis')(get_gender_analysis)
app.route('/test_get_major_analysis')(get_major_analysis)

def test_api_functions():
    """测试API函数"""
    print("开始测试API函数...")
    
    client = Client(app)
    
    # 测试get_cluster函数
    print("\n" + "-" * 50)
    print("测试 get_cluster 函数")
    try:
        response = client.get('/test_get_cluster')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"返回数据类型: {type(data).__name__}")
            if isinstance(data, dict):
                print(f"数据键: {list(data.keys())}")
                print("数据内容:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
    except Exception as e:
        print(f"测试 get_cluster 时出错: {str(e)}")
    
    # 测试get_gender_analysis函数
    print("\n" + "-" * 50)
    print("测试 get_gender_analysis 函数")
    try:
        response = client.get('/test_get_gender_analysis')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"返回数据类型: {type(data).__name__}")
            if isinstance(data, dict):
                print(f"数据键: {list(data.keys())}")
                print("数据内容:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
    except Exception as e:
        print(f"测试 get_gender_analysis 时出错: {str(e)}")
    
    # 测试get_major_analysis函数
    print("\n" + "-" * 50)
    print("测试 get_major_analysis 函数")
    try:
        response = client.get('/test_get_major_analysis')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"返回数据类型: {type(data).__name__}")
            if isinstance(data, dict):
                print(f"数据键: {list(data.keys())}")
                print("数据内容:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
    except Exception as e:
        print(f"测试 get_major_analysis 时出错: {str(e)}")

if __name__ == "__main__":
    test_api_functions()