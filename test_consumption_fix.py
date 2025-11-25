import pymysql

def test_consumption_query():
    """测试消费记录查询逻辑"""
    connection = None
    try:
        # 创建数据库连接
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            print("执行原始查询（不关联学生表）...")
            query = """
            SELECT cr.card_no, cr.peo_no, cr.date_time, cr.money, cr.dept 
            FROM consumption_records cr
            WHERE 1=1
            ORDER BY cr.date_time DESC
            LIMIT 10
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            print(f"查询结果数量: {len(results)}")
            if results:
                print("查询成功！前3条记录：")
                for i, record in enumerate(results[:3]):
                    print(f"记录 {i+1}:")
                    print(f"  校园卡号: {record.get('card_no')}")
                    print(f"  学号: {record.get('peo_no')}")
                    print(f"  消费时间: {record.get('date_time')}")
                    print(f"  消费金额: {record.get('money')}")
                    print(f"  消费地点: {record.get('dept')}")
            else:
                print("查询未返回数据")
                
            # 测试带筛选条件的查询
            print("\n测试带筛选条件的查询（卡号181316）...")
            query = """
            SELECT cr.card_no, cr.peo_no, cr.date_time, cr.money, cr.dept 
            FROM consumption_records cr
            WHERE cr.card_no = '181316'
            ORDER BY cr.date_time DESC
            LIMIT 10
            """
            cursor.execute(query)
            filtered_results = cursor.fetchall()
            print(f"筛选结果数量: {len(filtered_results)}")
            
    except Exception as e:
        print(f"查询过程中发生错误: {str(e)}")
    finally:
        if connection:
            connection.close()
            print("\n数据库连接已关闭")

if __name__ == "__main__":
    test_consumption_query()