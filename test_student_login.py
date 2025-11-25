import requests
import json
import hashlib
import pymysql

def get_db_connection():
    """获取数据库连接"""
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

def check_student_in_db(card_no):
    """检查学生是否在数据库中存在"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            # 查询学生表结构
            cursor.execute("DESCRIBE students")
            table_structure = cursor.fetchall()
            print("\n=== 学生表结构 ===")
            for field in table_structure:
                print(f"{field['Field']}: {field['Type']}")
            
            # 查询特定学生
            query = "SELECT * FROM students WHERE card_no = %s"
            cursor.execute(query, (card_no,))
            student = cursor.fetchone()
            
            # 查询学生表中的几条记录
            cursor.execute("SELECT * FROM students LIMIT 5")
            students_sample = cursor.fetchall()
            print("\n=== 学生表前5条记录 ===")
            for idx, s in enumerate(students_sample):
                print(f"记录 {idx+1}: {s['card_no'] if 'card_no' in s else 'N/A'}")
            
            return student
    except Exception as e:
        print(f"查询数据库时出错: {e}")
        return None
    finally:
        if connection:
            connection.close()

def test_student_login():
    """测试学生登录功能"""
    login_url = "http://localhost:5000/auth/login"
    
    # 测试学生账号
    card_no = "180001"  # 假设的学生卡号
    password_plain = "123456"  # 明文密码
    password_suffix = card_no[-6:]  # 卡号后6位
    password_md5 = hashlib.md5(password_suffix.encode()).hexdigest()  # 卡号后6位的MD5值
    
    print(f"=== 测试学生登录 ===")
    print(f"测试卡号: {card_no}")
    print(f"明文密码: {password_plain}")
    print(f"卡号后6位: {password_suffix}")
    print(f"卡号后6位的MD5: {password_md5}")
    print()
    
    # 测试1: 使用明文密码'123456'
    print("[测试1] 使用明文密码'123456'登录:")
    test_login(login_url, card_no, password_plain)
    print()
    
    # 测试2: 使用卡号后6位明文
    print("[测试2] 使用卡号后6位明文登录:")
    test_login(login_url, card_no, password_suffix)
    print()
    
    # 测试3: 使用卡号后6位的MD5值登录
    print("[测试3] 使用卡号后6位的MD5值登录:")
    test_login(login_url, card_no, password_md5)
    
    # 检查数据库中的学生信息
    print("=== 检查数据库中的学生信息 ===")
    student = check_student_in_db(card_no)
    if student:
        print(f"找到学生: {student}")
        # 特别打印密码字段信息
        if 'password' in student:
            print(f"学生密码: {student['password']}")
            # 计算可能的密码哈希用于比较
            print(f"卡号后6位MD5与数据库密码匹配: {student['password'] == password_md5}")
            print(f"默认密码'123456'与数据库密码匹配: {student['password'] == password_plain}")
            print(f"默认密码'123456'的MD5与数据库密码匹配: {student['password'] == hashlib.md5(password_plain.encode()).hexdigest()}")
    else:
        print(f"数据库中未找到卡号为 {card_no} 的学生")
    
    print("\n=== 尝试使用数据库中存在的卡号登录 ===")
    # 尝试使用管理员登录（作为对比）
    print("\n[对比测试] 尝试管理员登录:")
    test_admin_login(login_url)

def test_login(url, username, password, user_type='student'):
    """执行登录测试"""
    data = {
        'username': username,
        'password': password,
        'user_type': user_type
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json=data)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 尝试解析JSON响应
        try:
            result = response.json()
            print(f"JSON解析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError:
            print("响应不是有效的JSON格式")
            
    except Exception as e:
        print(f"请求失败: {str(e)}")

def test_admin_login(url):
    """测试管理员登录"""
    data = {
        'username': 'admin',
        'password': '123456',
        'user_type': 'admin'
    }
    test_login(url, data['username'], data['password'], data['user_type'])

if __name__ == "__main__":
    test_student_login()