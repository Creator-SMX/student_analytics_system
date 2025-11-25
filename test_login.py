#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

def test_admin_login():
    """测试管理员登录功能"""
    print("==== 测试管理员登录 ====")
    
    # 登录URL
    login_url = "http://127.0.0.1:5000/auth/login"
    
    # 测试数据
    test_cases = [
        {"username": "admin", "password": "admin123", "user_type": "admin"},  # 正确的管理员账号
        {"username": "admin", "password": "wrong123", "user_type": "admin"},  # 错误的密码
        {"username": "nonexistent", "password": "admin123", "user_type": "admin"}  # 不存在的用户
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n测试用例 {i+1}:")
        print(f"用户名: {test_case['username']}, 密码: {'*'*len(test_case['password'])}, 用户类型: {test_case['user_type']}")
        
        try:
            # 发送POST请求
            response = requests.post(
                login_url,
                json=test_case,
                headers={'Content-Type': 'application/json'}
            )
            
            # 打印响应信息
            print(f"响应状态码: {response.status_code}")
            
            try:
                response_json = response.json()
                print(f"响应内容: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                
                if response_json.get('success'):
                    print("✓ 登录成功")
                else:
                    print(f"✗ 登录失败: {response_json.get('message', '未知错误')}")
            except json.JSONDecodeError:
                print(f"响应内容不是有效的JSON: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("✗ 连接失败，请确保服务器正在运行")
        except Exception as e:
            print(f"✗ 请求发生错误: {str(e)}")

def test_direct_verification():
    """直接测试验证函数（不通过API）"""
    print("\n==== 直接测试验证函数 ====")
    
    try:
        # 导入验证函数
        from auth.models import verify_admin
        
        # 测试验证函数
        print("测试 verify_admin 函数:")
        print(f"使用正确密码: {verify_admin('admin', 'admin123')}")
        print(f"使用错误密码: {verify_admin('admin', 'wrong123')}")
        print(f"使用不存在用户: {verify_admin('nonexistent', 'admin123')}")
        
    except ImportError as e:
        print(f"✗ 导入验证函数失败: {str(e)}")
    except Exception as e:
        print(f"✗ 验证函数测试出错: {str(e)}")

if __name__ == "__main__":
    # 测试直接验证
    test_direct_verification()
    
    # 测试API登录
    test_admin_login()
    
    print("\n==== 测试完成 ====")