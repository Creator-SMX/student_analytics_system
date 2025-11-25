#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直接输出到控制台的数据库测试脚本"""
import pymysql

print("=== 数据库连接测试开始 ===")

try:
    # 尝试连接数据库
    print("尝试连接数据库 student_analytics...")
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='student_analytics',
        charset='utf8mb4'
    )
    print("✅ 数据库连接成功！")
    
    # 检查数据库中的表
    print("\n检查数据库中的表...")
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"数据库中的表数量: {len(tables)}")
        for table in tables:
            print(f"- 表名: {table[0]}")
    
    conn.close()
    print("\n✅ 数据库连接已关闭")
    print("\n=== 数据库连接测试成功 ===")
    
except Exception as e:
    print(f"\n❌ 错误: {str(e)}")
    import traceback
    print(f"错误详情: {traceback.format_exc()}")
    print("\n=== 数据库连接测试失败 ===")