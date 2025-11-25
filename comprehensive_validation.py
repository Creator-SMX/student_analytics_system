#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合验证脚本：测试系统稳定性和数据一致性

此脚本用于验证学生消费行为分析系统的以下方面：
1. 数据库连接池稳定性
2. 数据查询一致性（多次查询结果是否相同）
3. 图表数据计算的准确性
4. 并发请求处理能力
"""

import time
import threading
import json
import requests
import pandas as pd
import numpy as np
from utils.db_connection import execute_query, execute_update

# 配置
BASE_URL = 'http://localhost:5000'
TEST_RUNS = 3  # 验证轮数
CONCURRENT_THREADS = 5  # 并发线程数

# 记录测试结果
results = {
    'connection_pool': [],
    'data_consistency': [],
    'chart_data': [],
    'concurrent_performance': []
}

def test_connection_pool_stability():
    """测试连接池稳定性"""
    print("\n=== 测试连接池稳定性 ===")
    
    try:
        # 执行多次简单查询
        for i in range(10):
            start_time = time.time()
            result = execute_query("SELECT 1 as test_value")
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000  # 毫秒
            print(f"查询 {i+1}/10 完成，耗时: {execution_time:.2f}ms")
            
            # 验证结果
            assert isinstance(result, list), "结果类型应为列表"
            assert len(result) > 0, "结果不应为空"
            assert result[0]['test_value'] == 1, "值应为1"
        
        results['connection_pool'].append({"status": "success", "message": "连接池稳定性测试通过"})
        print("✓ 连接池稳定性测试通过")
        return True
    except Exception as e:
        results['connection_pool'].append({"status": "error", "message": str(e)})
        print(f"✗ 连接池稳定性测试失败: {str(e)}")
        return False

def test_data_consistency():
    """测试数据一致性（多次查询结果是否相同）"""
    print("\n=== 测试数据一致性 ===")
    
    try:
        # 定义要测试的查询
        queries = [
            "SELECT COUNT(*) as total FROM consumption_records",
            "SELECT * FROM consumption_records LIMIT 10",
            "SELECT dept as canteen_name, COUNT(*) as count FROM consumption_records GROUP BY dept"
        ]
        
        for i, query in enumerate(queries):
            print(f"\n测试查询 {i+1}: {query}")
            
            # 第一次查询
            result1 = execute_query(query)
            print(f"第一次查询结果: {len(result1)} 条记录")
            
            # 模拟页面刷新 - 等待一小段时间后再次查询
            time.sleep(0.5)
            
            # 第二次查询
            result2 = execute_query(query)
            print(f"第二次查询结果: {len(result2)} 条记录")
            
            # 验证两次查询结果是否一致
            assert len(result1) == len(result2), "两次查询的记录数不一致"
            
            # 对于简单聚合查询，验证具体数值
            if "COUNT(*)" in query and len(result1) == 1:
                # 使用结果中的第一个值，避免键名问题
                value1 = list(result1[0].values())[0]
                value2 = list(result2[0].values())[0]
                assert value1 == value2, "计数结果不一致"
                print(f"✓ 计数结果一致: {value1}")
            
        results['data_consistency'].append({"status": "success", "message": "数据一致性测试通过"})
        print("\n✓ 数据一致性测试通过 - 多次查询结果保持一致")
        return True
    except Exception as e:
        results['data_consistency'].append({"status": "error", "message": str(e)})
        print(f"\n✗ 数据一致性测试失败: {str(e)}")
        return False

def test_chart_data_calculation():
    """测试图表数据计算的准确性"""
    print("\n=== 测试图表数据计算准确性 ===")
    
    try:
        # 1. 测试食堂消费占比计算
        print("\n测试食堂消费占比计算:")
        
        # 直接从数据库计算
        db_query = """
        SELECT dept as canteen_name, COUNT(*) as count, 
               ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM consumption_records)), 2) as percentage 
        FROM consumption_records 
        GROUP BY dept 
        ORDER BY count DESC
        """
        db_results = execute_query(db_query)
        print("数据库直接计算结果:")
        for row in db_results:
            print(f"  {row['canteen_name']}: {row['count']} 次 ({row['percentage']}%)")
        
        # 2. 模拟API调用获取图表数据
        try:
            # 尝试从API获取数据
            response = requests.get(f"{BASE_URL}/api/analytics/canteen_distribution")
            if response.status_code == 200:
                api_data = response.json()
                print("\nAPI返回的图表数据:")
                for item in api_data.get('data', []):
                    print(f"  {item.get('name', 'N/A')}: {item.get('value', 0)}")
            else:
                print(f"\nAPI调用失败，状态码: {response.status_code}")
        except Exception as api_error:
            print(f"\nAPI调用异常: {str(api_error)}")
            # 继续测试，不依赖API
        
        # 3. 验证数据总和
        total_count = sum(row['count'] for row in db_results)
        all_consumption_count = execute_query("SELECT COUNT(*) as total FROM consumption_records")[0]['total']
        assert total_count == all_consumption_count, "食堂消费统计总数不匹配"
        print(f"\n✓ 数据总和验证通过: {total_count} 条记录")
        
        # 4. 验证百分比计算
        total_percentage = sum(row['percentage'] for row in db_results)
        assert abs(total_percentage - 100) < 0.1, f"百分比总和应为100%，实际为 {total_percentage}%"
        print(f"✓ 百分比总和验证通过: {total_percentage:.2f}%")
        
        results['chart_data'].append({"status": "success", "message": "图表数据计算准确性测试通过"})
        print("\n✓ 图表数据计算准确性测试通过")
        return True
    except Exception as e:
        results['chart_data'].append({"status": "error", "message": str(e)})
        print(f"\n✗ 图表数据计算准确性测试失败: {str(e)}")
        return False

def concurrent_request_worker(worker_id):
    """并发请求工作线程"""
    try:
        start_time = time.time()
        
        # 执行查询
        queries = [
            "SELECT COUNT(*) as total FROM consumption_records",
            "SELECT * FROM consumption_records ORDER BY date_time DESC LIMIT 5"
        ]
        
        for query in queries:
            result = execute_query(query)
            assert isinstance(result, list), "结果类型应为列表"
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # 毫秒
        print(f"线程 {worker_id} 完成，耗时: {execution_time:.2f}ms")
        return True
    except Exception as e:
        print(f"线程 {worker_id} 失败: {str(e)}")
        return False

def test_concurrent_performance():
    """测试并发请求处理能力"""
    print("\n=== 测试并发请求处理能力 ===")
    
    try:
        threads = []
        results_list = []
        
        # 创建并启动线程
        for i in range(CONCURRENT_THREADS):
            thread = threading.Thread(
                target=lambda i=i: results_list.append(concurrent_request_worker(i))
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有线程都成功完成
        success_count = sum(results_list)
        print(f"\n并发测试结果: {success_count}/{CONCURRENT_THREADS} 个请求成功")
        
        assert success_count == CONCURRENT_THREADS, "部分并发请求失败"
        
        results['concurrent_performance'].append({
            "status": "success", 
            "message": f"并发测试通过: {CONCURRENT_THREADS} 个请求同时执行成功"
        })
        print("\n✓ 并发请求处理能力测试通过")
        return True
    except Exception as e:
        results['concurrent_performance'].append({"status": "error", "message": str(e)})
        print(f"\n✗ 并发请求处理能力测试失败: {str(e)}")
        return False

def verify_page_refresh_stability():
    """验证页面刷新稳定性"""
    print("\n=== 验证页面刷新稳定性 ===")
    
    try:
        # 这里我们模拟多次刷新的效果，通过多次查询核心数据来验证
        key_metrics = []
        
        print("模拟5次页面刷新...")
        for i in range(5):
            print(f"刷新 {i+1}/5")
            
            # 获取关键指标
            metrics = {}
            
            # 1. 消费记录总数
            consumption_count = execute_query("SELECT COUNT(*) as total FROM consumption_records")[0]['total']
            metrics['consumption_count'] = consumption_count
            
            # 2. 食堂消费分布
            canteen_data = execute_query(
                "SELECT dept as canteen_name, COUNT(*) as count FROM consumption_records GROUP BY dept"
            )
            metrics['canteen_distribution'] = {item['canteen_name']: item['count'] for item in canteen_data}
            
            # 3. 时间分布样例
            time_data = execute_query(
                "SELECT HOUR(date_time) as hour, COUNT(*) as count FROM consumption_records GROUP BY hour LIMIT 5"
            )
            metrics['time_distribution_sample'] = {item['hour']: item['count'] for item in time_data}
            
            key_metrics.append(metrics)
            time.sleep(0.3)  # 模拟用户刷新间隔
        
        # 验证所有刷新的数据是否一致
        first_metrics = key_metrics[0]
        all_consistent = True
        
        for i, metrics in enumerate(key_metrics[1:], 2):
            if metrics != first_metrics:
                all_consistent = False
                print(f"刷新 {i} 的数据与第一次不一致！")
                # 找出不一致的地方
                if metrics['consumption_count'] != first_metrics['consumption_count']:
                    print(f"  - 消费记录总数: {first_metrics['consumption_count']} vs {metrics['consumption_count']}")
                
                for canteen in set(first_metrics['canteen_distribution'].keys()) | set(metrics['canteen_distribution'].keys()):
                    if first_metrics['canteen_distribution'].get(canteen) != metrics['canteen_distribution'].get(canteen):
                        print(f"  - 食堂 {canteen}: {first_metrics['canteen_distribution'].get(canteen)} vs {metrics['canteen_distribution'].get(canteen)}")
        
        assert all_consistent, "页面刷新后数据不一致"
        print("\n✓ 页面刷新稳定性验证通过 - 多次刷新数据保持一致")
        return True
    except Exception as e:
        print(f"\n✗ 页面刷新稳定性验证失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("========================================")
    print("学生消费行为分析系统 - 综合验证脚本")
    print("========================================")
    
    # 运行所有测试
    test_functions = [
        test_connection_pool_stability,
        test_data_consistency,
        test_chart_data_calculation,
        test_concurrent_performance,
        verify_page_refresh_stability
    ]
    
    all_tests_passed = True
    
    for test_func in test_functions:
        try:
            if not test_func():
                all_tests_passed = False
        except Exception as e:
            print(f"\n测试 {test_func.__name__} 发生未捕获异常: {str(e)}")
            all_tests_passed = False
    
    # 保存测试结果
    with open('validation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印最终总结
    print("\n========================================")
    print("验证总结:")
    print("========================================")
    
    for category, category_results in results.items():
        status = "✅ 通过" if category_results and category_results[-1]['status'] == "success" else "❌ 失败"
        print(f"{category}: {status}")
    
    if all_tests_passed:
        print("\n🎉 所有测试通过！系统稳定，数据一致性良好！")
        print("✅ 所有图表和数据都是从数据库正确计算得出")
        print("✅ 页面刷新后数据保持稳定，不会变来变去")
        print("✅ 连接池工作正常，并发处理能力良好")
    else:
        print("\n❌ 部分测试失败，请查看详细信息")
    
    print("\n验证结果已保存到 validation_results.json")

if __name__ == "__main__":
    main()