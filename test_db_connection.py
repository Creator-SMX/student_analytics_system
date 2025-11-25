#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""数据库连接稳定性测试脚本"""
import pymysql
import traceback
import threading
import time
import random
import json
from flask import Flask

# 创建一个简单的Flask应用实例用于测试
app = Flask(__name__)

# 导入现有的控制器进行测试
try:
    from analytics.analytics_controller import get_db_engine, DBConnection
    db_conn = DBConnection()
    print("✅ 成功导入analytics_controller")
except Exception as e:
    print(f"❌ 导入analytics_controller失败: {str(e)}")

def test_direct_connection():
    """直接使用pymysql测试数据库连接"""
    print("=== 直接数据库连接测试开始 ===")
    
    try:
        # 使用pymysql直接连接
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ 数据库连接成功!")
        
        # 测试一个简单查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() as version")
            result = cursor.fetchone()
            print(f"数据库版本: {result['version']}")
            
            # 测试访问students表
            cursor.execute("SELECT COUNT(*) as count FROM students")
            count = cursor.fetchone()['count']
            print(f"students表记录数: {count}")
            
            # 测试访问consumption_records表
            cursor.execute("SELECT COUNT(*) as count FROM consumption_records")
            count = cursor.fetchone()['count']
            print(f"consumption_records表记录数: {count}")
        
        connection.close()
        print("✅ 数据库连接已关闭")
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        traceback.print_exc()
        return False

def test_db_connection_class():
    """测试DBConnection类的连接功能"""
    print("\n=== DBConnection类测试开始 ===")
    
    if 'db_conn' not in globals():
        print("❌ DBConnection实例未创建")
        return False
    
    try:
        # 测试连接
        conn = db_conn.connect()
        if conn:
            print("✅ DBConnection连接成功")
            
            # 执行简单查询
            from sqlalchemy import text
            result = conn.execute(text("SELECT VERSION() as version")).fetchone()
            print(f"数据库版本: {result['version']}")
            
            # 关闭连接
            db_conn.disconnect()
            print("✅ DBConnection连接已关闭")
            return True
        else:
            print("❌ DBConnection连接失败")
            return False
    except Exception as e:
        print(f"❌ DBConnection测试失败: {str(e)}")
        traceback.print_exc()
        try:
            db_conn.disconnect()
        except:
            pass
        return False

def test_multiple_connections():
    """测试多次连接和断开"""
    print("\n=== 多次连接断开测试开始 ===")
    
    if 'db_conn' not in globals():
        print("❌ DBConnection实例未创建")
        return False
    
    success_count = 0
    total_tests = 5
    
    for i in range(total_tests):
        try:
            print(f"\n测试 #{i+1}/{total_tests}")
            conn = db_conn.connect()
            if conn:
                from sqlalchemy import text
                result = conn.execute(text("SELECT 1 as test")).fetchone()
                print(f"  ✅ 查询成功: {result['test']}")
                success_count += 1
            else:
                print("  ❌ 连接失败")
        except Exception as e:
            print(f"  ❌ 测试失败: {str(e)}")
        finally:
            try:
                db_conn.disconnect()
                print("  ✅ 连接已关闭")
            except Exception as e:
                print(f"  ❌ 关闭连接失败: {str(e)}")
            
        # 短暂延迟
        time.sleep(0.5)
    
    print(f"\n多次连接测试结果: {success_count}/{total_tests} 成功")
    return success_count == total_tests

def test_concurrent_connections():
    """测试并发连接"""
    print("\n=== 并发连接测试开始 ===")
    
    if 'db_conn' not in globals():
        print("❌ DBConnection实例未创建")
        return False
    
    error_count = 0
    total_threads = 10
    
    def worker(worker_id):
        nonlocal error_count
        try:
            print(f"线程 {worker_id} 开始连接")
            # 每个线程创建自己的连接
            local_conn = DBConnection()
            conn = local_conn.connect()
            if conn:
                from sqlalchemy import text
                # 执行不同的查询以模拟不同操作
                query = f"SELECT {worker_id} as worker_id, COUNT(*) as count FROM consumption_records WHERE id % {total_threads} = {worker_id} LIMIT 1"
                result = conn.execute(text(query)).fetchone()
                print(f"线程 {worker_id} 查询成功")
            else:
                print(f"线程 {worker_id} 连接失败")
                error_count += 1
        except Exception as e:
            print(f"线程 {worker_id} 错误: {str(e)}")
            if "Packet sequence number wrong" in str(e):
                print(f"⚠️  检测到目标错误: {str(e)}")
            error_count += 1
        finally:
            try:
                local_conn.disconnect()
                print(f"线程 {worker_id} 连接已关闭")
            except Exception as e:
                print(f"线程 {worker_id} 关闭连接失败: {str(e)}")
    
    # 创建并启动线程
    threads = []
    for i in range(total_threads):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
    
    for thread in threads:
        thread.start()
        time.sleep(0.1)  # 稍微错开启动时间
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print(f"\n并发连接测试结果: {total_threads - error_count}/{total_threads} 线程成功")
    if error_count > 0:
        print("❌ 并发连接测试失败，检测到连接问题")
    else:
        print("✅ 并发连接测试成功")
    
    return error_count == 0

# 连接池配置建议
def connection_pool_recommendations():
    """提供数据库连接池配置建议"""
    print("\n===== 数据库连接池配置建议 =====")
    print("1. 使用SQLAlchemy的连接池:")
    print("   - 添加pool_size参数设置初始连接数")
    print("   - 添加max_overflow参数设置最大连接数")
    print("   - 添加pool_pre_ping=True检测连接有效性")
    print("   - 添加pool_recycle参数回收长时间连接")
    print("\n2. 示例配置:")
    print("   engine = create_engine(")
    print("       'mysql+pymysql://user:password@host/db?charset=utf8mb4',")
    print("       pool_size=10,")
    print("       max_overflow=20,")
    print("       pool_pre_ping=True,")
    print("       pool_recycle=3600")
    print("   )")

if __name__ == "__main__":
    print("开始数据库连接稳定性测试...")
    
    # 运行各项测试
    test_direct_connection()
    test_db_connection_class()
    test_multiple_connections()
    test_concurrent_connections()
    
    # 输出连接池配置建议
    connection_pool_recommendations()
    
    print("\n测试完成")