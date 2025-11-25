#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证前端UI显示的聚类数据是否正确
此脚本将模拟API调用并验证返回的数据，
同时提供清除浏览器缓存的方法建议
"""

import requests
import json
import time
import os

def test_api_endpoint():
    """测试API端点返回的数据"""
    print("=== 测试API端点 ===")
    try:
        # 发送带有缓存控制头的请求，确保获取最新数据
        headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        response = requests.get('http://localhost:5000/analytics/api/get_cluster', headers=headers)
        response.raise_for_status()  # 如果状态码不是200，抛出异常
        
        data = response.json()
        print(f"API响应状态: {'成功' if data.get('status') == 'success' else data.get('status')}")
        print(f"总消费人数: {data.get('total_consumers')}")
        print(f"各类别人数: {data.get('counts')}")
        print(f"各类别标签: {data.get('labels')}")
        print(f"各类别百分比: {data.get('percentages')}")
        
        # 验证数据是否符合预期
        expected_total = 8636
        actual_total = data.get('total_consumers', 0)
        
        if actual_total == expected_total:
            print("✅ API返回的总人数正确！")
            return True, data
        else:
            print(f"❌ API返回的总人数不正确！期望: {expected_total}, 实际: {actual_total}")
            return False, data
    except Exception as e:
        print(f"测试API端点时出错: {str(e)}")
        return False, None

def check_data_consistency(data):
    """检查数据一致性"""
    if not data:
        return False
    
    print("\n=== 检查数据一致性 ===")
    counts = data.get('counts', [])
    total = data.get('total_consumers', 0)
    
    # 计算计数总和
    sum_counts = sum(counts)
    print(f"各类别计数总和: {sum_counts}")
    print(f"报告的总人数: {total}")
    
    if sum_counts == total:
        print("✅ 数据一致性检查通过！")
        return True
    else:
        print(f"❌ 数据不一致！计数总和与报告的总人数不匹配")
        return False

def main():
    print("学生消费行为聚类数据验证工具")
    print("=" * 50)
    
    # 测试API端点
    api_success, data = test_api_endpoint()
    
    if api_success:
        # 检查数据一致性
        check_data_consistency(data)
        
        print("\n=== 问题分析与解决方案 ===")
        print("1. API返回的数据是正确的，总人数为8636人")
        print("2. 如果前端仍然显示旧数据(8581人)，这很可能是浏览器缓存导致的")
        print("\n清除浏览器缓存的方法:")
        print("- Chrome/Edge: 按下 Ctrl+Shift+R 进行强制刷新")
        print("- Firefox: 按下 Ctrl+Shift+R 或 Ctrl+F5 进行强制刷新")
        print("- Safari: 按下 Command+Option+R 进行强制刷新")
        print("\n或者，您可以尝试:")
        print("- 清除浏览器的缓存和Cookie")
        print("- 使用隐私模式打开页面")
        print("- 重启浏览器后再次访问")
        print("\n如果问题仍然存在，请检查:")
        print("- 前端JavaScript代码中是否有硬编码的总人数值")
        print("- 前端是否使用了本地存储(localStorage)缓存数据")
    
    print("\n=== 验证完成 ===")

if __name__ == "__main__":
    main()