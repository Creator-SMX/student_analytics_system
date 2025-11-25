# 简单测试SQL查询

import pymysql
from utils.db_connection import db_conn

# 测试数据库连接和查询
def test_sql_query():
    print("开始测试数据库查询...")
    
    conn = None
    try:
        # 使用项目中已有的数据库连接
        conn = db_conn.connect()
        if not conn:
            print("数据库连接失败")
            return False
        
        print("数据库连接成功！")
        
        # 测试简单查询 - 先检查表是否存在
        check_table_sql = "SHOW TABLES LIKE 'consumption_records'"
        result = conn.execute(check_table_sql).fetchall()
        
        if not result:
            print("错误：consumption_records表不存在")
            return False
        
        print("consumption_records表存在")
        
        # 测试查询消费记录总数
        count_sql = "SELECT COUNT(*) AS total FROM consumption_records"
        result = conn.execute(count_sql).fetchone()
        total_records = result[0] if result else 0
        print(f"消费记录总数: {total_records}")
        
        # 测试查询唯一消费者数量
        unique_users_sql = "SELECT COUNT(DISTINCT card_no) AS unique_users FROM consumption_records"
        result = conn.execute(unique_users_sql).fetchone()
        unique_users = result[0] if result else 0
        print(f"唯一消费者数量: {unique_users}")
        
        # 测试聚类查询的简化版本
        cluster_sql = """
        SELECT
            COUNT(*) AS total_consumers,
            SUM(CASE WHEN monthly_total < 122.90 THEN 1 ELSE 0 END) AS '节约型'
        FROM (
            SELECT card_no, SUM(money) AS monthly_total
            FROM consumption_records
            GROUP BY card_no
            LIMIT 100  # 限制样本量以便快速测试
        ) AS user_monthly_totals
        """
        
        result = conn.execute(cluster_sql).fetchone()
        if result:
            print(f"简化聚类测试结果：总人数={result[0]}, 节约型={result[1] if result[1] is not None else 0}")
        
        return True
        
    except Exception as e:
        print(f"查询过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 确保关闭连接
        try:
            if conn:
                db_conn.disconnect()
            print("数据库连接已关闭")
        except Exception as e:
            print(f"关闭连接时出错: {str(e)}")

if __name__ == "__main__":
    success = test_sql_query()
    print(f"\n测试{'通过' if success else '失败'}")