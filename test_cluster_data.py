#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试get_cluster函数的数据是否正确
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入Flask应用和相关模块
from analytics.analytics_controller import analytics_bp, get_cluster
from flask import Flask, jsonify

# 创建一个简单的Flask应用来测试
test_app = Flask(__name__)
test_app.register_blueprint(analytics_bp, url_prefix='/analytics')

def test_get_cluster_data():
    """直接调用get_cluster函数测试返回的数据"""
    print("=== 测试get_cluster函数返回的数据 ===")
    
    try:
        # 使用Flask测试上下文
        with test_app.test_request_context():
            # 调用函数获取响应
            response = get_cluster()
            
            # 获取JSON数据
            data = json.loads(response.get_data(as_text=True))
            
            print("\n函数返回的数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 验证数据完整性
            total_consumers = data.get('total_consumers', 0)
            counts = data.get('counts', [])
            labels = data.get('labels', [])
            percentages = data.get('percentages', [])
            thresholds = data.get('thresholds', {})
            
            # 验证总和
            cluster_sum = sum(counts)
            print(f"\n验证信息:")
            print(f"总消费人数: {total_consumers}")
            print(f"聚类总和: {cluster_sum}")
            print(f"差异: {total_consumers - cluster_sum}")
            print(f"聚类标签: {labels}")
            print(f"聚类人数: {counts}")
            print(f"聚类百分比: {percentages}")
            print(f"阈值信息: {thresholds}")
            
            # 验证阈值顺序是否正确
            expected_labels = ['节约型', '极简型', '普通型', '活跃型', '土豪型']
            if labels == expected_labels:
                print("\n✅ 聚类标签顺序正确!")
            else:
                print(f"\n❌ 聚类标签顺序不正确!")
                print(f"预期: {expected_labels}")
                print(f"实际: {labels}")
            
            # 验证百分比计算是否合理
            sum_percentages = sum(percentages)
            if abs(sum_percentages - 100) < 0.1:  # 允许小的浮点误差
                print(f"✅ 百分比总和合理: {sum_percentages:.1f}%")
            else:
                print(f"❌ 百分比总和不合理: {sum_percentages:.1f}%")
            
            return True
            
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_threshold_standards():
    """验证是否使用了正确的阈值标准"""
    print("\n=== 验证阈值标准 ===")
    
    # 正确的阈值标准
    correct_thresholds = {
        "节约型": "< 122.90 元",
        "极简型": "122.90 - 196.65 元",
        "普通型": "196.65 - 294.97 元",
        "活跃型": "294.97 - 491.62 元",
        "土豪型": "≥ 491.62 元"
    }
    
    try:
        # 使用Flask测试上下文
        with test_app.test_request_context():
            response = get_cluster()
            data = json.loads(response.get_data(as_text=True))
            thresholds = data.get('thresholds', {})
            
            # 验证每个阈值
            all_correct = True
            for label, correct_threshold in correct_thresholds.items():
                actual_threshold = thresholds.get(label, "")
                if actual_threshold == correct_threshold:
                    print(f"✅ {label} 阈值正确: {actual_threshold}")
                else:
                    print(f"❌ {label} 阈值错误!")
                    print(f"  预期: {correct_threshold}")
                    print(f"  实际: {actual_threshold}")
                    all_correct = False
            
            return all_correct
            
    except Exception as e:
        print(f"验证过程中出错: {str(e)}")
        return False

def main():
    print("开始测试get_cluster函数的数据正确性...")
    print("====================================")
    
    # 测试1: 数据完整性和正确性
    data_test_result = test_get_cluster_data()
    
    # 测试2: 阈值标准验证
    threshold_test_result = verify_threshold_standards()
    
    print("\n====================================")
    print("测试结果总结:")
    print(f"数据完整性测试: {'通过' if data_test_result else '失败'}")
    print(f"阈值标准测试: {'通过' if threshold_test_result else '失败'}")
    
    if data_test_result and threshold_test_result:
        print("\n🎉 所有测试通过! get_cluster函数返回的数据符合要求。")
        return 0
    else:
        print("\n❌ 测试失败，请检查数据和阈值设置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())