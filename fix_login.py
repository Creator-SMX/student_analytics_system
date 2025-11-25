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

# 简单日志函数
def log(message, level='INFO'):
    print(f"[{level}] {message}")

# 直接修改auth/models.py文件
def fix_models_file():
    try:
        # 定义文件路径
        models_path = 'd:\\Pycharm\\PcData\\student_analytics_system\\auth\\models.py'
        
        # 新的正确代码内容
        new_content = """
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
学生行为分析系统 - 认证模型
"""

import mysql.connector
from mysql.connector import Error
import hashlib

# 数据库配置 - 修复版
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
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        # 修复SQL查询语句
        query = "SELECT * FROM admins WHERE username = %s AND password = %s AND status = 'active'"
        cursor.execute(query, (username, password_hash))
        admin = cursor.fetchone()
        
        return admin is not None
    except Exception as e:
        print(f"验证管理员时出错: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_admin_by_username(username):
    """根据用户名获取管理员信息"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM admins WHERE username = %s AND status = 'active'"
        cursor.execute(query, (username,))
        admin = cursor.fetchone()
        
        return admin
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
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        # 修复SQL查询语句 - 使用正确的表名
        query = "SELECT * FROM students WHERE card_no = %s AND password = %s AND status = 'active'"
        cursor.execute(query, (card_no, password_hash))
        student = cursor.fetchone()
        
        return student
    except Exception as e:
        print(f"验证学生时出错: {e}")
        return None

def update_admin_password(username, new_password):
    """更新管理员密码"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return False
            
        cursor = connection.cursor()
        password_hash = hashlib.md5(new_password.encode()).hexdigest()
        
        query = "UPDATE admins SET password = %s WHERE username = %s"
        cursor.execute(query, (password_hash, username))
        connection.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"更新管理员密码时出错: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def update_student_password(card_no, new_password):
    """更新学生密码"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return False
            
        cursor = connection.cursor()
        password_hash = hashlib.md5(new_password.encode()).hexdigest()
        
        query = "UPDATE students SET password = %s WHERE card_no = %s"
        cursor.execute(query, (password_hash, card_no))
        connection.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"更新学生密码时出错: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
        """
        
        # 写入新内容到文件
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        log("成功修复auth/models.py文件", "SUCCESS")
        return True
    except Exception as e:
        log(f"修复models.py文件失败: {str(e)}", "ERROR")
        return False

# 创建默认管理员账号
def create_default_admin():
    try:
        # 直接连接数据库创建管理员账号
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics'
        )
        
        cursor = connection.cursor()
        
        # 创建管理员表（如果不存在）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(32) NOT NULL,
            email VARCHAR(100),
            role VARCHAR(20) DEFAULT 'admin',
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_sql)
        
        # 创建默认管理员账号
        admin_username = 'admin'
        admin_password = 'admin123'
        password_hash = hashlib.md5(admin_password.encode()).hexdigest()
        
        # 检查是否已存在
        cursor.execute("SELECT * FROM admins WHERE username = %s", (admin_username,))
        if not cursor.fetchone():
            query = "INSERT INTO admins (username, password, role, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (admin_username, password_hash, 'admin', 'active'))
            connection.commit()
            log(f"已创建默认管理员账号: {admin_username} / {admin_password}", "SUCCESS")
        else:
            log(f"管理员账号 {admin_username} 已存在", "INFO")
        
        # 创建测试账号
        test_username = 'test_admin'
        test_password = 'admin123'
        password_hash = hashlib.md5(test_password.encode()).hexdigest()
        
        cursor.execute("SELECT * FROM admins WHERE username = %s", (test_username,))
        if not cursor.fetchone():
            query = "INSERT INTO admins (username, password, role, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (test_username, password_hash, 'admin', 'active'))
            connection.commit()
            log(f"已创建测试管理员账号: {test_username} / {test_password}", "SUCCESS")
        else:
            log(f"测试管理员账号 {test_username} 已存在", "INFO")
        
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        log(f"创建管理员账号失败: {str(e)}", "ERROR")
        return False

# 创建测试脚本
def create_test_script():
    try:
        test_script = """
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
登录测试工具
"""

import requests
import json

def test_login(username, password, user_type='admin'):
    print(f"测试登录: {username} / {password} (类型: {user_type})")
    try:
        url = 'http://localhost:5000/auth/login'
        payload = {'username': username, 'password': password, 'user_type': user_type}
        
        print(f"发送请求到: {url}")
        print(f"请求数据: {payload}")
        
        response = requests.post(url, json=payload)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        try:
            data = response.json()
            print(f"解析后的JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print("无法解析为JSON")
            
    except Exception as e:
        print(f"登录测试失败: {str(e)}")

def test_direct_connection():
    """测试直接连接数据库"""
    print("\n测试直接连接数据库...")
    try:
        import mysql.connector
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics'
        )
        print("数据库连接成功！")
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
        # 检查管理员表
        cursor.execute("SELECT * FROM admins LIMIT 5")
        admins = cursor.fetchall()
        print(f"管理员数量: {len(admins)}")
        
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"数据库连接测试失败: {str(e)}")
        return False

if __name__ == '__main__':
    print("====== 登录测试工具 ======")
    print("请确保Flask服务器已启动")
    
    # 先测试直接连接数据库
    test_direct_connection()
    
    print("\n测试管理员登录:")
    test_login('admin', 'admin123', 'admin')
    
    print("\n测试测试账号登录:")
    test_login('test_admin', 'admin123', 'admin')
    """
        
        with open('test_login.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
            
        log("已生成测试登录脚本: test_login.py", "SUCCESS")
        return True
    except Exception as e:
        log(f"创建测试脚本失败: {str(e)}", "ERROR")
        return False

# 主函数
def main():
    log("极简认证系统修复工具启动")
    
    # 1. 修复models.py文件
    log("\n1. 修复认证模型文件...")
    fix_models_file()
    
    # 2. 创建默认管理员账号
    log("\n2. 创建管理员账号...")
    create_default_admin()
    
    # 3. 创建测试脚本
    log("\n3. 创建测试工具...")
    create_test_script()
    
    log("\n====== 修复完成 ======", "SUCCESS")
    log("1. 已修复auth/models.py文件中的数据库连接和验证函数", "INFO")
    log("2. 已创建管理员账号: admin / admin123", "INFO")
    log("3. 已创建测试账号: test_admin / admin123", "INFO")
    log("4. 已生成测试工具: test_login.py", "INFO")
    log("\n请按照以下步骤继续:", "INFO")
    log("1. 重启Flask服务器: python app.py", "INFO")
    log("2. 运行登录测试: python test_login.py", "INFO")
    log("3. 在浏览器中访问登录页面", "INFO")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())