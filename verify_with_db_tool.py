#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用项目现有数据库工具类的验证脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.db_connection import db_conn

def verify_consumer_count():
    """
    验证消费人数统计
    """
    print("=== 使用项目数据库工具验证消费人数 ===")
    
    try:
        # 连接数据库
        if not db_conn.connect():
            print("无法连接到数据库，验证失败!")
            return
        
        print("\n1. 查询去重后的消费者总数:")
        query = "SELECT COUNT(DISTINCT card_number) AS unique_count FROM consumption_records"
        result = db_conn.execute_query(query)
        
        if result and len(result) > 0:
            unique_count = result[0]['unique_count']
            print(f"   数据库中去重后的消费者总数: {unique_count}")
        else:
            print("   未获取到消费者总数")
            unique_count = 0
        
        print("\n2. 按阈值分组统计各类消费群体:")
        # 使用与之前相同的SQL查询，但适配DictCursor的返回格式
        sql = """
        SELECT 
            SUM(CASE WHEN total_amount < 122.90 THEN 1 ELSE 0 END) AS '节约型',
            SUM(CASE WHEN total_amount >= 122.90 AND total_amount < 196.65 THEN 1 ELSE 0 END) AS '极简型',
            SUM(CASE WHEN total_amount >= 196.65 AND total_amount < 294.97 THEN 1 ELSE 0 END) AS '普通型',
            SUM(CASE WHEN total_amount >= 294.97 AND total_amount < 491.62 THEN 1 ELSE 0 END) AS '活跃型',
            SUM(CASE WHEN total_amount >= 491.62 THEN 1 ELSE 0 END) AS '土豪型'
        FROM (
            SELECT card_number, SUM(amount) AS total_amount
            FROM consumption_records
            GROUP BY card_number
        ) AS user_totals
        """
        
        category_result = db_conn.execute_query(sql)
        
        if category_result and len(category_result) > 0:
            categories = ['节约型', '极简型', '普通型', '活跃型', '土豪型']
            total_sum = 0
            
            for cat in categories:
                count = category_result[0].get(cat, 0)
                total_sum += count
                print(f"   {cat}: {count}人")
            
            print(f"\n3. 统计结果验证:")
            print(f"   各类别总计: {total_sum}人")
            print(f"   与数据库去重总数差异: {unique_count - total_sum}")
            
            # 验证聚类总和是否等于去重总数
            if unique_count > 0 and total_sum == unique_count:
                print("   ✅ 验证通过: 聚类总和与去重总数完全匹配")
            else:
                print(f"   ⚠️  验证警告: 聚类总和与去重总数不匹配")
                
        else:
            print("   未获取到分类统计结果")
            
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        db_conn.disconnect()
        print("\n验证完成!")

if __name__ == "__main__":
    verify_consumer_count()