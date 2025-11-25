#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
带认证的API测试脚本
"""

import os
import sys
import json
import time
import datetime
import traceback
import requests
import pandas as pd

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

# API测试类
class APITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.is_logged_in = False
    
    def login(self, username="admin", password="admin123"):
        """尝试登录系统"""
        log(f"尝试以 {username} 登录系统...")
        try:
            login_url = f"{self.base_url}/auth/login"
            
            # 尝试多种登录请求格式
            formats = [
                # 1. JSON格式
                {'json': {'username': username, 'password': password}},
                # 2. 表单格式
                {'data': {'username': username, 'password': password}},
                # 3. 查询参数
                {'params': {'username': username, 'password': password}}
            ]
            
            for i, format_data in enumerate(formats):
                log(f"尝试登录格式 {i+1}...")
                try:
                    response = self.session.post(login_url, **format_data, timeout=10)
                    log(f"登录请求响应: 状态码={response.status_code}, 内容长度={len(response.text)}")
                    
                    # 检查是否登录成功（通常是重定向或返回特定JSON）
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if data.get('status') == 'success' or data.get('message') == '登录成功':
                                log("登录成功！", "SUCCESS")
                                self.is_logged_in = True
                                return True
                        except:
                            # 非JSON响应，检查是否包含登录成功的标记
                            if "登录成功" in response.text or "dashboard" in response.url:
                                log("登录成功（基于响应内容）！", "SUCCESS")
                                self.is_logged_in = True
                                return True
                    elif response.status_code == 302:
                        # 重定向通常表示登录成功
                        log(f"登录成功（重定向到 {response.headers.get('Location')}）！", "SUCCESS")
                        self.is_logged_in = True
                        return True
                except Exception as e:
                    log(f"登录格式 {i+1} 失败: {str(e)}", "WARNING")
            
            log("所有登录尝试都失败了", "ERROR")
            return False
        except Exception as e:
            log(f"登录过程中发生异常: {str(e)}", "ERROR")
            traceback.print_exc()
            return False
    
    def test_api_with_auth(self, endpoint, method="GET", params=None, data=None, json=None):
        """测试需要认证的API端点"""
        if not self.is_logged_in:
            log(f"测试 {endpoint} 前需要先登录", "WARNING")
            if not self.login():
                return None
        
        url = f"{self.base_url}{endpoint}"
        log(f"测试API: {endpoint} ({url})")
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=10)
            elif method == "POST":
                response = self.session.post(url, data=data, json=json, params=params, timeout=10)
            else:
                log(f"不支持的HTTP方法: {method}", "ERROR")
                return None
            
            log(f"API响应: 状态码={response.status_code}")
            
            # 尝试解析JSON响应
            try:
                response_data = response.json()
                log(f"成功解析JSON响应，包含 {len(response_data)} 个键", "SUCCESS")
                
                # 显示部分数据
                if 'data' in response_data:
                    if isinstance(response_data['data'], list):
                        log(f"数据数组长度: {len(response_data['data'])}", "INFO")
                        if response_data['data']:
                            log(f"第一条数据示例: {json.dumps(response_data['data'][0], ensure_ascii=False)[:200]}...", "INFO")
                    else:
                        log(f"数据字段类型: {type(response_data['data']).__name__}", "INFO")
                
                return {
                    "status_code": response.status_code,
                    "data": response_data,
                    "success": response.status_code == 200
                }
            except ValueError:
                log(f"返回非JSON数据，响应内容: {response.text[:200]}...", "WARNING")
                return {
                    "status_code": response.status_code,
                    "text": response.text,
                    "success": False
                }
        except Exception as e:
            log(f"测试API {endpoint} 时出错: {str(e)}", "ERROR")
            traceback.print_exc()
            return {
                "status_code": None,
                "error": str(e),
                "success": False
            }
    
    def test_all_apis(self):
        """测试所有关键API端点"""
        apis = [
            {"name": "状态检查", "endpoint": "/api/status", "method": "GET"},
            {"name": "获取校园卡号", "endpoint": "/api/card-numbers", "method": "GET"},
            {"name": "今日统计", "endpoint": "/api/today-statistics", "method": "GET"},
            {"name": "消费记录", "endpoint": "/api/consumption-records", "method": "GET", "params": {"page": 1, "per_page": 5}},
            {"name": "门禁记录", "endpoint": "/api/access-records", "method": "GET", "params": {"page": 1, "per_page": 5}}
        ]
        
        results = {}
        for api in apis:
            result = self.test_api_with_auth(
                api["endpoint"], 
                method=api["method"],
                params=api.get("params")
            )
            results[api["name"]] = result
        
        return results

# 手动测试校园卡号API
def manual_card_number_test():
    """手动测试校园卡号功能"""
    log("执行手动校园卡号测试...")
    try:
        # 直接测试card-numbers API，捕获完整错误
        tester = APITester()
        
        # 先测试状态API
        status_result = tester.test_api_with_auth("/api/status")
        log(f"状态API测试结果: {'成功' if status_result and status_result['success'] else '失败'}")
        
        # 尝试直接访问card-numbers API
        log("尝试直接访问校园卡号API（不通过封装方法）...")
        try:
            # 先登录
            if tester.login():
                # 检查session中的cookies
                log(f"当前session cookies: {tester.session.cookies.get_dict()}")
                
                # 直接发送请求
                response = tester.session.get(f"{tester.base_url}/api/card-numbers", timeout=10)
                log(f"直接请求响应: 状态码={response.status_code}")
                
                # 打印完整响应内容
                log(f"完整响应内容: {response.text}")
                
                # 尝试解析
                try:
                    data = response.json()
                    log(f"解析后的JSON数据: {data}")
                except:
                    log("无法解析为JSON")
        except Exception as e:
            log(f"直接测试失败: {str(e)}", "ERROR")
            traceback.print_exc()
    except Exception as e:
        log(f"手动测试失败: {str(e)}", "ERROR")

# 创建测试HTML页面
def create_test_html():
    """创建一个简单的测试HTML页面来模拟前端调用"""
    html_content = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API测试页面</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .container { margin-bottom: 20px; }
        button { padding: 8px 16px; margin: 5px; cursor: pointer; }
        .response { border: 1px solid #ccc; padding: 10px; margin-top: 10px; max-height: 400px; overflow-y: auto; background: #f5f5f5; }
        .status { padding: 5px; border-radius: 3px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>学生消费行为分析系统 API 测试</h1>
    
    <div class="container">
        <h2>1. 登录</h2>
        <input type="text" id="username" placeholder="用户名" value="admin">
        <input type="password" id="password" placeholder="密码" value="admin123">
        <button id="loginBtn">登录</button>
        <div id="loginStatus" class="status"></div>
    </div>
    
    <div class="container">
        <h2>2. API 测试</h2>
        <button id="statusBtn">测试状态API</button>
        <button id="cardNumbersBtn">测试校园卡号API</button>
        <button id="statisticsBtn">测试今日统计API</button>
        <button id="consumptionBtn">测试消费记录API</button>
        <button id="accessBtn">测试门禁记录API</button>
        <div id="responseArea" class="response"></div>
    </div>
    
    <script>
        // 存储登录状态
        let isLoggedIn = false;
        
        // 显示响应
        function showResponse(title, data, success = true) {
            const responseArea = document.getElementById('responseArea');
            const statusClass = success ? 'success' : 'error';
            
            responseArea.innerHTML = `
                <h3>${title}</h3>
                <div class="status ${statusClass}">状态: ${success ? '成功' : '失败'}</div>
                <pre>${typeof data === 'string' ? data : JSON.stringify(data, null, 2)}</pre>
            `;
        }
        
        // 登录函数
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const loginStatus = document.getElementById('loginStatus');
            
            try {
                // 尝试多种登录格式
                let response;
                
                // 尝试JSON格式
                try {
                    response = await axios.post('/auth/login', { username, password });
                } catch (e) {
                    // 尝试表单格式
                    response = await axios.post('/auth/login', new URLSearchParams({ username, password }));
                }
                
                isLoggedIn = true;
                loginStatus.className = 'status success';
                loginStatus.textContent = '登录成功！';
                showResponse('登录响应', response.data, true);
                
            } catch (error) {
                isLoggedIn = false;
                loginStatus.className = 'status error';
                loginStatus.textContent = '登录失败！';
                showResponse('登录错误', error.response ? error.response.data : error.message, false);
            }
        }
        
        // 测试API函数
        async function testAPI(endpoint, title) {
            if (!isLoggedIn) {
                showResponse(title, { error: '请先登录' }, false);
                return;
            }
            
            try {
                const response = await axios.get(endpoint);
                showResponse(title, response.data, true);
            } catch (error) {
                showResponse(title, error.response ? error.response.data : error.message, false);
            }
        }
        
        // 绑定事件监听器
        document.getElementById('loginBtn').addEventListener('click', login);
        document.getElementById('statusBtn').addEventListener('click', () => testAPI('/api/status', '状态API测试'));
        document.getElementById('cardNumbersBtn').addEventListener('click', () => testAPI('/api/card-numbers', '校园卡号API测试'));
        document.getElementById('statisticsBtn').addEventListener('click', () => testAPI('/api/today-statistics', '今日统计API测试'));
        document.getElementById('consumptionBtn').addEventListener('click', () => testAPI('/api/consumption-records?page=1&per_page=5', '消费记录API测试'));
        document.getElementById('accessBtn').addEventListener('click', () => testAPI('/api/access-records?page=1&per_page=5', '门禁记录API测试'));
        
        // 页面加载时自动测试状态API
        window.addEventListener('load', () => {
            testAPI('/api/status', '状态API测试');
        });
    </script>
</body>
</html>
'''
    
    with open('api_test.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    log("已创建测试HTML页面: api_test.html", "SUCCESS")

# 主函数
def main():
    log("====== 带认证的API测试工具 ======")
    
    # 1. 创建测试HTML页面
    create_test_html()
    
    # 2. 执行API测试
    tester = APITester()
    results = tester.test_all_apis()
    
    # 3. 执行手动校园卡号测试
    manual_card_number_test()
    
    # 4. 生成报告
    log("\n====== API测试报告 ======")
    for name, result in results.items():
        if result and result.get('success'):
            log(f"✓ {name}: 成功", "SUCCESS")
        else:
            error_msg = "未知错误"
            if result:
                if result.get('status_code'):
                    error_msg = f"状态码 {result['status_code']}"
                elif result.get('error'):
                    error_msg = result['error']
            log(f"✗ {name}: 失败 ({error_msg})", "ERROR")
    
    log("\n请在浏览器中打开 api_test.html 进行交互式测试")
    log("也可以使用以下命令启动服务器并手动测试:")
    log("  python app.py")

if __name__ == "__main__":
    main()