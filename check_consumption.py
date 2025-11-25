import pymysql

# 连接数据库
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='student_analytics',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with conn.cursor() as cursor:
        # 检查消费记录总数
        cursor.execute('SELECT COUNT(*) as total FROM consumption_records')
        total_result = cursor.fetchone()
        print(f'消费记录总数: {total_result["total"]}')
        
        # 检查金额范围
        cursor.execute('SELECT MIN(money) as min_money, MAX(money) as max_money FROM consumption_records')
        range_result = cursor.fetchone()
        print(f'金额范围: {range_result["min_money"]} 到 {range_result["max_money"]}')
        
        # 检查价格区间分布
        price_distribution_sql = """
        SELECT 
            CASE 
                WHEN money >= 0 AND money < 5 THEN '0-5元'
                WHEN money >= 5 AND money < 10 THEN '5-10元'
                WHEN money >= 10 AND money < 20 THEN '10-20元'
                WHEN money >= 20 AND money < 50 THEN '20-50元'
                ELSE '50元以上'
            END as price_range,
            COUNT(*) as count
        FROM 
            consumption_records 
        WHERE 
            money >= 0
        GROUP BY 
            price_range
        ORDER BY 
            MIN(money)
        """
        
        cursor.execute(price_distribution_sql)
        price_results = cursor.fetchall()
        print('价格区间分布:')
        for row in price_results:
            print(f'{row["price_range"]}: {row["count"]}次')
            
except Exception as e:
    print(f"连接数据库失败: {str(e)}")
finally:
    if 'conn' in locals() and conn is not None:
        conn.close()