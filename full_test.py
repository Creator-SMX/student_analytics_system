import requests
import json

def test_admin_login():
    """测试管理员登录功能"""
    login_url = "http://localhost:5000/auth/login"
    
    # 尝试管理员登录
    try:
        print("尝试管理员登录...")
        data = {
            'username': 'admin',
            'password': '123456',
            'user_type': 'admin'
        }
        # 使用json参数而不是data，确保Content-Type设置为application/json
        response = requests.post(login_url, json=data)
        print(f"登录响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("登录成功！")
            return response.cookies
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"登录请求错误: {str(e)}")
        return None

def test_consumption_api(cookies):
    """测试消费记录API"""
    if not cookies:
        print("无有效登录信息，跳过API测试")
        return
    
    # 修正API URL，正确的消费记录API端点是/admin/consumption/list
    api_url = "http://localhost:5000/admin/consumption/list"
    
    try:
        # 准备请求参数
        params = {
            'page': 1,
            'page_size': 10
        }
        
        print("\n测试消费记录API...")
        print(f"请求URL: {api_url}")
        print(f"请求参数: {params}")
        
        # 发送请求，携带登录Cookie
        response = requests.get(api_url, params=params, cookies=cookies)
        print(f"API响应状态码: {response.status_code}")
        
        # 打印响应内容
        try:
            result = response.json()
            print("\nAPI响应内容:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 特别关注data和total字段
            if 'data' in result:
                print(f"\n返回记录数: {len(result['data'])}")
            if 'total' in result:
                print(f"总记录数: {result['total']}")
                
        except json.JSONDecodeError:
            print("无法解析JSON响应")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"API请求错误: {str(e)}")

def main():
    print("===== 完整功能测试 =====")
    
    # 测试登录
    cookies = test_admin_login()
    
    # 测试API
    test_consumption_api(cookies)

if __name__ == "__main__":
    main()