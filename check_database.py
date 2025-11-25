#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""数据库检查脚本"""
import pymysql
import traceback

def check_database_connection():
    """检查数据库连接状态"""
    print("=== 开始检查数据库连接 ===")
    try:
        # 使用与db_connection.py中相同的配置
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ 数据库连接成功！")
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        traceback.print_exc()
        return None

def check_tables_existence(conn):
    """检查必需的表是否存在"""
    print("\n=== 检查数据库表是否存在 ===")
    required_tables = ['access_records', 'admins', 'consumption_records', 'students']
    missing_tables = []
    
    try:
        with conn.cursor() as cursor:
            # 查询数据库中的所有表
            cursor.execute("SHOW TABLES")
            existing_tables = [table[f'Tables_in_{conn.db}'] for table in cursor.fetchall()]
            
            print(f"数据库中的表: {', '.join(existing_tables)}")
            
            # 检查必需的表是否存在
            for table in required_tables:
                if table in existing_tables:
                    print(f"✅ 表 '{table}' 存在")
                else:
                    print(f"❌ 表 '{table}' 不存在")
                    missing_tables.append(table)
    
        return missing_tables
    except Exception as e:
        print(f"❌ 检查表存在性时出错: {str(e)}")
        traceback.print_exc()
        return required_tables  # 假设所有表都缺失

def check_table_structure(conn, table_name):
    """检查表的字段结构"""
    print(f"\n=== 检查表 '{table_name}' 的结构 ===")
    try:
        with conn.cursor() as cursor:
            # 获取表结构
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            print(f"表 '{table_name}' 包含 {len(columns)} 个字段:")
            for col in columns:
                print(f"  - {col['Field']}: {col['Type']} {'(主键)' if col['Key'] == 'PRI' else ''}")
            
            return columns
    except Exception as e:
        print(f"❌ 检查 '{table_name}' 表结构时出错: {str(e)}")
        traceback.print_exc()
        return None

def check_sample_data(conn, table_name, limit=5):
    """检查表中的示例数据"""
    print(f"\n=== 检查表 '{table_name}' 的示例数据 ===")
    try:
        with conn.cursor() as cursor:
            # 获取表中的行数
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            total_rows = cursor.fetchone()['count']
            print(f"表 '{table_name}' 共有 {total_rows} 条记录")
            
            # 如果有数据，获取前几行作为示例
            if total_rows > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
                sample_data = cursor.fetchall()
                print(f"前 {len(sample_data)} 条记录:")
                # 打印字段名
                if sample_data:
                    print(" | ".join([str(key) for key in sample_data[0].keys()]))
                    print("-" * 50)
                    # 打印数据行
                    for row in sample_data:
                        print(" | ".join([str(value)[:20] + '...' if len(str(value)) > 20 else str(value) for value in row.values()]))
    except Exception as e:
        print(f"❌ 检查 '{table_name}' 表数据时出错: {str(e)}")
        traceback.print_exc()

def main():
    """主函数"""
    # 检查数据库连接
    conn = check_database_connection()
    if not conn:
        print("数据库检查失败，无法继续")
        return
    
    try:
        # 检查表是否存在
        missing_tables = check_tables_existence(conn)
        if missing_tables:
            print(f"\n❌ 错误: 缺少以下必需的表: {', '.join(missing_tables)}")
        else:
            print("\n✅ 所有必需的表都存在")
            
            # 检查每个表的结构和数据
            tables_to_check = ['access_records', 'admins', 'consumption_records', 'students']
            for table in tables_to_check:
                check_table_structure(conn, table)
                check_sample_data(conn, table)
    
    finally:
        # 关闭连接
        if conn:
            conn.close()
            print("\n✅ 数据库连接已关闭")

if __name__ == "__main__":
    main()