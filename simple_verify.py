#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最简单的数据库验证脚本
只执行单一查询来获取消费人数
"""

try:
    import pymysql
    print("pymysql模块导入成功")
except ImportError:
    print("错误: 请先安装pymysql模块: pip install pymysql")
    import sys
    sys.exit(1)

def main():
    """
    主函数：执行简单查询
    """
    print("开始简单验证...")
    
    # 数据库连接参数
    host = 'localhost'
    user = 'root'
    password = '123456'
    database = 'student_analytics'
    
    try:
        # 尝试建立连接
        print(f"尝试连接到数据库 {database} ...")
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        print("数据库连接成功!")
        
        # 创建游标
        cursor = conn.cursor()
        
        # 执行简单查询
        print("\n执行查询: SELECT COUNT(DISTINCT card_number) FROM consumption_records")
        cursor.execute("SELECT COUNT(DISTINCT card_number) FROM consumption_records")
        
        # 获取结果
        result = cursor.fetchone()
        if result:
            count = result[0]
            print(f"\n查询结果: 去重后的消费者总数 = {count}")
        else:
            print("\n未获取到查询结果")
            
    except Exception as e:
        print(f"\n发生错误: {type(e).__name__}: {str(e)}")
    finally:
        # 关闭连接
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
                print("\n数据库连接已关闭")
        except:
            pass

if __name__ == "__main__":
    main()