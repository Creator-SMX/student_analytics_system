from app import app
import json

def test_admin_login():
    """使用Flask测试客户端测试管理员登录"""
    # 获取测试客户端
    client = app.test_client()
    
    print("开始测试管理员登录...")
    
    # 准备登录数据
    login_data = {
        'username': 'admin',
        'password': '123456',
        'user_type': 'admin'
    }
    
    # 发送登录请求
    response = client.post('/auth/login', json=login_data)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.data.decode('utf-8')}")
    
    # 尝试解析JSON响应
    try:
        result = response.get_json()
        print(f"JSON响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"解析JSON失败: {str(e)}")

if __name__ == "__main__":
    test_admin_login()