#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
详细验证API响应的测试脚本
用于直接检查get_cluster API的响应数据，验证是否返回正确的总消费人数
"""

import os
import sys
import json
from analytics.analytics_controller import get_cluster
from flask import Flask, jsonify, make_response

# 创建一个最小化的Flask应用用于测试
app = Flask(__name__)
app.config['TESTING'] = True


def test_get_cluster_function():
    """直接测试get_cluster函数，不通过HTTP请求"""
    print("\n===== 直接测试get_cluster函数 =====")
    
    # 模拟Flask上下文，因为get_cluster函数使用了Flask的装饰器
    with app.test_request_context('/analytics/api/get_cluster'):
        try:
            # 直接调用函数获取结果
            response = get_cluster()
            
            # 检查响应类型
            if isinstance(response, tuple):
                data, status_code = response
                print(f"状态码: {status_code}")
            else:
                data = response.json if hasattr(response, 'json') else response
                
            # 打印结果
            print(f"总消费人数: {data.get('total_consumers', 'N/A')}")
            print(f"各类别人数: {data.get('counts', 'N/A')}")
            print(f"类别标签: {data.get('labels', 'N/A')}")
            print(f"各类别百分比: {data.get('percentages', 'N/A')}")
            
            # 验证各类别人数之和是否等于总消费人数
            counts = data.get('counts', [])
            total_consumers = data.get('total_consumers', 0)
            sum_counts = sum(counts)
            print(f"\n数据一致性验证:")
            print(f"各类别人数总和: {sum_counts}")
            print(f"总消费人数: {total_consumers}")
            print(f"一致性: {'✅ 通过' if sum_counts == total_consumers else '❌ 失败'}")
            
        except Exception as e:
            print(f"测试失败: {str(e)}")
            import traceback
            traceback.print_exc()


def verify_sql_query():
    """直接验证SQL查询，确认数据来源"""
    print("\n===== 验证SQL查询结果 =====")
    
    from sqlalchemy import text
    from analytics.analytics_controller import db_conn
    
    try:
        # 连接数据库
        conn = db_conn.connect()
        if not conn:
            print("数据库连接失败")
            return
        
        # 执行与get_cluster相同的SQL查询
        sql = """
        SELECT card_no, SUM(money) as total_money 
        FROM consumption_records 
        GROUP BY card_no
        """
        
        print(f"执行SQL: {sql.strip()}")
        results = conn.execute(text(sql)).fetchall()
        print(f"查询返回记录数: {len(results)}")
        
        # 关闭连接
        db_conn.disconnect()
        
    except Exception as e:
        print(f"SQL验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
    # 同时验证带过滤条件的查询（之前的版本）
    try:
        # 连接数据库
        conn = db_conn.connect()
        if not conn:
            print("数据库连接失败")
            return
        
        # 执行之前的带过滤条件的SQL查询
        old_sql = """
        SELECT card_no, SUM(money) as total_money 
        FROM consumption_records 
        WHERE money > 0 
        GROUP BY card_no 
        HAVING total_money > 0
        """
        
        print(f"\n执行旧版SQL（带过滤条件）: {old_sql.strip()}")
        old_results = conn.execute(text(old_sql)).fetchall()
        print(f"旧版查询返回记录数: {len(old_results)}")
        
        # 关闭连接
        db_conn.disconnect()
        
    except Exception as e:
        print(f"旧版SQL验证失败: {str(e)}")
        import traceback
        traceback.print_exc()


def check_file_changes():
    """检查文件修改是否已正确保存"""
    print("\n===== 检查文件修改状态 =====")
    
    file_path = "d:\\Pycharm\\PcData\\student_analytics_system\\analytics\\analytics_controller.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查SQL查询是否包含过滤条件
            if "WHERE money > 0" in content and "HAVING total_money > 0" in content:
                print("❌ 警告: 文件中仍存在过滤条件")
            else:
                print("✅ 文件中已移除过滤条件")
                
            # 检查是否包含新的SQL查询
            if "SELECT card_no, SUM(money) as total_money FROM consumption_records GROUP BY card_no" in content.replace('\n', ' '):
                print("✅ 文件中包含正确的SQL查询")
            else:
                print("❌ 警告: 文件中未找到正确的SQL查询")
                
    except Exception as e:
        print(f"检查文件失败: {str(e)}")


def check_flask_caching():
    """检查Flask缓存设置"""
    print("\n===== 检查Flask缓存设置 =====")
    
    # 检查app.py中的缓存相关配置
    app_path = "d:\\Pycharm\\PcData\\student_analytics_system\\app.py"
    
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查是否有缓存相关的导入或配置
            cache_keywords = ['cache', 'CACHE', 'flask_caching', 'Flask-Caching', 'SimpleCache']
            has_cache = any(keyword in content for keyword in cache_keywords)
            
            if has_cache:
                print("⚠️  发现可能的缓存配置")
                for keyword in cache_keywords:
                    if keyword in content:
                        print(f"   - 包含关键词: {keyword}")
            else:
                print("✅ 未发现明显的缓存配置")
                
    except Exception as e:
        print(f"检查Flask缓存失败: {str(e)}")


def main():
    """主测试函数"""
    print("开始验证API响应测试...")
    
    # 检查文件修改状态
    check_file_changes()
    
    # 检查Flask缓存设置
    check_flask_caching()
    
    # 直接验证SQL查询结果
    verify_sql_query()
    
    # 测试get_cluster函数
    test_get_cluster_function()
    
    print("\n===== 测试完成 =====")


if __name__ == "__main__":
    main()