#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试MySQL数据库连接和表结构"""
import pymysql
import traceback

def test_mysql_connection():
    """测试MySQL数据库连接和表结构"""
    print("=== MySQL数据库连接测试 ===\n")
    
    try:
        # 创建数据库连接
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ 数据库连接成功!")
        
        with connection.cursor() as cursor:
            # 检查所有表
            print("\n=== 数据库表 ===")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            for table in tables:
                table_name = list(table.values())[0]
                print(f"- {table_name}")
            
            # 检查表结构和数据统计
            print("\n=== 表结构和数据统计 ===")
            key_tables = ['students', 'consumption_records', 'access_records']
            
            for table in key_tables:
                print(f"\n--- {table} 表 ---")
                
                # 获取表结构
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print("列结构:")
                for col in columns:
                    print(f"  {col['Field']}: {col['Type']}")
                
                # 获取记录数
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                print(f"记录数: {count}")
                
                # 获取样本数据
                print("样本数据:")
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                samples = cursor.fetchall()
                for sample in samples:
                    print(f"  {sample}")
            
            # 检查关键统计数据
            print("\n=== 关键统计数据 ===")
            
            # 学生总数
            cursor.execute("SELECT COUNT(*) as total FROM students")
            total_students = cursor.fetchone()['total']
            print(f"学生总数: {total_students}")
            
            # 男女生人数
            cursor.execute("SELECT sex, COUNT(*) as count FROM students GROUP BY sex")
            gender_stats = cursor.fetchall()
            for item in gender_stats:
                print(f"{item['sex']}生人数: {item['count']}")
            
            # 总消费次数
            cursor.execute("SELECT COUNT(*) as total FROM consumption_records")
            total_consumption = cursor.fetchone()['total']
            print(f"总消费次数: {total_consumption}")
            
            # 有消费记录的学生数
            cursor.execute("SELECT COUNT(DISTINCT card_no) as count FROM consumption_records")
            consuming_students = cursor.fetchone()['count']
            print(f"有消费记录的学生数: {consuming_students}")
            
            # 总消费金额
            cursor.execute("SELECT SUM(money) as total, AVG(money) as avg FROM consumption_records")
            amount_stats = cursor.fetchone()
            print(f"总消费金额: {amount_stats['total']:.2f}")
            print(f"平均消费金额: {amount_stats['avg']:.2f}")
            
            # 检查视图
            print("\n=== 数据库视图 ===")
            cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
            views = cursor.fetchall()
            if views:
                for view in views:
                    print(f"- {view['Tables_in_student_analytics']}")
            else:
                print("没有找到视图")
        
        connection.close()
        print("\n✅ 数据库连接已关闭")
        return True
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_mysql_connection()