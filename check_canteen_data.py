#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查数据库中是否存在真实的食堂消费数据
"""

import pymysql
import pandas as pd
import sys

# 添加项目根目录到Python路径
sys.path.append('d:\\Pycharm\\PcData\\student_analytics_system')

def check_canteen_consumption_data():
    """直接查询数据库中的食堂消费数据"""
    print("开始检查数据库中的食堂消费数据...")
    
    try:
        # 连接数据库（使用与项目相同的配置）
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',  # 从db_connection.py获取的正确密码
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("数据库连接成功！")
        
        try:
            # 创建游标
            cursor = conn.cursor()
            
            # 1. 检查consumption_records表是否存在
            cursor.execute("SHOW TABLES LIKE 'consumption_records'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                print("[错误] consumption_records表不存在！")
                return False
            
            print("consumption_records表存在")
            
            # 2. 检查表结构
            cursor.execute("DESCRIBE consumption_records")
            columns = cursor.fetchall()
            print(f"表结构: {len(columns)} 个字段")
            for col in columns[:5]:  # 只显示前5个字段
                print(f"- {col['Field']} ({col['Type']})")
            if len(columns) > 5:
                print(f"... 等{len(columns)-5}个字段")
            
            # 3. 查询食堂相关的消费记录
            print("\n查询食堂相关的消费记录...")
            sql = """
                SELECT dept, COUNT(*) as count, ROUND(SUM(money), 2) as amount 
                FROM consumption_records 
                WHERE dept LIKE '%食堂%' 
                GROUP BY dept 
                ORDER BY count DESC
            """
            
            cursor.execute(sql)
            results = cursor.fetchall()
            
            print(f"\n找到 {len(results)} 个食堂的消费记录:")
            total_count = 0
            total_amount = 0.0
            
            if not results:
                print("[警告] 没有找到任何食堂相关的消费记录！")
                return False
            
            for row in results:
                dept = row['dept']
                count = row['count']
                amount = row['amount']
                total_count += count
                total_amount += amount if amount else 0
                
                print(f"- {dept}: {count}人次, ¥{amount}")
            
            print(f"\n总计: {total_count}人次, ¥{total_amount:.2f}")
            
            # 4. 检查是否有足够的数据
            if total_count > 0:
                print("\n结论: 数据库中存在真实的食堂消费数据")
                return True
            else:
                print("\n结论: 数据库中没有找到有效的食堂消费数据")
                return False
                
        finally:
            # 关闭游标和连接
            cursor.close()
            conn.close()
            print("数据库连接已关闭")
            
    except Exception as e:
        print(f"[错误] 查询过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_raw_data_sample():
    """查询少量原始数据样本"""
    print("\n=== 查询原始数据样本 ===")
    
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        try:
            cursor = conn.cursor()
            
            # 查询最近的10条食堂消费记录
            cursor.execute("""
                SELECT * FROM consumption_records 
                WHERE dept LIKE '%食堂%' 
                ORDER BY date_time DESC 
                LIMIT 10
            """)
            
            sample_data = cursor.fetchall()
            print(f"\n最近的10条食堂消费记录:")
            
            for i, record in enumerate(sample_data, 1):
                print(f"\n记录 {i}:")
                for key, value in record.items():
                    print(f"  {key}: {value}")
                    
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"[错误] 查询原始数据样本失败: {str(e)}")

if __name__ == "__main__":
    print("=== 食堂消费数据检查工具 ===\n")
    
    has_data = check_canteen_consumption_data()
    
    if has_data:
        check_raw_data_sample()
    
    print("\n检查完成！")