#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试API功能和数据库查询"""

from utils.db_connection import DatabaseConnection
import pandas as pd

print("测试API相关的数据库查询功能...")

# 创建数据库连接
db = DatabaseConnection()
if db.connect():
    print("✅ 数据库连接成功")
    
    # 测试1: 检查card_numbers查询
    print("\n测试1: 获取校园卡号列表")
    try:
        query = "SELECT DISTINCT card_no FROM consumption_records ORDER BY card_no LIMIT 5"
        result = db.execute_query(query)
        if result:
            print(f"✅ 查询成功，获取到 {len(result)} 条示例数据")
            for item in result:
                print(f"  - {item['card_no']}")
        else:
            print("❌ 查询返回空结果")
    except Exception as e:
        print(f"❌ 测试1失败: {str(e)}")
    
    # 测试2: 检查date_time字段是否存在
    print("\n测试2: 检查date_time字段")
    try:
        query = "SELECT date_time FROM consumption_records LIMIT 1"
        result = db.execute_query(query)
        if result:
            print(f"✅ date_time字段存在: {result[0]['date_time']}")
        else:
            print("❌ 查询返回空结果")
    except Exception as e:
        print(f"❌ 测试2失败: {str(e)}")
    
    # 测试3: 检查今日统计数据查询
    print("\n测试3: 获取今日统计数据")
    try:
        query = """
        SELECT 
            SUM(money) as total_amount, 
            COUNT(*) as total_count,
            AVG(money) as average_amount
        FROM consumption_records 
        WHERE DATE(date_time) = DATE(NOW())
        """
        result = db.execute_query(query)
        if result:
            print(f"✅ 查询成功")
            print(f"  总金额: {result[0]['total_amount']}")
            print(f"  总次数: {result[0]['total_count']}")
            print(f"  平均金额: {result[0]['average_amount']}")
        else:
            print("❌ 查询返回空结果")
    except Exception as e:
        print(f"❌ 测试3失败: {str(e)}")
    
    # 测试4: 检查是否存在consumption_time字段（曾经可能用过）
    print("\n测试4: 检查是否存在consumption_time字段")
    try:
        query = "SELECT consumption_time FROM consumption_records LIMIT 1"
        result = db.execute_query(query)
        print("✅ consumption_time字段存在")
    except Exception as e:
        print(f"❌ consumption_time字段不存在: {str(e)}")
    
    # 测试5: 使用Pandas DataFrame测试
    print("\n测试5: 使用Pandas DataFrame测试")
    try:
        query = "SELECT DISTINCT card_no FROM consumption_records ORDER BY card_no LIMIT 5"
        df = db.get_dataframe(query)
        print(f"✅ DataFrame查询成功，行数: {len(df)}")
        print(df.head())
    except Exception as e:
        print(f"❌ 测试5失败: {str(e)}")
    
    # 关闭连接
    db.disconnect()
else:
    print("❌ 数据库连接失败")