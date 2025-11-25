#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库连接和认证检查工具
"""

import os
import sys
import hashlib
import mysql.connector
from mysql.connector import Error

# 配置输出颜色
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# 适配Windows终端
if os.name == 'nt':
    os.system('')  # 初始化Windows控制台

# 日志函数
def log(message, level='INFO'):
    color = Colors.ENDC
    if level == 'INFO':
        color = Colors.OKBLUE
    elif level == 'SUCCESS':
        color = Colors.OKGREEN
    elif level == 'WARNING':
        color = Colors.WARNING
    elif level == 'ERROR':
        color = Colors.FAIL
    print(f"{color}{message}{Colors.ENDC}")

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'student_analytics'
}

# 测试不同的数据库配置
DB_CONFIGS_TO_TEST = [
    # 默认配置
    {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'student_analytics'
    },
    # 备选配置1 - 默认端口
    {
        'host': 'localhost:3306',
        'user': 'root',
        'password': '123456',
        'database': 'student_analytics'
    },
    # 备选配置2 - 空密码
    {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'student_analytics'
    },
    # 备选配置3 - 不同的数据库名
    {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'student_analysis'
    }
]

def test_db_connections():
    """测试数据库连接"""
    log("====== 测试数据库连接 ======", "INFO")
    
    working_config = None
    
    for i, config in enumerate(DB_CONFIGS_TO_TEST):
        log(f"测试连接配置 {i+1}: host={config['host']}, user={config['user']}, db={config['database']}", "INFO")
        try:
            # 先尝试连接到MySQL服务器（不指定数据库）
            server_config = config.copy()
            db_name = server_config.pop('database')
            
            connection = mysql.connector.connect(**server_config)
            log(f"✓ 成功连接到MySQL服务器", "SUCCESS")
            
            # 检查数据库是否存在
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
            if cursor.fetchone():
                log(f"✓ 数据库 '{db_name}' 存在", "SUCCESS")
                # 重新连接到指定数据库
                connection.close()
                connection = mysql.connector.connect(**config)
                log(f"✓ 成功连接到数据库 '{db_name}'", "SUCCESS")
                working_config = config
                cursor.close()
                connection.close()
                break
            else:
                log(f"✗ 数据库 '{db_name}' 不存在", "ERROR")
                cursor.close()
                connection.close()
                
        except Error as e:
            log(f"✗ 连接失败: {str(e)}", "ERROR")
    
    return working_config

def check_tables(connection):
    """检查必要的表是否存在"""
    log("\n====== 检查表结构 ======", "INFO")
    
    required_tables = ['students', 'admins', 'consumption_records', 'access_records']
    missing_tables = []
    
    try:
        cursor = connection.cursor()
        
        for table in required_tables:
            cursor.execute("SHOW TABLES LIKE %s", (table,))
            if cursor.fetchone():
                log(f"✓ 表 '{table}' 存在", "SUCCESS")
                
                # 显示表的列信息
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                log(f"  表 '{table}' 有 {len(columns)} 个字段: {', '.join([col[0] for col in columns])}", "INFO")
            else:
                log(f"✗ 表 '{table}' 不存在", "ERROR")
                missing_tables.append(table)
        
        cursor.close()
        return missing_tables
        
    except Error as e:
        log(f"检查表格时出错: {str(e)}", "ERROR")
        return required_tables

def check_admin_account(connection):
    """检查管理员账号"""
    log("\n====== 检查管理员账号 ======", "INFO")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 检查admin表中的数据
        cursor.execute("SELECT * FROM admins")
        admins = cursor.fetchall()
        
        if admins:
            log(f"✓ 发现 {len(admins)} 个管理员账号", "SUCCESS")
            for admin in admins:
                log(f"  管理员: {admin['username']}, 角色: {admin.get('role', '未知')}, 状态: {admin.get('status', '未知')}", "INFO")
        else:
            log("✗ 管理员表中没有数据", "ERROR")
            
        # 测试默认管理员账号（不使用实际密码，仅检查表结构）
        cursor.execute("DESCRIBE admins")
        columns = [col[0] for col in cursor.fetchall()]
        log(f"管理员表字段: {columns}", "INFO")
        
        cursor.close()
        return admins
        
    except Error as e:
        log(f"检查管理员账号时出错: {str(e)}", "ERROR")
        return []

def check_student_accounts(connection):
    """检查学生账号"""
    log("\n====== 检查学生账号 ======", "INFO")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 检查student表中的数据
        cursor.execute("SELECT COUNT(*) as count FROM students")
        result = cursor.fetchone()
        count = result['count']
        
        if count > 0:
            log(f"✓ 发现 {count} 个学生账号", "SUCCESS")
            
            # 显示前5个学生账号
            cursor.execute("SELECT * FROM students LIMIT 5")
            students = cursor.fetchall()
            for student in students:
                log(f"  学生: {student.get('card_no', 'N/A')}, 姓名: {student.get('name', 'N/A')}", "INFO")
        else:
            log("✗ 学生表中没有数据", "ERROR")
        
        cursor.close()
        return count > 0
        
    except Error as e:
        log(f"检查学生账号时出错: {str(e)}", "ERROR")
        return False

def create_test_admin(connection):
    """创建测试管理员账号"""
    log("\n====== 创建测试管理员账号 ======", "INFO")
    
    test_admin_username = "test_admin"
    test_admin_password = "admin123"
    password_hash = hashlib.md5(test_admin_password.encode()).hexdigest()
    
    try:
        cursor = connection.cursor()
        
        # 检查是否已存在
        cursor.execute("SELECT * FROM admins WHERE username = %s", (test_admin_username,))
        if cursor.fetchone():
            log(f"✓ 测试管理员账号 '{test_admin_username}' 已存在", "WARNING")
        else:
            # 创建测试管理员
            query = "INSERT INTO admins (username, password, role, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (test_admin_username, password_hash, 'admin', 'active'))
            connection.commit()
            log(f"✓ 成功创建测试管理员账号 '{test_admin_username}'，密码: {test_admin_password}", "SUCCESS")
        
        cursor.close()
        return True
        
    except Error as e:
        log(f"创建测试管理员时出错: {str(e)}", "ERROR")
        return False

def fix_auth_system(connection):
    """修复认证系统"""
    log("\n====== 修复认证系统 ======", "INFO")
    
    fixes_applied = []
    
    # 1. 确保admin表存在
    try:
        cursor = connection.cursor()
        
        # 检查admin表是否存在
        cursor.execute("SHOW TABLES LIKE 'admins'")
        if not cursor.fetchone():
            log("✗ 管理员表不存在，正在创建...", "WARNING")
            # 创建admin表
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
            log("✓ 管理员表已创建", "SUCCESS")
            fixes_applied.append("创建管理员表")
        
        # 2. 创建默认管理员账号
        cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
        if not cursor.fetchone():
            log("✗ 默认管理员账号不存在，正在创建...", "WARNING")
            default_password_hash = hashlib.md5("admin123".encode()).hexdigest()
            query = "INSERT INTO admins (username, password, role, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, ('admin', default_password_hash, 'admin', 'active'))
            connection.commit()
            log("✓ 默认管理员账号 'admin' 已创建，密码: admin123", "SUCCESS")
            fixes_applied.append("创建默认管理员账号")
        else:
            log("✓ 默认管理员账号 'admin' 已存在", "INFO")
        
        cursor.close()
        
    except Error as e:
        log(f"修复认证系统时出错: {str(e)}", "ERROR")
    
    return fixes_applied

def test_login_process(connection):
    """测试登录过程"""
    log("\n====== 测试登录过程 ======", "INFO")
    
    test_username = "admin"
    test_password = "admin123"
    password_hash = hashlib.md5(test_password.encode()).hexdigest()
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 模拟登录验证过程
        query = "SELECT * FROM admins WHERE username = %s AND password = %s"
        cursor.execute(query, (test_username, password_hash))
        admin = cursor.fetchone()
        
        if admin:
            log(f"✓ 登录验证成功！管理员账号 '{test_username}' 可以正常登录", "SUCCESS")
            log(f"  管理员信息: {admin}", "INFO")
            return True
        else:
            # 检查是否是密码错误
            cursor.execute("SELECT * FROM admins WHERE username = %s", (test_username,))
            admin_no_pass = cursor.fetchone()
            
            if admin_no_pass:
                log(f"✗ 用户名存在，但密码错误。数据库中存储的密码哈希: {admin_no_pass['password']}", "ERROR")
                log(f"  测试密码的哈希值: {password_hash}", "INFO")
            else:
                log(f"✗ 管理员账号 '{test_username}' 不存在", "ERROR")
            
            return False
        
    except Error as e:
        log(f"测试登录过程时出错: {str(e)}", "ERROR")
        return False

def generate_fixed_auth_files(working_config):
    """生成修复后的认证相关文件"""
    log("\n====== 生成修复后的认证文件 ======", "INFO")
    
    # 生成修复后的models.py
    models_content = f"""
import mysql.connector
from mysql.connector import Error
import hashlib
import os

# 数据库配置 - 已修复
DB_CONFIG = {
    'host': "{working_config['host']}",
    'user': "{working_config['user']}",
    'password': "{working_config['password']}",
    'database': "{working_config['database']}"
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
    """验证管理员账号"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        # 计算密码的MD5哈希值
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        query = "SELECT * FROM admins WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password_hash))
        admin = cursor.fetchone()
        
        return admin is not None
    except Error as e:
        print(f"验证管理员失败: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def verify_student(card_no, password):
    """验证学生账号"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        # 计算密码的MD5哈希值
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        query = "SELECT * FROM students WHERE card_no = %s AND password = %s"
        cursor.execute(query, (card_no, password_hash))
        student = cursor.fetchone()
        
        return student
    except Error as e:
        print(f"验证学生失败: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_admin_by_username(username):
    """根据用户名获取管理员信息"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM admins WHERE username = %s"
        cursor.execute(query, (username,))
        admin = cursor.fetchone()
        return admin
    except Error as e:
        print(f"获取管理员信息失败: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_student_by_card_no(card_no):
    """根据卡号获取学生信息"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM students WHERE card_no = %s"
        cursor.execute(query, (card_no,))
        student = cursor.fetchone()
        return student
    except Error as e:
        print(f"获取学生信息失败: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
"""
    
    # 生成修复后的auth_controller.py
    controller_content = """
from flask import Blueprint, request, jsonify, session, redirect, url_for
from .models import verify_admin, verify_student, get_admin_by_username, get_student_by_card_no

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口 - 已修复"""
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
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        print(f"[DEBUG] 登录尝试: username={username}, user_type={user_type}")
        
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

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出接口"""
    try:
        # 清除会话
        session.clear()
        return jsonify({'success': True, 'message': '登出成功'})
    except Exception as e:
        print(f"登出失败: {e}")
        return jsonify({'success': False, 'message': '登出失败'}), 500

@auth_bp.route('/check_login', methods=['GET'])
def check_login():
    """检查用户是否已登录"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user_id': session['user_id'],
            'username': session['username'],
            'user_type': session['user_type']
        })
    else:
        return jsonify({'logged_in': False})

def login_required(f):
    """登录装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function
"""
    
    # 保存修复后的文件
    try:
        # 备份原文件
        import shutil
        models_path = 'd:\\Pycharm\\PcData\\student_analytics_system\\auth\\models.py'
        controller_path = 'd:\\Pycharm\\PcData\\student_analytics_system\\auth\\controllers.py'
        
        if os.path.exists(models_path):
            shutil.copy(models_path, models_path + '.bak')
            log(f"已备份原models.py到models.py.bak", "INFO")
        
        if os.path.exists(controller_path):
            shutil.copy(controller_path, controller_path + '.bak')
            log(f"已备份原controllers.py到controllers.py.bak", "INFO")
        
        # 写入修复后的文件
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(models_content)
        log(f"已生成修复后的models.py", "SUCCESS")
        
        with open(controller_path, 'w', encoding='utf-8') as f:
            f.write(controller_content)
        log(f"已生成修复后的controllers.py", "SUCCESS")
        
        return True
    except Exception as e:
        log(f"生成修复文件时出错: {str(e)}", "ERROR")
        return False

def main():
    log("====== 数据库和认证系统检查工具 ======")
    
    # 1. 测试数据库连接
    working_config = test_db_connections()
    
    if not working_config:
        log("无法连接到数据库，系统无法正常工作！", "ERROR")
        return 1
    
    log(f"\n✓ 使用成功的数据库配置: {working_config['host']}, 数据库: {working_config['database']}", "SUCCESS")
    
    # 2. 使用成功的配置连接
    try:
        connection = mysql.connector.connect(**working_config)
        
        # 3. 检查表结构
        missing_tables = check_tables(connection)
        
        # 4. 检查管理员账号
        admins = check_admin_account(connection)
        
        # 5. 检查学生账号
        has_students = check_student_accounts(connection)
        
        # 6. 修复认证系统
        fixes_applied = fix_auth_system(connection)
        
        # 7. 测试登录过程
        login_success = test_login_process(connection)
        
        # 8. 生成修复后的认证文件
        if login_success and working_config:
            generate_fixed_auth_files(working_config)
        
        # 9. 创建测试管理员账号
        create_test_admin(connection)
        
        # 总结报告
        log("\n====== 检查和修复总结 ======", "INFO")
        log(f"数据库连接: {'成功' if working_config else '失败'}", "SUCCESS" if working_config else "ERROR")
        log(f"缺失的表: {', '.join(missing_tables) if missing_tables else '无'}", "WARNING" if missing_tables else "SUCCESS")
        log(f"管理员账号数量: {len(admins)}", "SUCCESS" if len(admins) > 0 else "WARNING")
        log(f"学生账号存在: {'是' if has_students else '否'}", "SUCCESS" if has_students else "WARNING")
        log(f"应用的修复: {', '.join(fixes_applied) if fixes_applied else '无'}", "SUCCESS" if fixes_applied else "INFO")
        log(f"登录测试: {'成功' if login_success else '失败'}", "SUCCESS" if login_success else "ERROR")
        
        log("\n====== 下一步建议 ======", "INFO")
        log("1. 重启Flask服务器以应用更改", "INFO")
        log("2. 使用以下账号登录系统:", "INFO")
        log("   - 管理员账号: admin / admin123", "INFO")
        log("   - 测试账号: test_admin / admin123", "INFO")
        log("3. 如果学生登录，请使用有效的学生卡号和密码", "INFO")
        
        connection.close()
        return 0
        
    except Error as e:
        log(f"操作数据库时出错: {str(e)}", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())