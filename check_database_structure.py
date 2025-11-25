#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库结构和可用表
"""

import sqlite3
import pandas as pd

# 连接到数据库
db_path = 'student_analytics.db'
try:
    print(f"正在连接数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 列出所有表
    print("\n=== 数据库中的所有表 ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        print("数据库中没有表!")
    else:
        for table in tables:
            table_name = table[0]
            print(f"\n表名: {table_name}")
            
            # 显示表结构
            print(f"  表结构:")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
            
            # 显示前5条数据
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 5", conn)
                print(f"  前5条数据:")
                print(f"  {df}")
            except Exception as e:
                print(f"  获取数据时出错: {str(e)}")
    
    # 检查其他可能的数据库文件
    print("\n=== 检查其他可能的数据库文件 ===")
    import os
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    print(f"当前目录下的数据库文件: {db_files}")
    
    # 检查是否有数据导入脚本
    print("\n=== 检查数据导入脚本 ===")
    import glob
    import_data_scripts = glob.glob('*import*.py')
    create_db_scripts = glob.glob('*create*.py')
    print(f"导入数据相关脚本: {import_data_scripts}")
    print(f"创建数据库相关脚本: {create_db_scripts}")
    
    conn.close()
    print("\n数据库结构检查完成")
    
except Exception as e:
    print(f"错误: {str(e)}")
    if 'conn' in locals():
        conn.close()