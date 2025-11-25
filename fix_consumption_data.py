#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复消费记录数据"""

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

def fix_consumption_records():
    """修复消费记录数据"""
    connection = connect_to_db()
    
    try:
        cursor = connection.cursor()
        
        print("\n🔍 检查当前消费记录表状态...")
        # 检查表中数据
        cursor.execute("SELECT COUNT(*) FROM consumption_records")
        count = cursor.fetchone()[0]
        print(f"当前表中有 {count} 条记录")
        
        # 检查前10条记录的card_no
        cursor.execute("SELECT card_no FROM consumption_records LIMIT 10")
        sample_data = cursor.fetchall()
        print("前10条记录的card_no示例:")
        for item in sample_data:
            print(f"  - {item[0]}")
        
        # 清空表并重新导入
        print("\n🗑️  清空消费记录表...")
        cursor.execute("TRUNCATE TABLE consumption_records")
        print("✅ 表已清空")
        
        print("\n📥 开始重新导入消费记录数据...")
        # 读取CSV文件
        df = pd.read_csv('data2.csv', encoding='gbk')
        total_rows = len(df)
        print(f"读取到 {total_rows} 条消费记录数据")
        
        # 准备插入数据
        start_time = time.time()
        inserted_count = 0
        failed_count = 0
        batch_size = 10000
        
        # 批量插入
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                try:
                    # 处理日期时间
                    date_time = None
                    if 'Date' in row and pd.notna(row['Date']):
                        try:
                            date_time = pd.to_datetime(row['Date'])
                        except Exception as dt_err:
                            print(f"⚠️  日期解析错误: {dt_err}")
                            date_time = None
                    
                    # 执行单条插入
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
                    
                    # 显示进度
                    if inserted_count % 5000 == 0 or inserted_count == total_rows:
                        progress = (inserted_count / total_rows) * 100
                        print(f"进度: {progress:.1f}% - 已导入 {inserted_count} 条数据")
                except Exception as e:
                    failed_count += 1
                    # 继续处理下一条数据
                    if failed_count <= 10:  # 只打印前10个错误
                        print(f"⚠️  插入失败: {e}")
                    continue
        
        # 提交事务
        connection.commit()
        
        end_time = time.time()
        print(f"✅ 消费记录数据修复完成!")
        print(f"总共导入: {inserted_count} 条")
        print(f"导入失败: {failed_count} 条")
        print(f"耗时: {end_time - start_time:.2f} 秒")
        
        # 验证修复结果
        print("\n🔍 验证修复结果...")
        cursor.execute("SELECT COUNT(*) FROM consumption_records")
        new_count = cursor.fetchone()[0]
        print(f"修复后的记录数: {new_count}")
        
        cursor.execute("SELECT DISTINCT card_no FROM consumption_records LIMIT 10")
        distinct_cards = cursor.fetchall()
        print("修复后的不同卡号示例:")
        for card in distinct_cards:
            print(f"  - {card[0]}")
        
    except Exception as e:
        print(f"\n❌ 数据修复过程中发生错误: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n✅ 数据库连接已关闭")

if __name__ == "__main__":
    print("====================================")
    print("学生消费行为分析系统 - 消费记录数据修复")
    print("====================================")
    fix_consumption_records()