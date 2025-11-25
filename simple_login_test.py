import requests
import json

def test_login():
    """简单的登录测试"""
    login_url = "http://localhost:5000/auth/login"
    
    # 准备登录数据
    data = {
        'username': 'admin',
        'password': '123456',
        'user_type': 'admin'
    }
    
    print(f"测试管理员登录: {data}")
    
    try:
        # 发送POST请求
        response = requests.post(login_url, json=data)
        
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

if __name__ == "__main__":
    test_login()