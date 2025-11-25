#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
极简认证系统修复工具
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
import hashlib

# 修复auth/models.py文件
def fix_auth_models():
    try:
        # 简单的修复内容
        fixed_content = '''
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import hashlib

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'student_analytics'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def verify_admin(username, password):
    """验证管理员身份"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return False
            
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM admins WHERE username = %s AND status = 1"
        cursor.execute(query, (username,))
        admin = cursor.fetchone()
        
        if admin:
            # 支持明文和MD5密码
            if admin['password'] == password or admin['password'] == hashlib.md5(password.encode()).hexdigest():
                return True
        return False
    except Exception as e:
        print(f"验证管理员时出错: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_admin_by_username(username):
    """获取管理员信息"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM admins WHERE username = %s AND status = 1"
        cursor.execute(query, (username,))
        return cursor.fetchone()
    except Exception as e:
        print(f"获取管理员信息时出错: {e}")
        return None

def verify_student(card_no, password):
    """验证学生身份"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM students WHERE card_no = %s"
        cursor.execute(query, (card_no,))
        student = cursor.fetchone()
        
        if student:
            # 支持明文和MD5密码
            if student['password'] == password or student['password'] == hashlib.md5(password.encode()).hexdigest():
                return student
        return None
    except Exception as e:
        print(f"验证学生时出错: {e}")
        return None
'''
        
        # 写入文件
        models_path = 'auth/models.py'
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("[SUCCESS] 成功修复auth/models.py文件")
        return True
    except Exception as e:
        print(f"[ERROR] 修复models.py失败: {str(e)}")
        return False

# 创建管理员账号
def create_admin():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics'
        )
        
        cursor = connection.cursor()
        
        # 创建管理员账号
        admin_username = 'admin'
        admin_password = 'admin123'
        admin_name = '系统管理员'
        
        # 检查并更新或创建
        cursor.execute("SELECT * FROM admins WHERE username = %s", (admin_username,))
        if cursor.fetchone():
            query = "UPDATE admins SET password = %s, name = %s, role = 'admin', status = 1 WHERE username = %s"
            cursor.execute(query, (admin_password, admin_name, admin_username))
            print(f"[SUCCESS] 已更新管理员账号: {admin_username} / {admin_password}")
        else:
            query = "INSERT INTO admins (username, password, name, role, status) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (admin_username, admin_password, admin_name, 'admin', 1))
            print(f"[SUCCESS] 已创建管理员账号: {admin_username} / {admin_password}")
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"[ERROR] 创建管理员失败: {str(e)}")
        return False

# 主函数
def main():
    print("====== 极简认证修复工具 ======")
    
    # 修复认证模型
    print("\n1. 修复认证模型...")
    fix_auth_models()
    
    # 创建管理员账号
    print("\n2. 创建管理员账号...")
    create_admin()
    
    print("\n====== 修复完成 ======")
    print("1. 已修复认证模型文件")
    print("2. 已创建管理员账号: admin / admin123")
    print("\n请重启Flask服务器并尝试登录")

if __name__ == "__main__":
    main()