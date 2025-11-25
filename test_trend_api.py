#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试消费趋势API"""
import requests
import json

def test_trend_api():
    try:
        # 由于API需要管理员权限，我们直接调用函数获取数据
        # 创建一个模拟Flask应用上下文的环境
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app import get_consumption_trend
        from flask import Flask, session
        
        # 创建测试应用
        app = Flask(__name__)
        app.secret_key = 'test_key'
        
        # 在应用上下文中调用函数
        with app.test_request_context():
            session['user_id'] = 'admin'
            session['user_type'] = 'admin'
            response = get_consumption_trend()
            
            # 获取响应数据
            data = response.get_json()
            print("API响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            # 验证数据
            if data.get('success') == True:
                chart_data = data.get('data', {})
                labels = chart_data.get('labels', [])
                amounts = chart_data.get('data', [])
                
                print(f"\n标签数量: {len(labels)}")
                print(f"数据点数量: {len(amounts)}")
                
                # 安全地计算数据范围
                if len(amounts) > 0:
                    print(f"数据范围: 最小={min(amounts)}, 最大={max(amounts)}")
                    
                    # 检查是否有非零数据
                    if any(amount > 0 for amount in amounts):
                        print("✅ 测试成功: 图表数据包含非零值!")
                    else:
                        print("❌ 测试失败: 图表数据全为0!")
                else:
                    print("⚠️  没有返回任何数据点")
            else:
                print(f"❌ API调用失败: {data.get('error')}")
    
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_trend_api()