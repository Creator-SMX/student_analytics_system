#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""数据库连接测试脚本"""
import pymysql
import sys

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'student_analytics'
}

def test_mysql_connection():
    """测试MySQL连接"""
    try:
        print("尝试连接到MySQL数据库...")
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ 成功连接到MySQL数据库!")
        
        # 测试执行简单查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ 查询测试成功: {result}")
            
            # 尝试列出数据库中的表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ 数据库中的表: {[table[0] for table in tables]}")
        
        connection.close()
        return True
    except Exception as e:
        print(f"❌ MySQL连接失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_db_connection_class():
    """测试DatabaseConnection类"""
    try:
        print("\n尝试使用DatabaseConnection类...")
        from utils.db_connection import DatabaseConnection
        
        db = DatabaseConnection(
            host='localhost',
            user='root', 
            password='123456', 
            database='student_analytics'
        )
        
        if db.connect():
            print("✅ DatabaseConnection类初始化成功!")
            # 测试获取数据
            df = db.get_dataframe("SELECT 1")
            if df is not None:
                print("✅ 成功获取DataFrame数据!")
            db.disconnect()
            return True
        else:
            print("❌ DatabaseConnection类连接失败!")
            return False
    except Exception as e:
        print(f"❌ DatabaseConnection类测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_imports():
    """检查必要的导入"""
    print("\n检查必要的导入...")
    required_modules = ['flask', 'pandas', 'pymysql', 'flask_cors']
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} 导入成功")
        except ImportError as e:
            print(f"❌ {module} 导入失败: {str(e)}")

def main():
    """主函数"""
    print("=== 数据库连接测试脚本 ===")
    
    # 检查Python版本
    print(f"\nPython版本: {sys.version}")
    
    # 检查必要的导入
    check_imports()
    
    # 测试MySQL连接
    test_mysql_connection()
    
    # 测试DatabaseConnection类
    test_db_connection_class()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()