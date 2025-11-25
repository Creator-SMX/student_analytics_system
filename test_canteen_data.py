#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试脚本：验证食堂消费人次和占比计算"""

import pymysql
from sqlalchemy import create_engine, text
import json

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'db': 'student_analytics',
    'charset': 'utf8mb4'
}

# 创建数据库连接引擎
def get_db_engine():
    engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['db']}?charset={db_config['charset']}")
    return engine

def test_canteen_consumption_data():
    """测试食堂消费数据计算"""
    print("===== 测试食堂消费人次和占比计算 =====")
    
    try:
        # 连接数据库
        engine = get_db_engine()
        conn = engine.connect()
        print("数据库连接成功")
        
        # 修改SQL查询，排除教师食堂，只计算第一到第五食堂
        sql = "SELECT dept, COUNT(*) as count, ROUND(SUM(money),2) as amount FROM consumption_records WHERE dept LIKE '%食堂%' AND dept != '教师食堂' GROUP BY dept ORDER BY count DESC"
        print(f"执行SQL查询: {sql}")
        
        # 执行查询并获取结果
        results = conn.execute(text(sql)).fetchall()
        print(f"查询完成，获取到 {len(results)} 条食堂数据")
        
        # 转换结果格式
        locations = [r.dept for r in results]
        counts = [r.count for r in results]
        amounts = [float(r.amount) for r in results]
        
        # 计算总消费人次
        total_count = sum(counts)
        print(f"总消费人次: {total_count}")
        
        # 计算百分比
        percentages = [(count/total_count*100) for count in counts]
        
        # 打印详细结果
        print("\n===== 食堂消费详细数据 =====")
        print("{:<15} {:<10} {:<15} {:<10}".format("食堂名称", "消费人次", "消费金额(元)", "占比(%)"))
        print("-" * 50)
        
        for loc, cnt, amt, pct in zip(locations, counts, amounts, percentages):
            print("{:<15} {:<10} {:<15.2f} {:<10.1f}".format(loc, cnt, amt, pct))
        
        # 生成JSON格式数据，与API返回格式保持一致
        json_data = {
            "locations": locations,
            "counts": counts,
            "amounts": amounts,
            "percentages": [round(pct, 1) for pct in percentages]
        }
        
        print("\n===== JSON格式输出（与API一致） =====")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
        
        # 与图表数据对比的建议
        print("\n===== 对比建议 =====")
        print("请将以上计算结果与前端图表进行对比，确保数据一致性：")
        print("1. 检查每个食堂的消费人次是否与图表显示一致")
        print("2. 检查百分比计算是否与图表显示一致")
        print("3. 检查食堂排序是否与图表一致（按消费人次降序）")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
    finally:
        # 确保关闭数据库连接
        if 'conn' in locals():
            try:
                conn.close()
                print("\n数据库连接已关闭")
            except:
                pass

if __name__ == "__main__":
    test_canteen_consumption_data()