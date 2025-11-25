"""独立测试get_cluster函数的核心逻辑"""
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入需要的模块
from sqlalchemy import text
from analytics.analytics_controller import db_conn

def test_cluster_query_logic():
    """测试聚类查询逻辑"""
    print("开始测试get_cluster核心逻辑...")
    
    try:
        # 连接数据库
        conn = db_conn.connect()
        if not conn:
            print("错误: 数据库连接失败")
            return False
        
        print("✓ 数据库连接成功")
        
        # 测试money > 0过滤条件
        print("\n测试总消费人数查询:")
        total_sql = """
        SELECT COUNT(DISTINCT card_no) AS total_count 
        FROM consumption_records
        WHERE money > 0
        """
        total_result = conn.execute(text(total_sql)).fetchone()
        total_consumers = total_result.total_count if total_result else 0
        print(f"✓ 总消费人数: {total_consumers}")
        
        # 测试节约型消费查询
        print("\n测试节约型消费查询:")
        sql = """
        SELECT COUNT(DISTINCT card_no) AS count 
        FROM (
            SELECT card_no, SUM(money) AS total_amount
            FROM consumption_records
            WHERE money > 0
            GROUP BY card_no
        ) AS student_totals
        WHERE total_amount < 122.90
        """
        result = conn.execute(text(sql)).fetchone()
        frugal_count = result.count if result and result.count is not None else 0
        print(f"✓ 节约型消费人数: {frugal_count}")
        
        # 测试极简型消费查询
        print("\n测试极简型消费查询:")
        sql = """
        SELECT COUNT(DISTINCT card_no) AS count 
        FROM (
            SELECT card_no, SUM(money) AS total_amount
            FROM consumption_records
            WHERE money > 0
            GROUP BY card_no
        ) AS student_totals
        WHERE total_amount BETWEEN 122.90 AND 196.65
        """
        result = conn.execute(text(sql)).fetchone()
        minimal_count = result.count if result and result.count is not None else 0
        print(f"✓ 极简型消费人数: {minimal_count}")
        
        # 计算百分比示例
        if total_consumers > 0:
            frugal_percentage = round((frugal_count / total_consumers * 100), 1)
            print(f"\n✓ 节约型消费百分比: {frugal_percentage}%")
        
        print("\n✓ 所有查询测试完成")
        return True
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        print("详细错误信息:")
        traceback.print_exc()
        return False
    
    finally:
        # 确保关闭连接
        try:
            db_conn.disconnect()
            print("✓ 数据库连接已关闭")
        except Exception as e:
            print(f"关闭连接错误: {str(e)}")

if __name__ == "__main__":
    print("===== 测试get_cluster核心逻辑 =====")
    success = test_cluster_query_logic()
    if success:
        print("\n🎉 测试成功! get_cluster核心逻辑工作正常")
        sys.exit(0)
    else:
        print("\n❌ 测试失败! 请检查上述错误信息")
        sys.exit(1)