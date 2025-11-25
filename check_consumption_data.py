#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查消费记录数据"""
import pymysql
import traceback

def check_consumption_data():
    try:
        # 连接数据库
        conn = pymysql.connect(
            host='localhost', 
            user='root', 
            password='123456', 
            database='student_analytics',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # 检查总记录数和总金额
        cursor.execute('SELECT COUNT(*) as count, SUM(money) as total FROM consumption_records')
        total_info = cursor.fetchone()
        print('总记录数和总金额:', total_info)
        
        # 检查最近12个月的数据
        print('\n近12个月的消费数据:')
        cursor.execute('''
            SELECT DATE_FORMAT(date_time, '%Y-%m') AS month, 
                   SUM(money) AS total_amount 
            FROM consumption_records 
            GROUP BY DATE_FORMAT(date_time, '%Y-%m') 
            ORDER BY month DESC 
            LIMIT 12
        ''')
        for row in cursor.fetchall():
            print(row)
        
        # 检查最近的几条记录
        print('\n最近的5条消费记录:')
        cursor.execute('SELECT * FROM consumption_records ORDER BY date_time DESC LIMIT 5')
        for row in cursor.fetchall():
            print(row)
            
    except Exception as e:
        print(f"检查数据时出错: {str(e)}")
        traceback.print_exc()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    check_consumption_data()