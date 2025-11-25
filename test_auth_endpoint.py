#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试认证端点的脚本
用于直接测试/auth/login API，查看详细的请求和响应信息
"""

import requests
import json

# 服务器URL
BASE_URL = "http://localhost:5001"
LOGIN_URL = f"{BASE_URL}/auth/login"

print("===== 测试登录API =====")
print(f"测试URL: {LOGIN_URL}")

# 测试数据
admin_credentials = {
    'username': 'admin',
    'password': '123456'
}

print(f"测试凭据: {admin_credentials}")

# 1. 使用JSON格式发送请求
try:
    print("\n1. 使用JSON格式发送请求:")
    headers = {'Content-Type': 'application/json'}
    response = requests.post(LOGIN_URL, json=admin_credentials, headers=headers)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应头: {response.headers}")
    print(f"响应内容: {response.text}")
    
    # 尝试解析JSON响应
    try:
        result = response.json()
        print(f"JSON解析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except json.JSONDecodeError:
        print("警告: 响应内容不是有效的JSON格式")
        
    # 检查Cookie
    print(f"\n响应Cookie: {response.cookies}")
    
    # 2. 测试表单格式请求（虽然前端使用JSON）
    print("\n\n2. 使用表单格式发送请求:")
    form_response = requests.post(LOGIN_URL, data=admin_credentials)
    
    print(f"表单请求状态码: {form_response.status_code}")
    print(f"表单请求响应: {form_response.text}")
    
    # 3. 测试使用错误密码
    print("\n\n3. 测试使用错误密码:")
    wrong_credentials = {
        'username': 'admin',
        'password': 'wrong_password'
    }
    wrong_response = requests.post(LOGIN_URL, json=wrong_credentials)
    print(f"错误密码状态码: {wrong_response.status_code}")
    print(f"错误密码响应: {wrong_response.text}")
    
    # 4. 测试check_login接口
    print("\n\n4. 测试check_login接口:")
    check_url = f"{BASE_URL}/auth/check_login"
    check_response = requests.get(check_url)
    print(f"check_login状态码: {check_response.status_code}")
    print(f"check_login响应: {check_response.text}")
    
    # 5. 测试主页重定向
    print("\n\n5. 测试主页重定向:")
    home_response = requests.get(BASE_URL, allow_redirects=False)
    print(f"主页状态码: {home_response.status_code}")
    print(f"重定向目标: {home_response.headers.get('Location')}")
    
    # 6. 测试登录页面
    print("\n\n6. 测试登录页面:")
    login_page_response = requests.get(f"{BASE_URL}/login")
    print(f"登录页面状态码: {login_page_response.status_code}")
    print(f"登录页面内容长度: {len(login_page_response.text)} 字节")
    
    print("\n===== 测试完成 =====")
    
    # 总结
    print("\n===== 测试总结 =====")
    print("请检查上述测试结果，重点关注:")
    print("1. JSON请求是否正常工作")
    print("2. 响应中的错误信息")
    print("3. Cookie是否正确设置")
    
    # 检查是否有成功的登录响应
    try:
        if response.status_code == 200 and response.json().get('success'):
            print("✅ 登录API测试成功！")
        else:
            print("❌ 登录API测试失败，请检查服务器端配置")
    except:
        print("❌ 无法确定登录结果，请检查响应格式")
        
except Exception as e:
    print(f"测试过程中发生错误: {str(e)}")
    import traceback
    traceback.print_exc()