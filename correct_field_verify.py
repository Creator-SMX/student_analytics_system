#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用正确字段名的验证脚本
发现问题：数据库字段名是card_no和money，不是card_number和amount
"""

import pymysql

def main():
    """
    主函数：使用正确字段名验证消费人数
    """
    print("=== 使用正确字段名验证消费人数 ===")
    
    # 数据库连接参数
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'student_analytics',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    conn = None
    cursor = None
    
    try:
        # 连接数据库
        print("正在连接数据库...")
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        print("✅ 数据库连接成功!")
        
        # 1. 获取去重后的消费者总数（使用正确的字段名card_no）
        print("\n1. 查询去重后的消费者总数:")
        cursor.execute("SELECT COUNT(DISTINCT card_no) AS unique_count FROM consumption_records")
        result = cursor.fetchone()
        unique_count = result['unique_count']
        print(f"   数据库中去重后的消费者总数: {unique_count}")
        
        # 2. 获取总消费记录数
        print("\n2. 查询总消费记录数:")
        cursor.execute("SELECT COUNT(*) AS total_records FROM consumption_records")
        total_result = cursor.fetchone()
        total_records = total_result['total_records']
        print(f"   总消费记录数: {total_records}")
        
        # 3. 按阈值分组统计各类消费群体（使用正确的字段名）
        print("\n3. 按阈值分组统计各类消费群体:")
        sql = """
        SELECT 
            SUM(CASE WHEN total_amount < 122.90 THEN 1 ELSE 0 END) AS '节约型',
            SUM(CASE WHEN total_amount >= 122.90 AND total_amount < 196.65 THEN 1 ELSE 0 END) AS '极简型',
            SUM(CASE WHEN total_amount >= 196.65 AND total_amount < 294.97 THEN 1 ELSE 0 END) AS '普通型',
            SUM(CASE WHEN total_amount >= 294.97 AND total_amount < 491.62 THEN 1 ELSE 0 END) AS '活跃型',
            SUM(CASE WHEN total_amount >= 491.62 THEN 1 ELSE 0 END) AS '土豪型'
        FROM (
            SELECT card_no, SUM(money) AS total_amount
            FROM consumption_records
            GROUP BY card_no
        ) AS user_totals
        """
        
        cursor.execute(sql)
        category_result = cursor.fetchone()
        
        if category_result:
            categories = ['节约型', '极简型', '普通型', '活跃型', '土豪型']
            counts = []
            total_sum = 0
            
            for cat in categories:
                count = category_result.get(cat, 0)
                counts.append(count)
                total_sum += count
                print(f"   {cat}: {count}人")
            
            print(f"\n4. 统计结果验证:")
            print(f"   各类别总计: {total_sum}人")
            print(f"   与数据库去重总数对比: {unique_count}")
            print(f"   差异值: {unique_count - total_sum}")
            
            # 计算百分比
            print("\n5. 各类别百分比:")
            if total_sum > 0:
                for i, (cat, count) in enumerate(zip(categories, counts)):
                    percentage = (count / total_sum) * 100
                    print(f"   {cat}: {percentage:.1f}%")
            
        # 4. 查询前5条记录看看数据结构
        print("\n6. 查看前5条消费记录样本:")
        cursor.execute("SELECT * FROM consumption_records LIMIT 5")
        sample_records = cursor.fetchall()
        
        if sample_records:
            print(f"   记录1的字段: {list(sample_records[0].keys())}")
            print(f"   记录1的部分值:")
            for key in list(sample_records[0].keys())[:5]:  # 只显示前5个字段
                print(f"     {key}: {sample_records[0][key]}")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("\n✅ 数据库连接已关闭")

if __name__ == "__main__":
    main()