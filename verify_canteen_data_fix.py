#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证食堂数据修复脚本
用于检查修复后的API是否返回了正确的数据库数据
"""

import sys
import os
import json
import requests
import pandas as pd
from sqlalchemy import text, create_engine

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从项目导入数据库连接信息
try:
    from analytics.analytics_controller import get_db_engine
    db_engine = get_db_engine()
except ImportError:
    # 如果导入失败，使用直接连接方式
    print("无法导入数据库连接，使用直接连接...")
    
    def connect_db():
        """直接连接数据库"""
        try:
            # 数据库连接配置（从analytics_controller.py中提取）
            db_config = {
                'user': 'root',
                'password': '123456',  # 注意：实际应用中不应硬编码密码
                'host': 'localhost',
                'port': 3306,
                'database': 'student_analytics_system'
            }
            
            engine = create_engine(
                f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
            return engine
        except Exception as e:
            print(f"数据库连接失败: {str(e)}")
            return None
    
    db_engine = connect_db()

def verify_db_data():
    """直接从数据库获取数据进行验证"""
    print("\n===== 从数据库直接获取食堂消费数据 =====")
    try:
        if not db_engine:
            print("数据库引擎不可用")
            return None
        
        with db_engine.connect() as conn:
            sql = "SELECT dept, COUNT(*) as count, ROUND(SUM(money),2) as amount FROM consumption_records WHERE dept LIKE '%食堂%' GROUP BY dept ORDER BY count DESC"
            results = conn.execute(text(sql)).fetchall()
            
            # 转换为DataFrame便于显示
            df = pd.DataFrame(results)
            if not df.empty:
                print("\n数据库中的食堂消费数据:")
                print(df)
                
                # 计算总人次
                total_count = df['count'].sum()
                print(f"\n总消费人次: {total_count}")
                
                # 转换为API返回格式
                db_data = {
                    "locations": df['dept'].tolist(),
                    "counts": df['count'].tolist(),
                    "amounts": df['amount'].astype(float).tolist(),
                    "percentages": [(count/total_count*100).round(1) for count in df['count'].tolist()]
                }
                
                return db_data
            else:
                print("数据库中没有找到食堂数据")
                return None
    except Exception as e:
        print(f"查询数据库失败: {str(e)}")
        return None

def verify_api_data():
    """验证API端点是否返回正确数据"""
    print("\n===== 验证修复后的API端点 =====")
    
    # 测试的API端点列表
    api_endpoints = [
        ("/analytics/api/get_canteen_analysis", "直接获取食堂分析API"),
        ("/api/get_canteen_data", "兼容旧版API"),
        ("/analytics/api/get_consumption_query", "前端report.html使用的API")
    ]
    
    # 假设API在本地运行
    base_url = "http://localhost:5000"
    
    results = {}
    
    for endpoint, description in api_endpoints:
        full_url = base_url + endpoint
        print(f"\n测试 {description}: {full_url}")
        try:
            # 注意：实际测试可能需要添加认证信息
            # response = requests.get(full_url, headers={'Authorization': 'Bearer token'})
            response = requests.get(full_url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"API返回状态: 成功")
                
                # 显示关键信息
                if 'locations' in data:
                    print(f"食堂数量: {len(data['locations'])}")
                    if 'counts' in data:
                        total_count = sum(data['counts'])
                        print(f"总消费人次: {total_count}")
                        # 显示前3个食堂的数据
                        for i in range(min(3, len(data['locations']))):
                            print(f"  - {data['locations'][i]}: {data['counts'][i]}人次 ({data['percentages'][i]}%)")
                elif 'counts' in data:
                    print(f"返回数据格式: counts列表")
                    print(f"食堂数量: {len(data['counts'])}")
                    if data['counts']:
                        print(f"前3个食堂的数据:")
                        for i in range(min(3, len(data['counts']))):
                            print(f"  - {data['counts'][i]['location']}: {data['counts'][i]['count']}人次")
                
                results[endpoint] = {
                    'status': 'success',
                    'data': data
                }
            else:
                print(f"API返回状态: 失败 (状态码: {response.status_code})")
                print(f"响应内容: {response.text}")
                results[endpoint] = {
                    'status': 'error',
                    'code': response.status_code
                }
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {str(e)}")
            results[endpoint] = {
                'status': 'error',
                'message': str(e)
            }
    
    return results

def compare_data(db_data, api_results):
    """比较数据库数据和API返回的数据"""
    if not db_data or not api_results:
        print("\n无法进行数据比较，数据不完整")
        return
    
    print("\n===== 数据一致性比较 =====")
    
    # 检查主要API端点（get_canteen_analysis_api）
    main_api = "/analytics/api/get_canteen_analysis"
    if main_api in api_results and api_results[main_api]['status'] == 'success':
        api_data = api_results[main_api]['data']
        
        # 比较总人次
        db_total = sum(db_data['counts'])
        api_total = sum(api_data['counts'])
        
        print(f"数据库总人次: {db_total}")
        print(f"API返回总人次: {api_total}")
        
        if abs(db_total - api_total) < 0.001:  # 考虑浮点数精度问题
            print("✓ 总人次数据一致")
        else:
            print(f"✗ 总人次数据不一致! 差异: {db_total - api_total}")
        
        # 比较食堂数量
        if len(db_data['locations']) == len(api_data['locations']):
            print("✓ 食堂数量一致")
        else:
            print(f"✗ 食堂数量不一致! 数据库: {len(db_data['locations'])}, API: {len(api_data['locations'])}")
        
        # 比较前几个食堂的数据
        print("\n前3个食堂数据比较:")
        for i in range(min(3, len(db_data['locations']), len(api_data['locations']))):
            db_name = db_data['locations'][i]
            api_name = api_data['locations'][i]
            
            if db_name == api_name:
                db_count = db_data['counts'][i]
                api_count = api_data['counts'][i]
                
                if abs(db_count - api_count) < 0.001:
                    print(f"✓ {db_name}: {db_count}人次 数据一致")
                else:
                    print(f"✗ {db_name}: 数据库{db_count}人次 vs API{api_count}人次")
            else:
                print(f"✗ 食堂名称不匹配: 数据库'{db_name}' vs API'{api_name}'")
    
    print("\n===== 验证总结 =====")
    all_success = True
    for endpoint, result in api_results.items():
        if result['status'] == 'success':
            print(f"✓ {endpoint}: 返回成功")
        else:
            all_success = False
            print(f"✗ {endpoint}: 返回失败")
    
    if all_success and db_data and len(api_results) > 0:
        print("\n🎉 所有API端点修复成功! 现在应该返回真实的数据库数据。")
    else:
        print("\n⚠️  部分API端点可能仍有问题，请检查服务器状态和认证信息。")

def main():
    """主函数"""
    print("\n========================================")
    print("       食堂消费数据修复验证工具")
    print("========================================")
    
    # 从数据库获取数据
    db_data = verify_db_data()
    
    # 验证API数据
    print("\n注意：API测试需要服务器正在运行")
    print("如果服务器未运行，建议手动启动服务器并测试")
    
    # 尝试验证API数据
    api_results = verify_api_data()
    
    # 比较数据
    compare_data(db_data, api_results)
    
    print("\n========================================")
    print("验证完成。请刷新前端页面查看修复后的食堂消费人次数据。")
    print("========================================")

if __name__ == "__main__":
    main()