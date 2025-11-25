#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面诊断脚本 - 测试数据库连接和API功能
"""

import os
import sys
import json
import time
import datetime
import traceback
import requests
import pandas as pd
from utils.db_connection import DatabaseConnection

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
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    color = Colors.ENDC
    if level == 'INFO':
        color = Colors.OKBLUE
    elif level == 'SUCCESS':
        color = Colors.OKGREEN
    elif level == 'WARNING':
        color = Colors.WARNING
    elif level == 'ERROR':
        color = Colors.FAIL
    print(f"{color}[{timestamp}] [{level}] {message}{Colors.ENDC}")

# 测试数据库连接
def test_database_connection():
    log("开始测试数据库连接...")
    try:
        # 创建数据库连接
        db_conn = DatabaseConnection()
        if db_conn.connect():
            log("数据库连接成功", "SUCCESS")
            
            # 检查表是否存在
            log("检查数据库表结构...")
            tables = ['students', 'consumption_records', 'access_records', 'admins']
            for table in tables:
                try:
                    # 查询表结构
                    query = f"DESCRIBE {table}"
                    df = db_conn.get_dataframe(query)
                    if not df.empty:
                        log(f"表 {table} 存在，包含字段: {', '.join(df['Field'].tolist())}", "SUCCESS")
                        
                        # 查询记录数
                        count_query = f"SELECT COUNT(*) as count FROM {table}"
                        count_df = db_conn.get_dataframe(count_query)
                        count = count_df['count'].iloc[0]
                        log(f"表 {table} 包含 {count} 条记录", "SUCCESS")
                except Exception as e:
                    log(f"检查表 {table} 时出错: {str(e)}", "ERROR")
            
            # 测试校园卡号查询
            log("测试校园卡号查询...")
            try:
                query = "SELECT DISTINCT card_no FROM consumption_records LIMIT 10"
                card_df = db_conn.get_dataframe(query)
                if not card_df.empty:
                    log(f"成功获取校园卡号样本: {', '.join(map(str, card_df['card_no'].tolist()))}", "SUCCESS")
                else:
                    log("未找到校园卡号数据", "WARNING")
            except Exception as e:
                log(f"查询校园卡号失败: {str(e)}", "ERROR")
                
            db_conn.disconnect()
            return True
        else:
            log("数据库连接失败", "ERROR")
            return False
    except Exception as e:
        log(f"数据库连接异常: {str(e)}", "ERROR")
        traceback.print_exc()
        return False

# 检查数据库配置
def check_database_config():
    log("检查数据库配置...")
    try:
        # 检查db_connection.py文件
        config_path = "utils/db_connection.py"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                log(f"找到数据库配置文件: {config_path}", "INFO")
                # 简单分析配置内容
                if 'host' in content and 'user' in content and 'password' in content and 'database' in content:
                    log("配置文件包含必要的数据库连接参数", "INFO")
                else:
                    log("配置文件可能缺少必要的连接参数", "WARNING")
        else:
            log(f"未找到数据库配置文件: {config_path}", "ERROR")
    except Exception as e:
        log(f"检查数据库配置时出错: {str(e)}", "ERROR")

# 测试API端点
def test_api_endpoints():
    log("开始测试API端点...")
    base_url = "http://localhost:5000"
    endpoints = [
        {"name": "状态检查", "url": "/api/status", "method": "GET"},
        {"name": "获取校园卡号", "url": "/api/card-numbers", "method": "GET"},
        {"name": "今日统计", "url": "/api/today-statistics", "method": "GET"},
        {"name": "消费记录", "url": "/api/consumption-records", "method": "GET"},
        {"name": "门禁记录", "url": "/api/access-records", "method": "GET"}
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            log(f"测试API: {endpoint['name']} ({endpoint['url']})...")
            if endpoint['method'] == "GET":
                response = requests.get(f"{base_url}{endpoint['url']}", timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        log(f"API {endpoint['name']} 返回成功，状态码: {response.status_code}", "SUCCESS")
                        # 显示部分数据
                        if isinstance(data, dict):
                            keys = list(data.keys())[:3]  # 只显示前3个键
                            log(f"返回数据结构: {', '.join(keys)}...", "INFO")
                    except ValueError:
                        log(f"API {endpoint['name']} 返回非JSON数据", "WARNING")
                else:
                    log(f"API {endpoint['name']} 请求失败，状态码: {response.status_code}", "ERROR")
                    log(f"响应内容: {response.text[:200]}...", "ERROR")
                    
                results[endpoint['name']] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
        except requests.exceptions.ConnectionError:
            log(f"无法连接到服务器 {base_url}，请检查服务器是否正在运行", "ERROR")
            results[endpoint['name']] = {
                "status_code": None,
                "success": False,
                "error": "ConnectionError"
            }
        except Exception as e:
            log(f"测试API {endpoint['name']} 时出错: {str(e)}", "ERROR")
            results[endpoint['name']] = {
                "status_code": None,
                "success": False,
                "error": str(e)
            }
    
    return results

# 创建模拟API测试客户端
def create_test_client():
    log("创建Flask测试客户端...")
    try:
        # 导入Flask应用
        from app import app
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # 模拟登录
            log("模拟管理员登录...")
            login_response = client.post('/auth/login', json={
                'username': 'admin',
                'password': 'admin123'  # 默认密码
            })
            
            if login_response.status_code == 200:
                log("模拟登录成功", "SUCCESS")
                
                # 测试需要认证的API
                log("使用测试客户端测试API端点...")
                endpoints = [
                    "/api/status",
                    "/api/card-numbers",
                    "/api/today-statistics",
                    "/api/consumption-records"
                ]
                
                for endpoint in endpoints:
                    response = client.get(endpoint)
                    log(f"测试 {endpoint} - 状态码: {response.status_code}", 
                         "SUCCESS" if response.status_code == 200 else "ERROR")
                    if response.status_code == 200:
                        try:
                            data = response.get_json()
                            log(f"返回数据类型: {type(data).__name__}", "INFO")
                        except:
                            log(f"返回非JSON数据", "WARNING")
            else:
                log(f"模拟登录失败，状态码: {login_response.status_code}", "ERROR")
    except Exception as e:
        log(f"创建测试客户端失败: {str(e)}", "ERROR")
        traceback.print_exc()

# 检查校园卡号API
def check_card_numbers_api():
    log("详细检查校园卡号API...")
    try:
        # 直接从数据库获取校园卡号，绕过API
        db_conn = DatabaseConnection()
        if db_conn.connect():
            # 查询consumption_records表中的card_no
            query = "SELECT DISTINCT card_no FROM consumption_records LIMIT 20"
            df = db_conn.get_dataframe(query)
            
            if not df.empty:
                log(f"从数据库成功获取 {len(df)} 个不同的校园卡号", "SUCCESS")
                log(f"卡号样本: {', '.join(map(str, df['card_no'].tolist()[:5]))}...", "INFO")
                
                # 检查数据类型
                card_types = df['card_no'].apply(type).unique()
                log(f"卡号数据类型: {[t.__name__ for t in card_types]}", "INFO")
                
                # 检查是否有空值
                null_count = df['card_no'].isnull().sum()
                log(f"空卡号数量: {null_count}", "INFO")
            else:
                log("数据库中未找到校园卡号", "WARNING")
            
            db_conn.disconnect()
    except Exception as e:
        log(f"检查校园卡号API失败: {str(e)}", "ERROR")

# 检查消费记录API
def check_consumption_api():
    log("详细检查消费记录API...")
    try:
        # 尝试直接运行API函数
        from app import get_consumption_records
        
        # 创建模拟请求对象
        class MockRequest:
            def __init__(self):
                self.args = {}
        
        # 模拟会话
        from flask import session
        with app.test_request_context():
            session['user_id'] = 'admin'
            session['user_type'] = 'admin'
            
            # 尝试调用API函数
            # 注意：这只是模拟，实际可能需要更多上下文
            log("API函数检查完成", "INFO")
    except Exception as e:
        log(f"直接检查API函数失败: {str(e)}", "WARNING")

# 主函数
def main():
    log("====== 学生消费行为分析系统诊断工具 ======")
    
    # 1. 检查数据库配置
    check_database_config()
    
    # 2. 测试数据库连接
    db_ok = test_database_connection()
    
    # 3. 详细检查校园卡号功能
    if db_ok:
        check_card_numbers_api()
    
    # 4. 测试API端点
    log("\n" + "="*50)
    log("注意：API测试需要服务器正在运行")
    log("如果服务器未运行，请先启动服务器: python app.py")
    log("="*50)
    api_results = test_api_endpoints()
    
    # 5. 尝试创建测试客户端（如果API测试失败）
    if not any(result['success'] for result in api_results.values()):
        log("\n尝试使用Flask测试客户端...")
        create_test_client()
    
    # 6. 生成报告
    log("\n====== 诊断报告 ======")
    log(f"数据库连接: {'成功' if db_ok else '失败'}", 
         "SUCCESS" if db_ok else "ERROR")
    
    log("API状态:")
    for name, result in api_results.items():
        if result['success']:
            log(f"  - {name}: 正常", "SUCCESS")
        else:
            error_msg = result.get('error', f"状态码 {result['status_code']}")
            log(f"  - {name}: 异常 ({error_msg})")
    
    log("\n诊断完成，请查看上面的详细信息")

if __name__ == "__main__":
    main()