import pymysql
import json
from datetime import datetime

class ConsumptionQueryTest:
    @staticmethod
    def get_db_connection():
        """获取数据库连接"""
        return pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    
    @staticmethod
    def query_consumption_records(card_no='', start_date='', end_date='', limit=10):
        """
        查询消费记录的演示函数
        
        参数:
        - card_no: 校园卡号，可选
        - start_date: 开始日期，格式 YYYY-MM-DD，可选
        - end_date: 结束日期，格式 YYYY-MM-DD，可选
        - limit: 返回记录数限制
        """
        connection = None
        try:
            connection = ConsumptionQueryTest.get_db_connection()
            with connection.cursor() as cursor:
                # 基础查询
                base_query = """
                SELECT cr.card_no, s.peo_no, cr.date_time, cr.money, cr.dept 
                FROM consumption_records cr
                LEFT JOIN students s ON cr.card_no = s.card_no
                WHERE 1=1
                """
                params = []
                
                # 添加筛选条件
                conditions = []
                if card_no:
                    conditions.append("cr.card_no = %s")
                    params.append(card_no)
                
                if start_date:
                    conditions.append("DATE(cr.date_time) >= %s")
                    params.append(start_date)
                
                if end_date:
                    conditions.append("DATE(cr.date_time) <= %s")
                    params.append(end_date)
                
                # 拼接条件
                if conditions:
                    base_query += " AND " + " AND ".join(conditions)
                
                # 添加排序和限制
                base_query += " ORDER BY cr.date_time DESC LIMIT %s"
                params.append(limit)
                
                print(f"执行查询:\n{base_query}")
                print(f"参数: {params}")
                
                # 执行查询
                cursor.execute(base_query, params)
                records = cursor.fetchall()
                
                return records
        except Exception as e:
            print(f"查询错误: {str(e)}")
            return []
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def get_sample_card_numbers(limit=5):
        """获取示例校园卡号"""
        connection = None
        try:
            connection = ConsumptionQueryTest.get_db_connection()
            with connection.cursor() as cursor:
                query = "SELECT DISTINCT card_no FROM consumption_records WHERE card_no != 'card_no' ORDER BY card_no LIMIT %s"
                cursor.execute(query, [limit])
                return [row['card_no'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"获取卡号错误: {str(e)}")
            return []
        finally:
            if connection:
                connection.close()

# 演示查询消费记录
def main():
    print("===== 消费记录查询演示 =====\n")
    
    # 获取示例卡号
    sample_cards = ConsumptionQueryTest.get_sample_card_numbers()
    print(f"示例校园卡号: {sample_cards}\n")
    
    # 1. 查询最新的10条消费记录
    print("1. 查询最新的10条消费记录:")
    records = ConsumptionQueryTest.query_consumption_records(limit=10)
    print(f"查询结果 ({len(records)}条):")
    for record in records[:3]:  # 只显示前3条
        print(f"  - 卡号: {record['card_no']}, 学号: {record['peo_no'] or '未知'}, 时间: {record['date_time']}, 金额: {record['money']}, 部门: {record['dept']}")
    print()
    
    # 2. 按校园卡号查询
    if sample_cards:
        card_no = sample_cards[0]
        print(f"2. 按校园卡号 {card_no} 查询:")
        records = ConsumptionQueryTest.query_consumption_records(card_no=card_no, limit=5)
        print(f"查询结果 ({len(records)}条):")
        for record in records:
            print(f"  - 时间: {record['date_time']}, 金额: {record['money']}, 部门: {record['dept']}")
        print()
    
    # 3. 按日期范围查询（2019年4月的消费记录）
    print("3. 查询2019年4月的消费记录:")
    records = ConsumptionQueryTest.query_consumption_records(start_date='2019-04-01', end_date='2019-04-30', limit=5)
    print(f"查询结果 ({len(records)}条):")
    for record in records:
        print(f"  - 卡号: {record['card_no']}, 时间: {record['date_time']}, 金额: {record['money']}, 部门: {record['dept']}")
    print()
    
    # 4. 组合条件查询
    if sample_cards:
        card_no = sample_cards[0]
        print(f"4. 组合条件查询（卡号: {card_no}, 日期: 2019-04-01至2019-04-10）:")
        records = ConsumptionQueryTest.query_consumption_records(
            card_no=card_no, 
            start_date='2019-04-01', 
            end_date='2019-04-10', 
            limit=5
        )
        print(f"查询结果 ({len(records)}条):")
        for record in records:
            print(f"  - 时间: {record['date_time']}, 金额: {record['money']}, 部门: {record['dept']}")
    
    print("\n===== 查询演示完成 =====")

if __name__ == "__main__":
    main()