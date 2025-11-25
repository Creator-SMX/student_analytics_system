#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证消费人数的详细脚本"""
import pymysql
from sqlalchemy import create_engine, text

def verify_database_counts():
    """详细验证数据库中的消费人数"""
    print("=== 验证数据库消费人数开始 ===")
    
    # 数据库配置
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'db': 'student_analytics',
        'charset': 'utf8mb4'
    }
    
    try:
        # 创建SQLAlchemy引擎
        engine_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['db']}?charset={db_config['charset']}"
        engine = create_engine(engine_url)
        
        with engine.connect() as conn:
            print("\n1. 检查数据库中的学生总数:")
            students_total = conn.execute(text("SELECT COUNT(*) FROM students")).scalar()
            print(f"   学生表总人数: {students_total}")
            
            print("\n2. 检查消费记录中的不同学生数:")
            # 不同的查询方式
            
            # 方式1: 直接统计有消费记录的card_no数量（get_cluster函数使用的逻辑）
            query1 = """
            SELECT COUNT(DISTINCT card_no) 
            FROM consumption_records 
            WHERE money > 0
            """
            count1 = conn.execute(text(query1)).scalar()
            print(f"   方式1 (有消费记录且金额>0的card_no数): {count1}")
            
            # 方式2: 统计所有有消费记录的card_no数量（包括金额<=0的）
            query2 = """
            SELECT COUNT(DISTINCT card_no) 
            FROM consumption_records
            """
            count2 = conn.execute(text(query2)).scalar()
            print(f"   方式2 (所有有消费记录的card_no数): {count2}")
            
            # 方式3: 检查聚类查询中的具体条件
            query3 = """
            SELECT card_no, SUM(money) as total_money 
            FROM consumption_records 
            WHERE money > 0 
            GROUP BY card_no
            HAVING total_money > 0
            """
            results = conn.execute(text(query3)).fetchall()
            count3 = len(results)
            print(f"   方式3 (聚类查询实际返回的记录数): {count3}")
            
            # 检查是否有异常数据
            print("\n3. 检查异常数据:")
            # 空卡号
            empty_card_count = conn.execute(text("SELECT COUNT(DISTINCT card_no) FROM consumption_records WHERE card_no IS NULL OR card_no = ''")).scalar()
            print(f"   空卡号数量: {empty_card_count}")
            
            # 负消费记录
            neg_money_count = conn.execute(text("SELECT COUNT(*) FROM consumption_records WHERE money <= 0")).scalar()
            print(f"   负消费或零消费记录数: {neg_money_count}")
            
            # 验证students表和consumption_records表的关联
            print("\n4. 验证学生表和消费记录表的关联:")
            # 消费记录中存在但学生表中不存在的卡号
            query_missing = """
            SELECT COUNT(DISTINCT c.card_no) 
            FROM consumption_records c
            LEFT JOIN students s ON c.card_no = s.card_no
            WHERE s.card_no IS NULL AND c.card_no IS NOT NULL AND c.card_no != '' AND c.money > 0
            """
            missing_count = conn.execute(text(query_missing)).scalar()
            print(f"   消费记录中存在但学生表中不存在的卡号数: {missing_count}")
            
            # 学生表中有但无消费记录的学生数
            query_no_consumption = """
            SELECT COUNT(*) 
            FROM students s
            LEFT JOIN consumption_records c ON s.card_no = c.card_no AND c.money > 0
            WHERE c.card_no IS NULL
            """
            no_consumption_count = conn.execute(text(query_no_consumption)).scalar()
            print(f"   学生表中有但无有效消费记录的学生数: {no_consumption_count}")
            
            print("\n=== 验证数据库消费人数结束 ===")
            print(f"\n数据差异分析:")
            print(f"   硬编码值: 8636")
            print(f"   实际计算值: {count3}")
            print(f"   差异: {8636 - count3}")
            print(f"   可能原因: 数据清洗、异常记录过滤、时间差异等")
            
            return {
                'students_total': students_total,
                'active_consumers': count3,
                'hardcoded_value': 8636,
                'difference': 8636 - count3
            }
            
    except Exception as e:
        print(f"\n❌ 验证过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    verify_database_counts()