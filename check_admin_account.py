#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

def check_admin_account():
    """检查数据库中的管理员账号"""
    try:
        # 数据库连接配置
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics'
        )
        
        if connection.is_connected():
            print("成功连接到数据库")
            
            cursor = connection.cursor(dictionary=True)
            
            # 检查admins表是否存在
            cursor.execute("SHOW TABLES LIKE 'admins'")
            if cursor.fetchone():
                print("admins表存在")
                
                # 查询管理员账号信息
                cursor.execute("SELECT * FROM admins")
                admins = cursor.fetchall()
                
                if admins:
                    print(f"找到 {len(admins)} 个管理员账号")
                    for admin in admins:
                        print(f"\n管理员信息:")
                        print(f"ID: {admin.get('id')}")
                        print(f"用户名: {admin.get('username')}")
                        print(f"密码: {admin.get('password')}")
                        print(f"名称: {admin.get('name')}")
                        print(f"角色: {admin.get('role')}")
                        print(f"状态: {admin.get('status')}")
                else:
                    print("未找到任何管理员账号")
            else:
                print("错误: admins表不存在")
                
                # 尝试创建admins表
                try:
                    create_table_query = """
                    CREATE TABLE IF NOT EXISTS admins (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(100) NOT NULL,
                        name VARCHAR(100),
                        role VARCHAR(20) DEFAULT 'admin',
                        status INT DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                    cursor.execute(create_table_query)
                    print("已创建admins表")
                    
                    # 创建默认管理员账号
                    admin_username = 'admin'
                    admin_password = 'admin123'
                    admin_name = '系统管理员'
                    
                    insert_query = """
                    INSERT INTO admins (username, password, name, role, status)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (admin_username, admin_password, admin_name, 'admin', 1))
                    connection.commit()
                    print(f"已创建默认管理员账号: {admin_username} / {admin_password}")
                    
                except Exception as e:
                    print(f"创建表或管理员账号失败: {str(e)}")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"数据库操作失败: {e}")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    print("==== 检查管理员账号 ====")
    check_admin_account()