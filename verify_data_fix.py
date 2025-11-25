#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证数据修复结果"""

from utils.db_connection import DatabaseConnection

print("验证数据修复结果...")

# 创建数据库连接
db = DatabaseConnection()
if db.connect():
    print("✅ 数据库连接成功")
    
    # 检查消费记录总数
    query = "SELECT COUNT(*) FROM consumption_records"
    result = db.execute_query(query)
    if result:
        count = result[0]['COUNT(*)']
        print(f"\n消费记录总数: {count}")
    
    # 检查不同的card_no数量
    query = "SELECT COUNT(DISTINCT card_no) FROM consumption_records"
    result = db.execute_query(query)
    if result:
        distinct_count = result[0]['COUNT(DISTINCT card_no)']
        print(f"不同的卡号数量: {distinct_count}")
    
    # 检查前20条记录的card_no
    query = "SELECT card_no FROM consumption_records LIMIT 20"
    result = db.execute_query(query)
    if result:
        print("\n前20条记录的card_no:")
        for i, item in enumerate(result):
            print(f"  {i+1}. {item['card_no']}")
    
    # 检查是否还有'card_no'字符串值
    query = "SELECT COUNT(*) FROM consumption_records WHERE card_no = 'card_no'"
    result = db.execute_query(query)
    if result:
        invalid_count = result[0]['COUNT(*)']
        print(f"\n无效的'card_no'字符串记录数: {invalid_count}")
    
    # 检查示例数据
    query = "SELECT * FROM consumption_records LIMIT 5"
    result = db.execute_query(query)
    if result:
        print("\n前5条完整记录示例:")
        for i, record in enumerate(result):
            print(f"\n记录 {i+1}:")
            for key, value in record.items():
                print(f"  {key}: {value}")
    
    # 检查今日统计数据
    print("\n检查今日统计数据查询:")
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
        print(f"总金额: {result[0]['total_amount']}")
        print(f"总次数: {result[0]['total_count']}")
        print(f"平均金额: {result[0]['average_amount']}")
    
    # 关闭连接
    db.disconnect()
else:
    print("❌ 数据库连接失败")