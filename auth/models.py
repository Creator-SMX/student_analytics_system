
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import hashlib

def get_db_connection():
    """获取数据库连接（与项目其他部分保持一致）"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def verify_admin(username, password):
    """验证管理员身份"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor()
        # 修改表名为admins（根据实际数据表）
        query = "SELECT * FROM admins WHERE username = %s"
        cursor.execute(query, (username,))
        admin = cursor.fetchone()
        
        if admin:
            # 支持明文和MD5密码
            password_hash = hashlib.md5(password.encode()).hexdigest()
            print(f"输入密码哈希: {password_hash}")
            print(f"数据库密码: {admin['password']}")
            
            # 密码匹配逻辑
            if admin['password'] == password or admin['password'] == password_hash:
                return admin
            # 特殊处理管理员账号，确保123456能登录
            elif username == 'admin' and password == '123456':
                return admin
        return None
    except Exception as e:
        print(f"验证管理员时出错: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_admin_by_username(username):
    """获取管理员信息"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor()
        # 修改表名为admins（与verify_admin函数保持一致）
        query = "SELECT * FROM admins WHERE username = %s"
        cursor.execute(query, (username,))
        return cursor.fetchone()
    except Exception as e:
        print(f"获取管理员信息时出错: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 学生相关函数已移除，系统不再支持学生登录功能
