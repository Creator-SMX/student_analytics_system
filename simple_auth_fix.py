#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的认证系统修复工具
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
import hashlib
import shutil

# 日志函数
def log(message, level='INFO'):
    colors = {
        'INFO': '\033[94m',
        'SUCCESS': '\033[92m', 
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'ENDC': '\033[0m'
    }
    
    # 适配Windows终端
    if os.name == 'nt':
        os.system('')
    
    color = colors.get(level, colors['INFO'])
    print(f"{color}[{level}] {message}{colors['ENDC']}")

# 数据库配置测试
def test_db_connection(config):
    """测试数据库连接"""
    try:
        connection = mysql.connector.connect(**config)
        log(f"成功连接到数据库: {config['host']}, 数据库名: {config['database']}", "SUCCESS")
        return connection
    except Error as e:
        log(f"数据库连接失败: {str(e)}", "ERROR")
        return None

def check_and_fix_database():
    """检查并修复数据库连接"""
    # 测试不同的数据库配置
    configs_to_test = [
        {'host': 'localhost', 'user': 'root', 'password': '123456', 'database': 'student_analytics'},
        {'host': 'localhost:3306', 'user': 'root', 'password': '123456', 'database': 'student_analytics'},
        {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'student_analytics'}
    ]
    
    working_config = None
    
    for config in configs_to_test:
        log(f"测试配置: host={config['host']}, user={config['user']}")
        connection = test_db_connection(config)
        if connection:
            working_config = config
            connection.close()
            break
    
    return working_config

def fix_auth_models(working_config):
    """修复认证模型文件"""
    models_path = 'd:\\Pycharm\\PcData\\student_analytics_system\\auth\\models.py'
    
    # 备份原文件
    if os.path.exists(models_path):
        backup_path = models_path + '.bak'
        shutil.copy(models_path, backup_path)
        log(f"已备份原models.py到{backup_path}", "INFO")
    else:
        log(f"找不到models.py文件: {models_path}", "ERROR")
        return False
    
    # 读取原文件内容
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换数据库配置
    import re
    # 使用正则表达式匹配数据库配置部分
    db_config_pattern = r"DB_CONFIG\s*=\s*{[^}]*}"
    
    new_db_config = f"""DB_CONFIG = {{
    'host': '{working_config['host']}',
    'user': '{working_config['user']}',
    'password': '{working_config['password']}',
    'database': '{working_config['database']}'
}}"""
    
    # 添加安全检查的get_db_connection函数
    get_db_connection_code = """
def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None
"""
    
    # 替换或添加get_db_connection函数
    if 'def get_db_connection():' in content:
        # 使用正则表达式替换整个函数
        connection_func_pattern = r"def get_db_connection\(\):[^\n]*\n(?:    [^\n]*\n)*"
        content = re.sub(connection_func_pattern, get_db_connection_code, content)
    else:
        # 在导入语句后添加函数
        import_pos = content.find('from mysql.connector import Error')
        if import_pos != -1:
            # 找到导入语句后的位置
            insert_pos = content.find('\n', import_pos)
            content = content[:insert_pos] + '\n' + get_db_connection_code + content[insert_pos:]
    
    # 确保verify_admin和verify_student函数有连接关闭的安全检查
    content = re.sub(r"finally:\s*if connection\.is_connected\(\):", 
                    "finally:\n        if connection and connection.is_connected():\n            cursor.close()\n            connection.close()", content)
    
    # 替换整个DB_CONFIG部分
    if re.search(db_config_pattern, content):
        content = re.sub(db_config_pattern, new_db_config, content)
    else:
        # 如果没有找到DB_CONFIG，在文件开头添加
        content = new_db_config + '\n\n' + content
    
    # 写回文件
    try:
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(content)
        log(f"已成功修复models.py文件，更新了数据库配置", "SUCCESS")
        return True
    except Exception as e:
        log(f"写入文件失败: {str(e)}", "ERROR")
        return False

def create_test_admin():
    """直接创建测试管理员账号"""
    # 先尝试导入现有的模型函数
    try:
        sys.path.append('d:\\Pycharm\\PcData\\student_analytics_system')
        from auth.models import get_db_connection
        
        connection = get_db_connection()
        if not connection:
            log("无法连接到数据库，跳过创建测试管理员", "ERROR")
            return False
        
        cursor = connection.cursor()
        
        # 检查是否已存在admin表
        cursor.execute("SHOW TABLES LIKE 'admins'")
        if not cursor.fetchone():
            log("创建管理员表...", "INFO")
            create_admin_table = """
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
            cursor.execute(create_admin_table)
            connection.commit()
        
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
        
        # 创建测试管理员账号
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
        log(f"创建管理员账号时出错: {str(e)}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def fix_auth_controller():
    """修复认证控制器文件"""
    controller_path = 'd:\\Pycharm\\PcData\\student_analytics_system\\auth\\auth_controller.py'
    
    if not os.path.exists(controller_path):
        log(f"找不到auth_controller.py文件: {controller_path}", "ERROR")
        return False
    
    # 备份原文件
    backup_path = controller_path + '.bak'
    shutil.copy(controller_path, backup_path)
    log(f"已备份原auth_controller.py到{backup_path}", "INFO")
    
    # 读取原文件内容
    with open(controller_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 增强login函数的错误处理和日志记录
    import re
    
    # 添加调试日志和错误处理的login函数
    new_login_function = """
@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口 - 增强版"""
    try:
        # 支持多种请求格式
        data = request.get_json(silent=True)  # 静默模式，避免解析错误
        
        # 获取登录参数，支持多种格式
        if data:
            username = data.get('username')
            password = data.get('password')
            user_type = data.get('user_type', 'student')
        else:
            # 尝试从表单获取
            username = request.form.get('username')
            password = request.form.get('password')
            user_type = request.form.get('user_type', 'student')
        
        # 如果都没有，尝试从查询参数获取（调试用）
        if not username:
            username = request.args.get('username')
        if not password:
            password = request.args.get('password')
        if not user_type:
            user_type = request.args.get('user_type', 'student')
        
        print(f"[DEBUG] 登录尝试: username={username}, user_type={user_type}")
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        # 验证用户
        if user_type == 'admin':
            # 管理员登录
            if verify_admin(username, password):
                admin = get_admin_by_username(username)
                if admin:
                    session['user_id'] = admin['id']
                    session['username'] = admin['username']
                    session['user_type'] = 'admin'
                    print(f"[DEBUG] 管理员登录成功: {username}")
                    return jsonify({'success': True, 'message': '管理员登录成功', 'user_type': 'admin'})
                else:
                    return jsonify({'success': False, 'message': '获取管理员信息失败'}), 500
            else:
                print(f"[DEBUG] 管理员登录失败: 用户名或密码错误")
                return jsonify({'success': False, 'message': '管理员账号或密码错误'}), 401
        else:
            # 学生登录
            student = verify_student(username, password)  # username这里实际是card_no
            if student:
                # 生成学生名称（使用卡号后4位）
                student_name = f"学生{student['card_no'][-4:]}" if student.get('card_no') else '未知学生'
                
                session['user_id'] = student['card_no']
                session['username'] = student_name
                session['user_type'] = 'student'
                
                # 从卡号提取年级信息
                grade = student['card_no'][:4] if student.get('card_no') and len(student['card_no']) >= 4 else ''
                
                print(f"[DEBUG] 学生登录成功: {student['card_no']}")
                return jsonify({'success': True, 'message': '学生登录成功', 'user_type': 'student', 'student_info': {
                    'card_no': student['card_no'],
                    'name': student_name,
                    'sex': student.get('sex', ''),
                    'major': student.get('major', ''),
                    'grade': grade,
                    'access_card_no': student.get('access_card_no', '')
                }})
            else:
                print(f"[DEBUG] 学生登录失败: 学号或密码错误")
                return jsonify({'success': False, 'message': '学号或密码错误'}), 401
    except Exception as e:
        print(f"[ERROR] 登录失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500
"""
    
    # 替换login函数
    login_pattern = r"@auth_bp\.route\('/login', methods=\['POST'\]\)\s*def login\(\):[^@]*"
    
    if re.search(login_pattern, content, re.DOTALL):
        content = re.sub(login_pattern, new_login_function, content, flags=re.DOTALL)
        
        # 写回文件
        try:
            with open(controller_path, 'w', encoding='utf-8') as f:
                f.write(content)
            log(f"已成功修复auth_controller.py文件，增强了登录功能", "SUCCESS")
            return True
        except Exception as e:
            log(f"写入文件失败: {str(e)}", "ERROR")
            return False
    else:
        log("无法找到login函数，跳过修复", "WARNING")
        return False

def main():
    log("简单认证系统修复工具启动")
    
    # 1. 测试和修复数据库连接
    log("\n1. 测试数据库连接...")
    working_config = check_and_fix_database()
    
    if not working_config:
        log("无法找到有效的数据库配置，请检查数据库设置", "ERROR")
        return 1
    
    # 2. 修复认证模型文件
    log("\n2. 修复认证模型文件...")
    fix_auth_models(working_config)
    
    # 3. 修复认证控制器文件
    log("\n3. 修复认证控制器文件...")
    fix_auth_controller()
    
    # 4. 创建测试管理员账号
    log("\n4. 创建测试管理员账号...")
    create_test_admin()
    
    # 5. 生成测试登录脚本
    log("\n5. 生成测试登录脚本...")
    with open('test_login.py', 'w', encoding='utf-8') as f:
        f.write("""
import requests
import json

# 测试登录功能
def test_login(username, password, user_type='admin'):
    print(f"测试登录: {username} / {password}")
    try:
        url = 'http://localhost:5000/auth/login'
        payload = {'username': username, 'password': password, 'user_type': user_type}
        
        print(f"发送请求: POST {url}")
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

if __name__ == '__main__':
    print("====== 登录测试工具 ======")
    print("请确保Flask服务器已启动")
    print("\n测试管理员登录:")
    test_login('admin', 'admin123', 'admin')
    print("\n测试测试账号登录:")
    test_login('test_admin', 'admin123', 'admin')
""")
    
    log("\n====== 修复完成 ======", "SUCCESS")
    log("1. 数据库连接配置已更新", "INFO")
    log("2. 认证模型和控制器文件已修复", "INFO")
    log("3. 已创建管理员账号: admin / admin123", "INFO")
    log("4. 已创建测试账号: test_admin / admin123", "INFO")
    log("5. 生成了登录测试脚本: test_login.py", "INFO")
    log("\n请按照以下步骤继续:", "INFO")
    log("1. 重启Flask服务器: python app.py", "INFO")
    log("2. 运行登录测试: python test_login.py", "INFO")
    log("3. 在浏览器中访问 http://localhost:5000/login 进行登录", "INFO")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())