#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试API端点是否从数据库动态获取数据"""
import requests
import json
import time

def test_api_endpoint(endpoint, expected_keys=None):
    """测试API端点并验证返回数据格式"""
    try:
        url = f"http://127.0.0.1:5000{endpoint}"
        print(f"\n测试API端点: {url}")
        response = requests.get(url)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据类型: {type(data).__name__}")
            
            # 打印数据摘要
            if isinstance(data, dict):
                print(f"数据键: {list(data.keys())}")
                # 验证预期的键是否存在
                if expected_keys:
                    missing_keys = [key for key in expected_keys if key not in data]
                    if missing_keys:
                        print(f"警告: 缺少预期的键: {missing_keys}")
                    else:
                        print("✓ 所有预期的键都存在")
                # 打印部分数据内容
                for key, value in list(data.items())[:3]:  # 只打印前3个键值对
                    if isinstance(value, (list, dict)):
                        print(f"  {key}: {type(value).__name__} 长度={len(value)}")
                    else:
                        print(f"  {key}: {value}")
            elif isinstance(data, list):
                print(f"数据长度: {len(data)}")
                # 打印前2个元素作为示例
                for i, item in enumerate(data[:2]):
                    print(f"  第{i+1}个元素: {item}")
            
            return True, data
        else:
            print(f"错误: API返回状态码 {response.status_code}")
            return False, None
    except Exception as e:
        print(f"测试API端点时出错: {str(e)}")
        return False, None

def main():
    """测试所有API端点"""
    print("=" * 80)
    print("开始测试API端点是否从数据库动态获取数据")
    print("=" * 80)
    
    # 测试get_cluster API
    print("\n" + "-" * 50)
    print("测试消费行为聚类API")
    success, data = test_api_endpoint(
        "/api/get_cluster", 
        expected_keys=["counts", "labels", "percentages", "total_consumers"]
    )
    
    if success and data:
        # 验证聚类数据是否合理
        labels = data.get("labels", [])
        counts = data.get("counts", [])
        percentages = data.get("percentages", [])
        total_consumers = data.get("total_consumers", 0)
        
        print(f"\n聚类数据验证:")
        print(f"总消费人数: {total_consumers}")
        print(f"聚类数量: {len(labels)}")
        
        # 打印每个聚类的详细信息
        for i, (label, count, percentage) in enumerate(zip(labels, counts, percentages)):
            print(f"  {i+1}. {label}: {count}人 ({percentage}%)")
        
        # 验证百分比总和是否接近100%
        sum_percentages = sum(percentages)
        print(f"\n百分比总和: {sum_percentages:.1f}%")
        if 99.0 <= sum_percentages <= 101.0:  # 允许1%的误差
            print("✓ 百分比计算合理")
        else:
            print("⚠ 百分比总和可能计算有误")
    
    # 测试get_gender_analysis API
    print("\n" + "-" * 50)
    print("测试性别分析API")
    success, data = test_api_endpoint("/get_gender_analysis")
    
    # 测试get_major_analysis API
    print("\n" + "-" * 50)
    print("测试专业分析API")
    success, data = test_api_endpoint("/get_major_analysis")
    
    # 测试其他主要API端点
    print("\n" + "-" * 50)
    print("测试核心数据概览API")
    success, data = test_api_endpoint("/analytics/api/get_overview")
    
    print("\n" + "-" * 50)
    print("测试消费时段分析API")
    success, data = test_api_endpoint("/analytics/api/get_time_analysis")
    
    print("\n" + "-" * 50)
    print("测试门禁行为模式API")
    success, data = test_api_endpoint("/analytics/api/get_access_pattern")
    
    print("\n" + "-" * 50)
    print("测试食堂消费分析API")
    success, data = test_api_endpoint("/analytics/api/get_canteen_analysis")
    
    print("\n" + "=" * 80)
    print("API端点测试完成")
    print("=" * 80)

if __name__ == "__main__":
    main()