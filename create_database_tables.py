#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""创建数据库和表结构脚本"""
import pymysql
import traceback

print("=== 开始创建数据库和表结构 ===")

try:
    # 先连接到MySQL服务器（不指定数据库）
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    
    with conn.cursor() as cursor:
        # 创建数据库（如果不存在）
        print("正在创建数据库 student_analytics...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS student_analytics DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ 数据库创建成功")
        
        # 选择数据库
        cursor.execute("USE student_analytics")
        
        # 先删除现有表（如果存在）以避免冲突
        print("\n正在清理现有表结构...")
        cursor.execute("DROP TABLE IF EXISTS access_records")
        cursor.execute("DROP TABLE IF EXISTS consumption_records")
        cursor.execute("DROP TABLE IF EXISTS admins")
        cursor.execute("DROP TABLE IF EXISTS students")
        print("✅ 表结构清理完成")
        
        # 创建 admins 表（先创建，不依赖其他表）
        print("\n正在创建 admins 表...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(32) NOT NULL,
            name VARCHAR(50) NOT NULL,
            role VARCHAR(20) DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("✅ admins 表创建成功")
        
        # 创建 students 表
        print("\n正在创建 students 表...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT PRIMARY KEY AUTO_INCREMENT,
            student_id VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(50) NOT NULL,
            gender VARCHAR(10),
            major VARCHAR(100),
            grade VARCHAR(20),
            password VARCHAR(32) NOT NULL,
            balance DECIMAL(10, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("✅ students 表创建成功")
        
        # 创建 consumption_records 表（移除外键约束以避免插入冲突）
        print("\n正在创建 consumption_records 表...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumption_records (
            id INT PRIMARY KEY AUTO_INCREMENT,
            student_id VARCHAR(20) NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            category VARCHAR(50),
            consumption_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            location VARCHAR(100)
        )
        """)
        print("✅ consumption_records 表创建成功")
        
        # 创建 access_records 表
        print("\n正在创建 access_records 表...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_records (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id VARCHAR(20) NOT NULL,
            user_type VARCHAR(10) NOT NULL,  -- 'student' 或 'admin'
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            login_ip VARCHAR(50),
            logout_time TIMESTAMP NULL
        )
        """)
        print("✅ access_records 表创建成功")
        
        # 插入默认管理员账户（密码: 123456）
        print("\n正在插入默认管理员账户...")
        cursor.execute("""
        INSERT INTO admins (username, password, name) VALUES 
        ('admin', 'e10adc3949ba59abbe56e057f20f883e', '系统管理员')
        """)
        print("✅ 默认管理员账户创建成功 (用户名: admin, 密码: 123456)")
        
        # 插入一些测试学生数据
        print("\n正在插入测试学生数据...")
        cursor.execute("""
        INSERT INTO students (student_id, name, gender, major, grade, password, balance) VALUES
        ('2021001', '张三', '男', '计算机科学', '2021', 'e10adc3949ba59abbe56e057f20f883e', 500.00),
        ('2021002', '李四', '女', '软件工程', '2021', 'e10adc3949ba59abbe56e057f20f883e', 300.00),
        ('2021003', '王五', '男', '数据科学', '2021', 'e10adc3949ba59abbe56e057f20f883e', 450.00)
        """)
        print("✅ 测试学生数据插入成功 (密码: 123456)")
        
        # 插入一些消费记录
        print("\n正在插入测试消费记录...")
        cursor.execute("""
        INSERT INTO consumption_records (student_id, amount, category, location) VALUES
        ('2021001', 15.50, '午餐', '第一食堂'),
        ('2021001', 8.00, '早餐', '第二食堂'),
        ('2021002', 12.00, '午餐', '第一食堂'),
        ('2021003', 10.50, '晚餐', '第二食堂'),
        ('2021003', 6.00, '早餐', '第一食堂')
        """)
        print("✅ 测试消费记录插入成功")
    
    conn.commit()
    conn.close()
    print("\n✅ 所有数据库操作完成！数据库 student_analytics 已创建并初始化成功。")
    print("\n=== 数据库初始化完成 ===")
    
except Exception as e:
    print(f"\n❌ 错误: {str(e)}")
    traceback.print_exc()
    print("\n=== 数据库初始化失败 ===")