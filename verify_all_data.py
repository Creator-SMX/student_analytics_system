#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全面验证所有数据库表的数据恢复情况"""

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

def verify_all_tables(connection):
    """验证所有表的数据"""
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        print("\n🔍 开始全面验证数据恢复情况...")
        
        # 1. 检查各表是否存在
        tables = ['students', 'consumption_records', 'access_records', 'admins']
        for table in tables:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if cursor.fetchone():
                print(f"✅ 表 {table} 存在")
            else:
                print(f"❌ 表 {table} 不存在")
        
        # 2. 检查各表记录数
        print("\n📊 各表记录数统计:")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count:,} 条记录")
            except Error as e:
                print(f"❌ 查询 {table} 失败: {e}")
        
        # 3. 检查消费记录表的card_no字段
        print("\n📋 消费记录表card_no字段样本:")
        cursor.execute("SELECT card_no FROM consumption_records LIMIT 20")
        cards = cursor.fetchall()
        if cards:
            print(f"前20条记录的card_no值:")
            for i, card in enumerate(cards, 1):
                print(f"  {i}. {card[0]}")
            
            # 检查是否存在'card_no'字符串值
            cursor.execute("SELECT COUNT(*) FROM consumption_records WHERE card_no = 'card_no'")
            invalid_count = cursor.fetchone()[0]
            print(f"\n❌ 无效的'card_no'字符串记录数: {invalid_count}")
            
            # 检查不同卡号的数量
            cursor.execute("SELECT COUNT(DISTINCT card_no) FROM consumption_records")
            distinct_count = cursor.fetchone()[0]
            print(f"✅ 不同卡号的数量: {distinct_count}")
        else:
            print("❌ 消费记录表为空")
        
        # 4. 检查学生表
        print("\n🧑‍🎓 学生表样本数据:")
        cursor.execute("SELECT card_no, sex, major FROM students LIMIT 10")
        students = cursor.fetchall()
        for student in students:
            print(f"  卡号: {student[0]}, 性别: {student[1]}, 专业: {student[2]}")
        
        # 5. 检查门禁记录
        print("\n🚪 门禁记录表样本:")
        cursor.execute("SELECT card_no, access_time FROM access_records LIMIT 5")
        access = cursor.fetchall()
        for a in access:
            print(f"  卡号: {a[0]}, 时间: {a[1]}")
        
        # 6. 检查今日统计数据
        print("\n📈 今日消费统计数据:")
        cursor.execute("""
            SELECT 
                SUM(money) as total_amount, 
                COUNT(*) as total_count,
                AVG(money) as average_amount 
            FROM consumption_records 
            WHERE DATE(date_time) = CURDATE()
        """)
        stats = cursor.fetchone()
        print(f"  今日总金额: {stats[0] if stats[0] else 0}")
        print(f"  今日总次数: {stats[1] if stats[1] else 0}")
        print(f"  今日平均金额: {stats[2] if stats[2] else 0}")
        
        print("\n🎉 数据验证完成!")
        
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()

if __name__ == "__main__":
    print("====================================")
    print("学生消费行为分析系统 - 数据验证工具")
    print("====================================")
    
    connection = connect_to_db()
    try:
        verify_all_tables(connection)
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("✅ 数据库连接已关闭")