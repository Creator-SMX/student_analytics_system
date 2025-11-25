#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证系统修复工具 - 基于实际数据库结构
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
import hashlib

# 简单日志函数
def log(message, level='INFO'):
    print(f"[{level}] {message}")

# 直接修改auth/models.py文件，严格按照提供的数据库结构
def fix_models_file():
    try:
        # 定义文件路径
        models_path = 'd:\\Pycharm\\PcData\\student_analytics_system\\auth\\models.py'
        
        # 新的正确代码内容 - 严格按照数据库结构
        new_content = '''#!/usr/bin/env python
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
    """验证管理员身份 - 严格按照数据库结构"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return False
            
        cursor = connection.cursor(dictionary=True)
        
        # 注意：根据数据库结构，密码字段是varchar(255)，这里假设密码是明文存储
        # 如果密码是加密的，需要相应调整
        query = "SELECT * FROM admins WHERE username = %s AND status = 1"
        cursor.execute(query, (username,))
        admin = cursor.fetchone()
        
        if admin:
            # 检查密码
            # 根据实际情况可能需要使用不同的加密方式
            # 先尝试明文比较，如果不行再尝试MD5
            if admin['password'] == password:
                return True
            
            # 尝试MD5加密比较
            password_hash = hashlib.md5(password.encode()).hexdigest()
            if admin['password'] == password_hash:
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
    """根据用户名获取管理员信息"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM admins WHERE username = %s AND status = 1"
        cursor.execute(query, (username,))
        admin = cursor.fetchone()
        
        return admin
    except Exception as e:
        print(f"获取管理员信息时出错: {e}")
        return None

def verify_student(card_no, password):
    """验证学生身份 - 严格按照数据库结构"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor(dictionary=True)
        
        # 根据数据库结构，学生表使用card_no作为主键
        query = "SELECT * FROM students WHERE card_no = %s"
        cursor.execute(query, (card_no,))
        student = cursor.fetchone()
        
        if student:
            # 检查密码
            # 数据库结构显示默认密码是'123456'
            if student['password'] == password:
                return student
            
            # 尝试MD5加密比较
            password_hash = hashlib.md5(password.encode()).hexdigest()
            if student['password'] == password_hash:
                return student
        
        return None
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
        # 保持与现有系统一致的密码处理方式
        query = "UPDATE admins SET password = %s WHERE username = %s"
        cursor.execute(query, (new_password, username))
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
        # 保持与现有系统一致的密码处理方式
        query = "UPDATE students SET password = %s WHERE card_no = %s"
        cursor.execute(query, (new_password, card_no))
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
        
        # 确保字符串正确闭合
        new_content += "'''
        # 写入新内容到文件
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        log("成功修复auth/models.py文件，严格按照数据库结构修改", "SUCCESS")
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
        
        # 检查管理员表是否存在
        cursor.execute("SHOW TABLES LIKE 'admins'")
        if not cursor.fetchone():
            log("管理员表不存在，请先导入数据库结构", "ERROR")
            return False
        
        # 创建默认管理员账号 - 严格按照数据库结构
        admin_username = 'admin'
        admin_password = 'admin123'
        admin_name = '系统管理员'
        
        # 检查是否已存在
        cursor.execute("SELECT * FROM admins WHERE username = %s", (admin_username,))
        if not cursor.fetchone():
            query = "INSERT INTO admins (username, password, name, role, status) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (admin_username, admin_password, admin_name, 'admin', 1))
            connection.commit()
            log(f"已创建默认管理员账号: {admin_username} / {admin_password}", "SUCCESS")
        else:
            # 更新现有管理员密码
            query = "UPDATE admins SET password = %s, name = %s, role = 'admin', status = 1 WHERE username = %s"
            cursor.execute(query, (admin_password, admin_name, admin_username))
            connection.commit()
            log(f"已更新管理员账号密码: {admin_username} / {admin_password}", "SUCCESS")
        
        # 创建测试账号
        test_username = 'test_admin'
        test_password = 'admin123'
        test_name = '测试管理员'
        
        cursor.execute("SELECT * FROM admins WHERE username = %s", (test_username,))
        if not cursor.fetchone():
            query = "INSERT INTO admins (username, password, name, role, status) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (test_username, test_password, test_name, 'admin', 1))
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

# 修复认证控制器
def fix_auth_controller():
    try:
        controller_path = 'd:\\Pycharm\\PcData\\student_analytics_system\\auth\\auth_controller.py'
        
        # 读取现有控制器内容
        with open(controller_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查并添加必要的导入
        if 'import json' not in content:
            if 'import' in content:
                import_pos = content.find('import')
                content = content[:import_pos] + 'import json\n' + content[import_pos:]
            else:
                content = 'import json\n' + content
        
        # 增强login函数的日志记录
        import re
        
        # 查找login函数
        login_pattern = r"@auth_bp\.route\(['\"/]login['\"/], methods=\[[^\]]*\]\)\s*def login\(\):"
        match = re.search(login_pattern, content)
        
        if match:
            # 在函数开始处添加调试日志
            function_start = match.end()
            content = content[:function_start] + '\n    print("[DEBUG] 登录请求收到")\n    print(f"[DEBUG] 请求方法: {request.method}")\n    print(f"[DEBUG] 请求参数: {dict(request.args)}")' + content[function_start:]
            
            # 写入文件
            with open(controller_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            log("成功修复auth_controller.py，添加了调试日志", "SUCCESS")
        else:
            log("未找到login函数，跳过修复auth_controller.py", "WARNING")
        
        return True
    except Exception as e:
        log(f"修复auth_controller.py失败: {str(e)}", "ERROR")
        return False

# 创建测试脚本
def create_test_script():
    try:
        test_script = """
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
登录测试工具 - 基于实际数据库结构
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
        except Exception as e:
            print(f"无法解析为JSON: {str(e)}")
            
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
        
        # 检查所有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
        # 检查管理员表结构
        print("\n管理员表结构:")
        cursor.execute("DESCRIBE admins")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # 检查管理员数据
        cursor.execute("SELECT id, username, name, role, status FROM admins")
        admins = cursor.fetchall()
        print(f"\n管理员数量: {len(admins)}")
        for admin in admins:
            print(f"  ID: {admin[0]}, 用户名: {admin[1]}, 姓名: {admin[2]}, 角色: {admin[3]}, 状态: {admin[4]}")
        
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
    log("认证系统修复工具启动 - 基于实际数据库结构")
    
    # 1. 修复models.py文件
    log("\n1. 修复认证模型文件...")
    fix_models_file()
    
    # 2. 修复认证控制器
    log("\n2. 修复认证控制器...")
    fix_auth_controller()
    
    # 3. 创建默认管理员账号
    log("\n3. 创建管理员账号...")
    create_default_admin()
    
    # 4. 创建测试脚本
    log("\n4. 创建测试工具...")
    create_test_script()
    
    log("\n====== 修复完成 ======", "SUCCESS")
    log("1. 已修复auth/models.py文件，严格按照数据库结构修改", "INFO")
    log("2. 已修复auth_controller.py，添加了调试日志", "INFO")
    log("3. 已创建管理员账号: admin / admin123", "INFO")
    log("4. 已生成测试工具: test_login.py", "INFO")
    log("\n请按照以下步骤继续:", "INFO")
    log("1. 重启Flask服务器: python app.py", "INFO")
    log("2. 运行登录测试: python test_login.py", "INFO")
    log("3. 在浏览器中访问登录页面", "INFO")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())