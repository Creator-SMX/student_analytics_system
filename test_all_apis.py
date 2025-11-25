import requests
import json

# 基础配置
BASE_URL = 'http://localhost:5000'
API_ENDPOINTS = [
    '/analytics/analytics/api/get_overview',
    '/analytics/analytics/api/get_time_analysis',
    '/analytics/analytics/api/get_cluster',
    '/analytics/analytics/api/get_access_pattern',
    '/analytics/analytics/api/get_consumption_query'
]

# 登录获取token
def login():
    login_url = f"{BASE_URL}/auth/login"
    credentials = {'username': 'admin', 'password': '123456'}
    try:
        response = requests.post(login_url, data=credentials)
        if response.status_code == 200:
            return response.cookies  # 返回cookies，包含session信息
        else:
            print(f"登录失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"登录时发生错误: {e}")
        return None

# 测试所有API端点
def test_all_apis():
    print("===== 开始测试所有API端点 =====")
    
    # 登录
    cookies = login()
    if not cookies:
        print("无法登录，测试终止")
        return
    print("登录成功")
    
    # 测试每个端点
    success_count = 0
    for endpoint in API_ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n测试端点: {endpoint}")
        print(f"完整URL: {url}")
        
        try:
            response = requests.get(url, cookies=cookies)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                success_count += 1
                try:
                    data = response.json()
                    print(f"响应数据类型: {type(data)}")
                    if isinstance(data, dict):
                        print(f"响应数据键: {list(data.keys())}")
                        if data:
                            first_key = list(data.keys())[0]
                            print(f"第一个键的值示例: {data[first_key]}")
                    elif isinstance(data, list):
                        print(f"响应数据长度: {len(data)}")
                        if data:
                            print(f"第一个元素示例: {data[0]}")
                except json.JSONDecodeError:
                    print("响应不是有效的JSON格式")
                    print(f"响应内容预览: {response.text[:100]}...")
            else:
                print(f"请求失败，响应内容: {response.text}")
                
        except Exception as e:
            print(f"请求时发生错误: {e}")
    
    # 测试总结
    print("\n===== 测试总结 =====")
    print(f"总共测试端点数量: {len(API_ENDPOINTS)}")
    print(f"成功端点数量: {success_count}")
    print(f"失败端点数量: {len(API_ENDPOINTS) - success_count}")
    print(f"成功率: {success_count / len(API_ENDPOINTS) * 100:.1f}%")

if __name__ == "__main__":
    test_all_apis()