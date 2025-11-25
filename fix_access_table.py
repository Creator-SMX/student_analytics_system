#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复门禁表结构并导入数据"""

import pandas as pd
import mysql.connector
from mysql.connector import Error

# 数据库连接信息
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'student_analytics',
    'charset': 'utf8mb4'
}

def connect_to_db():
    """连接到数据库"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print(f"✅ 成功连接到数据库: {DB_CONFIG['database']}")
            return connection
    except Error as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def fix_access_table(connection):
    """修复门禁表结构"""
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        print("\n🔧 修复门禁表结构...")
        
        # 先查看表结构
        print("当前门禁表结构:")
        cursor.execute("SHOW COLUMNS FROM access_records")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]} - {col[1]}")
        
        # 删除旧表并重新创建
        print("\n🗑️ 删除并重新创建门禁表...")
        cursor.execute("DROP TABLE IF EXISTS access_records")
        
        # 创建正确的门禁表
        create_table_sql = """
        CREATE TABLE access_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            card_no VARCHAR(20) NOT NULL,
            access_time DATETIME,
            location VARCHAR(100)
        )
        """
        cursor.execute(create_table_sql)
        print("✅ 门禁表已重新创建")
        
        # 查看新的表结构
        print("\n新的门禁表结构:")
        cursor.execute("SHOW COLUMNS FROM access_records")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]} - {col[1]}")
        
        connection.commit()
        
    except Error as e:
        print(f"❌ 修复门禁表失败: {e}")
        connection.rollback()

def import_access_data(connection):
    """导入门禁数据"""
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        print("\n📥 导入门禁记录数据...")
        
        # 读取CSV文件
        df = pd.read_csv('data3.csv', encoding='gbk')
        total_rows = len(df)
        print(f"读取到 {total_rows} 条门禁记录数据")
        
        # 导入数据
        inserted_count = 0
        for _, row in df.iterrows():
            try:
                # 处理日期时间
                access_time = None
                if 'Date' in row and pd.notna(row['Date']):
                    try:
                        access_time = pd.to_datetime(row['Date'])
                    except Exception:
                        access_time = None
                
                sql = """
                    INSERT INTO access_records 
                    (card_no, access_time, location)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (
                    str(row['CardNo']) if pd.notna(row['CardNo']) else None,
                    access_time,
                    str(row['Location']) if pd.notna(row['Location']) else None
                ))
                inserted_count += 1
                
                if inserted_count % 1000 == 0 or inserted_count == total_rows:
                    print(f"已导入 {inserted_count}/{total_rows} 条门禁记录")
            except Exception as e:
                if inserted_count <= 10:  # 只打印前10个错误
                    print(f"⚠️  插入失败: {e}")
                continue
        
        connection.commit()
        print(f"✅ 门禁数据导入完成! 总共导入: {inserted_count} 条")
        
    except Exception as e:
        print(f"❌ 导入门禁数据失败: {e}")
        connection.rollback()

def verify_access_table(connection):
    """验证门禁表"""
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        print("\n🔍 验证门禁表数据...")
        
        # 检查记录数
        cursor.execute("SELECT COUNT(*) FROM access_records")
        count = cursor.fetchone()[0]
        print(f"门禁表记录数: {count} 条")
        
        # 检查样本数据
        cursor.execute("SELECT card_no, access_time, location FROM access_records LIMIT 5")
        records = cursor.fetchall()
        print("门禁表样本数据:")
        for record in records:
            print(f"  卡号: {record[0]}, 时间: {record[1]}, 位置: {record[2]}")
            
    except Error as e:
        print(f"❌ 验证门禁表失败: {e}")

if __name__ == "__main__":
    print("====================================")
    print("学生消费行为分析系统 - 门禁表修复工具")
    print("====================================")
    
    connection = connect_to_db()
    try:
        fix_access_table(connection)
        import_access_data(connection)
        verify_access_table(connection)
        print("\n🎉 门禁表修复完成!")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("✅ 数据库连接已关闭")