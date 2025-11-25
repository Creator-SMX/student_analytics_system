#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试SQL语法修复脚本"""
import pymysql
import pandas as pd

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'student_analytics'
}

def test_sql_fix():
    """测试SQL语法修复是否有效"""
    try:
        # 建立数据库连接
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ 成功连接到数据库")
        
        # 使用修复后的SQL语法（使用CONCAT而不是||）
        consumption_query = """
        SELECT 
            cr.date_time, 
            CONCAT('消费 - ', cr.card_no) AS activity_id,
            CONCAT(cr.card_no, ' 在 ', cr.dept, ' 消费了 ', cr.money, ' 元') AS description,
            '消费' AS type,
            cr.money AS amount,
            COALESCE(s.major, '未知专业') AS major,
            cr.card_no
        FROM consumption_records cr
        LEFT JOIN students s ON cr.card_no = s.card_no
        LIMIT 5
        """
        
        print("\n测试消费记录查询:")
        print(consumption_query)
        
        # 执行查询
        df = pd.read_sql(consumption_query, connection)
        print(f"✅ 查询成功，返回 {len(df)} 条记录")
        print("\n查询结果示例:")
        print(df.head())
        
        # 测试门禁记录查询（修正JOIN条件，使用access_card_no）
        access_query = """
        SELECT 
            ar.date_time, 
            CONCAT('门禁 - ', COALESCE(s.card_no, ar.access_card_no)) AS activity_id,
            CONCAT(COALESCE(s.card_no, ar.access_card_no), ' 从 ', ar.address, ' ', ar.describe_text) AS description,
            '门禁' AS type,
            0 AS amount,
            COALESCE(s.major, '未知专业') AS major,
            COALESCE(s.card_no, ar.access_card_no) AS card_no
        FROM access_records ar
        LEFT JOIN students s ON ar.access_card_no = s.card_no
        LIMIT 5
        """
        
        print("\n测试门禁记录查询:")
        print(access_query)
        
        # 执行查询
        df_access = pd.read_sql(access_query, connection)
        print(f"✅ 查询成功，返回 {len(df_access)} 条记录")
        print("\n查询结果示例:")
        print(df_access.head())
        
        print("\n✅ SQL语法修复测试成功!")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
            print("✅ 数据库连接已关闭")

if __name__ == "__main__":
    print("开始测试SQL语法修复...")
    test_sql_fix()