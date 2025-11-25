#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""恢复所有数据库表数据"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import time
import sys

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
        sys.exit(1)

def restore_students_data(connection):
    """恢复学生数据"""
    try:
        cursor = connection.cursor()
        print("\n📥 开始恢复学生数据...")
        
        # 读取CSV文件
        df = pd.read_csv('data1.csv', encoding='gbk')
        total_rows = len(df)
        print(f"读取到 {total_rows} 条学生数据")
        
        # 清空表
        cursor.execute("TRUNCATE TABLE students")
        print("✅ 学生表已清空")
        
        # 批量插入
        start_time = time.time()
        inserted_count = 0
        failed_count = 0
        
        for _, row in df.iterrows():
            try:
                sql = """
                    INSERT INTO students 
                    (card_no, sex, major, access_card_no, password)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    str(row['CardNo']) if pd.notna(row['CardNo']) else None,
                    str(row['Sex']) if pd.notna(row['Sex']) else None,
                    str(row['Major']) if pd.notna(row['Major']) else None,
                    str(row['CardNo']) if pd.notna(row['CardNo']) else None,
                    str(row['CardNo']) if pd.notna(row['CardNo']) else None
                ))
                inserted_count += 1
                
                if inserted_count % 1000 == 0 or inserted_count == total_rows:
                    print(f"已导入 {inserted_count}/{total_rows} 条学生数据")
            except Exception as e:
                failed_count += 1
                if failed_count <= 5:
                    print(f"⚠️  插入失败: {e}")
                continue
        
        connection.commit()
        end_time = time.time()
        print(f"✅ 学生数据恢复完成!")
        print(f"总共导入: {inserted_count} 条")
        print(f"导入失败: {failed_count} 条")
        print(f"耗时: {end_time - start_time:.2f} 秒")
        
    except Exception as e:
        print(f"\n❌ 学生数据恢复过程中发生错误: {e}")
        connection.rollback()

def restore_consumption_data(connection):
    """恢复消费记录数据"""
    try:
        cursor = connection.cursor()
        print("\n📥 开始恢复消费记录数据...")
        
        # 读取CSV文件
        df = pd.read_csv('data2.csv', encoding='gbk')
        total_rows = len(df)
        print(f"读取到 {total_rows} 条消费记录数据")
        
        # 清空表
        cursor.execute("TRUNCATE TABLE consumption_records")
        print("✅ 消费记录表已清空")
        
        # 批量插入
        start_time = time.time()
        inserted_count = 0
        failed_count = 0
        batch_size = 10000
        
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                try:
                    # 处理日期时间
                    date_time = None
                    if 'Date' in row and pd.notna(row['Date']):
                        try:
                            date_time = pd.to_datetime(row['Date'])
                        except Exception:
                            date_time = None
                    
                    sql = """
                        INSERT INTO consumption_records 
                        (card_no, peo_no, date_time, money, term_no, term_ser_no, con_oper_no, oper_no, dept)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        str(row['CardNo']) if pd.notna(row['CardNo']) else None,
                        str(row['PeoNo']) if pd.notna(row['PeoNo']) else None,
                        date_time,
                        float(row['Money']) if pd.notna(row['Money']) else 0,
                        str(row['TermNo']) if pd.notna(row['TermNo']) else None,
                        str(row['TermSerNo']) if pd.notna(row['TermSerNo']) else None,
                        str(row['conOperNo']) if pd.notna(row['conOperNo']) else None,
                        str(row['OperNo']) if pd.notna(row['OperNo']) else None,
                        str(row['Dept']) if pd.notna(row['Dept']) else None
                    ))
                    inserted_count += 1
                    
                    if inserted_count % 10000 == 0 or inserted_count == total_rows:
                        progress = (inserted_count / total_rows) * 100
                        print(f"进度: {progress:.1f}% - 已导入 {inserted_count} 条消费记录")
                except Exception as e:
                    failed_count += 1
                    if failed_count <= 5:
                        print(f"⚠️  插入失败: {e}")
                    continue
        
        connection.commit()
        end_time = time.time()
        print(f"✅ 消费记录数据恢复完成!")
        print(f"总共导入: {inserted_count} 条")
        print(f"导入失败: {failed_count} 条")
        print(f"耗时: {end_time - start_time:.2f} 秒")
        
    except Exception as e:
        print(f"\n❌ 消费记录数据恢复过程中发生错误: {e}")
        connection.rollback()

def restore_access_records(connection):
    """恢复门禁记录数据"""
    try:
        cursor = connection.cursor()
        print("\n📥 开始恢复门禁记录数据...")
        
        # 读取CSV文件
        df = pd.read_csv('data3.csv', encoding='gbk')
        total_rows = len(df)
        print(f"读取到 {total_rows} 条门禁记录数据")
        
        # 清空表
        cursor.execute("TRUNCATE TABLE access_records")
        print("✅ 门禁记录表已清空")
        
        # 批量插入
        start_time = time.time()
        inserted_count = 0
        failed_count = 0
        
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
                failed_count += 1
                if failed_count <= 5:
                    print(f"⚠️  插入失败: {e}")
                continue
        
        connection.commit()
        end_time = time.time()
        print(f"✅ 门禁记录数据恢复完成!")
        print(f"总共导入: {inserted_count} 条")
        print(f"导入失败: {failed_count} 条")
        print(f"耗时: {end_time - start_time:.2f} 秒")
        
    except Exception as e:
        print(f"\n❌ 门禁记录数据恢复过程中发生错误: {e}")
        connection.rollback()

def verify_data_restore(connection):
    """验证数据恢复结果"""
    try:
        cursor = connection.cursor()
        print("\n🔍 验证数据恢复结果...")
        
        # 检查各表记录数
        tables = ['students', 'consumption_records', 'access_records']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table} 表: {count} 条记录")
        
        # 检查消费记录表的card_no字段
        print("\n消费记录表的card_no字段示例:")
        cursor.execute("SELECT card_no FROM consumption_records LIMIT 10")
        sample_cards = cursor.fetchall()
        for card in sample_cards:
            print(f"  - {card[0]}")
            
    except Exception as e:
        print(f"\n❌ 数据验证过程中发生错误: {e}")

if __name__ == "__main__":
    print("====================================")
    print("学生消费行为分析系统 - 数据完全恢复工具")
    print("====================================")
    
    connection = connect_to_db()
    try:
        # 按顺序恢复所有数据
        restore_students_data(connection)
        restore_consumption_data(connection)
        restore_access_records(connection)
        
        # 验证恢复结果
        verify_data_restore(connection)
        
        print("\n🎉 所有数据恢复完成!")
        
    finally:
        if connection.is_connected():
            connection.close()
            print("✅ 数据库连接已关闭")