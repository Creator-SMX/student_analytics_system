import mysql.connector
from mysql.connector import Error

# 数据库连接信息
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # MySQL默认用户
    'password': '123456',  # 设置默认密码
    'charset': 'utf8mb4'
}

# 创建数据库和表的SQL语句
SQL_STATEMENTS = [
    # 创建数据库
    "CREATE DATABASE IF NOT EXISTS student_analytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
    
    # 使用数据库
    "USE student_analytics;",
    
    # 创建学生表
    """CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        card_no VARCHAR(20) NOT NULL UNIQUE,
        sex VARCHAR(10) NOT NULL,
        major VARCHAR(100) NOT NULL,
        access_card_no VARCHAR(20) NOT NULL UNIQUE,
        password VARCHAR(255) DEFAULT '123456',  # 默认密码
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",
    
    # 创建消费记录表
    """CREATE TABLE IF NOT EXISTS consumption_records (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        card_no VARCHAR(20) NOT NULL,
        peo_no VARCHAR(20),
        date_time DATETIME,
        money DECIMAL(10, 2),
        term_no VARCHAR(20),
        term_ser_no VARCHAR(20),
        con_oper_no VARCHAR(20),
        oper_no VARCHAR(20),
        dept VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_card_no (card_no),
        INDEX idx_date_time (date_time),
        INDEX idx_dept (dept)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",
    
    # 创建门禁记录表
    """CREATE TABLE IF NOT EXISTS access_records (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        access_card_no VARCHAR(20) NOT NULL,
        date_time DATETIME,
        address VARCHAR(200),
        access INT,
        describe_text VARCHAR(200),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_access_card_no (access_card_no),
        INDEX idx_date_time (date_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",
    
    # 创建管理员表
    """CREATE TABLE IF NOT EXISTS admins (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(100) NOT NULL,
        role VARCHAR(50) DEFAULT 'admin',
        status TINYINT DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",
    
    # 插入默认管理员
    "INSERT INTO admins (username, password, name, role) VALUES ('admin', 'e10adc3949ba59abbe56e057f20f883e', '系统管理员', 'superadmin') ON DUPLICATE KEY UPDATE username=username;"
]

def create_database_and_tables():
    """创建数据库和表结构"""
    try:
        # 连接到MySQL服务器
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("开始创建数据库和表...")
            
            # 执行SQL语句
            for sql in SQL_STATEMENTS:
                cursor.execute(sql)
                print(f"执行: {sql[:50]}...")
            
            connection.commit()
            print("\n✅ 数据库和表创建成功!")
            print("\n📋 创建的表:")
            print("1. students - 学生信息表")
            print("2. consumption_records - 消费记录表")
            print("3. access_records - 门禁记录表")
            print("4. admins - 管理员表")
            print("\n🔑 默认管理员账号:")
            print("   用户名: admin")
            print("   密码: 123456")
            
    except Error as e:
        print(f"❌ 数据库操作失败: {e}")
        print("\n请检查以下事项:")
        print("1. MySQL服务是否正在运行")
        print("2. 数据库连接信息是否正确")
        print("3. 用户是否有创建数据库和表的权限")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n数据库连接已关闭")

if __name__ == "__main__":
    print("====================================")
    print("学生消费行为分析系统 - 数据库初始化")
    print("====================================")
    
    # 显示当前配置
    print(f"当前配置:")
    print(f"  主机: {DB_CONFIG['host']}")
    print(f"  用户: {DB_CONFIG['user']}")
    print(f"  密码: {'*' * len(DB_CONFIG['password'])}")
    
    # 直接执行数据库创建
    print("\n开始执行数据库创建...")
    create_database_and_tables()