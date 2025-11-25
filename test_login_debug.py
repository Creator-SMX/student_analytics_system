#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
登录功能调试脚本
直接测试登录函数，不通过Flask应用
"""

from auth.models import verify_admin

def test_admin_login():
    """测试管理员登录"""
    print("\n===== 测试管理员登录 =====")
    admin_username = 'admin'
    admin_password = '123456'
    
    print(f"尝试登录管理员账号: {admin_username} / {admin_password}")
    admin = verify_admin(admin_username, admin_password)
    
    if admin:
        print("✓ 管理员登录成功")
        print(f"管理员信息: {admin}")
    else:
        print("✗ 管理员登录失败")
    
    return admin

# 学生登录功能已移除，系统不再支持学生登录

def check_database_connection():
    """检查数据库连接"""
    print("\n===== 检查数据库连接 =====")
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✓ 数据库连接成功")
        
        # 检查必要的表是否存在
        with connection.cursor() as cursor:
            # 检查学生表
            cursor.execute("SHOW TABLES LIKE 'students'")
            has_students_table = cursor.fetchone() is not None
            print(f"学生表存在: {has_students_table}")
            
            # 检查管理员表
            cursor.execute("SHOW TABLES LIKE 'admins'")
            has_admins_table = cursor.fetchone() is not None
            print(f"管理员表存在: {has_admins_table}")
            
            # 如果表存在，检查是否有数据
            if has_students_table:
                cursor.execute("SELECT COUNT(*) as count FROM students")
                student_count = cursor.fetchone()['count']
                print(f"学生表记录数: {student_count}")
            
            if has_admins_table:
                cursor.execute("SELECT COUNT(*) as count FROM admins")
                admin_count = cursor.fetchone()['count']
                print(f"管理员表记录数: {admin_count}")
                
                # 显示管理员账号信息（隐藏密码）
                cursor.execute("SELECT username FROM admins")
                admins = cursor.fetchall()
                print(f"管理员账号列表: {[a['username'] for a in admins]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("===== 开始登录功能调试 =====")
    
    # 1. 先检查数据库连接
    if not check_database_connection():
        print("\n数据库连接失败，无法继续测试登录功能")
        return
    
    # 2. 测试管理员登录
    admin = test_admin_login()
    
    # 3. 总结
    print("\n===== 调试总结 =====")
    print(f"管理员登录: {'成功' if admin else '失败'}")
    
    if not admin:
        print("\n问题分析:")
        print("1. 可能数据库中没有管理员账号信息")
        print("2. 可能密码验证逻辑有问题")
        print("3. 可能数据库连接配置不正确")
        print("\n建议:")
        print("1. 检查数据库中的admins表数据")
        print("2. 确认密码存储格式（明文或MD5）")
        print("3. 检查数据库连接参数是否正确")

if __name__ == '__main__':
    main()