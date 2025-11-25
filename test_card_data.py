#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：检查数据库中的校园卡号数据
"""

import sqlite3
import pandas as pd

# 连接到数据库
db_path = 'student_analytics.db'
try:
    print(f"正在连接数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查表结构
    print("\n=== 表结构 ===")
    cursor.execute("PRAGMA table_info(consumption_records)")
    columns = cursor.fetchall()
    print("consumption_records 表的列:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 检查前10条数据
    print("\n=== 前10条数据示例 ===")
    query = "SELECT * FROM consumption_records LIMIT 10"
    df = pd.read_sql_query(query, conn)
    print(df)
    
    # 检查card_no列的数据
    print("\n=== card_no列的数据分布 ===")
    query = "SELECT card_no, COUNT(*) as count FROM consumption_records GROUP BY card_no LIMIT 20"
    card_stats = pd.read_sql_query(query, conn)
    print(card_stats)
    
    # 检查是否有重复的值
    print("\n=== 检查是否有'card_no'字符串值 ===")
    query = "SELECT COUNT(*) FROM consumption_records WHERE card_no = 'card_no'"
    cursor.execute(query)
    result = cursor.fetchone()
    print(f"存在 'card_no' 字符串值的记录数: {result[0]}")
    
    # 获取非'card_no'值的数量
    print("\n=== 获取实际卡号数量 ===")
    query = "SELECT COUNT(DISTINCT card_no) FROM consumption_records WHERE card_no != 'card_no'"
    cursor.execute(query)
    result = cursor.fetchone()
    print(f"非'card_no'字符串的唯一卡号数量: {result[0]}")
    
    # 显示一些实际卡号的例子
    if result[0] > 0:
        print("\n=== 实际卡号示例 ===")
        query = "SELECT DISTINCT card_no FROM consumption_records WHERE card_no != 'card_no' LIMIT 10"
        actual_cards = pd.read_sql_query(query, conn)
        print(actual_cards)
        
    conn.close()
    print("\n数据库检查完成")
    
except Exception as e:
    print(f"错误: {str(e)}")
    if 'conn' in locals():
        conn.close()