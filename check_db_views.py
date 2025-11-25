#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库中的表和视图"""
import pymysql

try:
    # 连接数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='student_analytics'
    )
    cursor = conn.cursor()
    
    # 检查所有表
    print("\n数据库表:")
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    for table in tables:
        print(f'- {table[0]}')
    
    # 检查所有视图
    print("\n数据库视图:")
    cursor.execute('SHOW FULL TABLES WHERE Table_type = "VIEW"')
    views = cursor.fetchall()
    for view in views:
        print(f'- {view[0]}')
    
    # 检查consumption_clusters表是否存在并查看其数据
    print("\n检查consumption_clusters表数据:")
    try:
        cursor.execute('SELECT * FROM consumption_clusters LIMIT 5')
        rows = cursor.fetchall()
        if rows:
            print(f"找到 {len(rows)} 条数据")
            for row in rows:
                print(f"  {row}")
        else:
            print("表中没有数据")
    except Exception as e:
        print(f"表不存在或查询失败: {e}")
    
    # 尝试查询vw_consumption_clusters视图
    print("\n尝试查询vw_consumption_clusters视图:")
    try:
        cursor.execute('SELECT * FROM vw_consumption_clusters')
        row = cursor.fetchone()
        if row:
            print(f"视图数据: {row}")
    except Exception as e:
        print(f"视图不存在或查询失败: {e}")
    
    # 尝试查询v_cluster_input视图
    print("\n尝试查询v_cluster_input视图:")
    try:
        cursor.execute('SELECT * FROM v_cluster_input LIMIT 5')
        rows = cursor.fetchall()
        if rows:
            print(f"找到 {len(rows)} 条数据")
            for row in rows:
                print(f"  {row}")
    except Exception as e:
        print(f"视图不存在或查询失败: {e}")
        
    conn.close()
    
except Exception as e:
    print(f"连接数据库失败: {e}")