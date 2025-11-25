#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直接测试get_cluster函数的返回值"""

import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from flask import Flask
from analytics.analytics_controller import get_cluster

# 创建Flask应用
app = Flask(__name__)
app.config['TESTING'] = True

# 添加蓝图（如果需要）
from analytics.analytics_controller import analytics_bp
app.register_blueprint(analytics_bp, url_prefix='/analytics')

def test_cluster_function():
    """直接调用get_cluster函数测试"""
    print("开始直接测试get_cluster函数...")
    
    try:
        # 使用Flask测试上下文
        with app.test_request_context():
            # 调用函数
            response = get_cluster()
            
            # 获取响应数据
            if hasattr(response, 'get_data'):
                data = json.loads(response.get_data(as_text=True))
                print("\n函数返回数据:")
                print(f"总消费人数(total_consumers): {data.get('total_consumers', '未找到')}")
                print(f"各类别人数(counts): {data.get('counts', '未找到')}")
                print(f"类别标签(labels): {data.get('labels', '未找到')}")
                print(f"百分比(percentages): {data.get('percentages', '未找到')}")
                
                # 检查total_consumers是否为0
                if data.get('total_consumers', 0) == 0:
                    print("\n警告: total_consumers为0，请检查数据库查询逻辑")
                
                # 验证各类别人数之和
                if 'counts' in data:
                    total_counts = sum(data['counts'])
                    print(f"\n各类别人数之和: {total_counts}")
                    if 'total_consumers' in data:
                        print(f"是否与total_consumers一致: {total_counts == data['total_consumers']}")
            else:
                print("无法获取响应数据")
                
    except Exception as e:
        print(f"测试出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cluster_function()