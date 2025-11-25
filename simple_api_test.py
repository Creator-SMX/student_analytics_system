import requests
import json

session = requests.Session()

# 定义基础URL
base_url = 'http://localhost:5000'

# 定义所有要测试的API端点
api_endpoints = [
    '/analytics/analytics/api/get_overview',  # 核心数据概览
    '/analytics/analytics/api/get_time_analysis',  # 消费时段分析
    '/analytics/analytics/api/get_cluster',  # 消费行为聚类
    '/analytics/analytics/api/get_access_pattern',  # 门禁行为模式
    '/analytics/analytics/api/get_canteen_analysis'  # 食堂消费分析
]

def test_api_endpoint(endpoint):
    """测试单个API端点"""
    url = f'{base_url}{endpoint}'
    print(f'\n测试端点: {endpoint}')
    print(f'完整URL: {url}')
    
    try:
        response = session.get(url)
        print(f'状态码: {response.status_code}')
        
        if response.status_code == 200:
            # 尝试解析JSON响应
            try:
                data = response.json()
                print(f'响应数据类型: {type(data)}')
                print(f'响应数据结构: {list(data.keys())[:5]}...')
                if isinstance(data, dict) and data:
                    # 显示第一个数据项的示例
                    first_key = list(data.keys())[0]
                    print(f'第一个字段示例 ({first_key}): {data[first_key]}')
                elif isinstance(data, list) and data:
                    print(f'数据项数量: {len(data)}')
                    print(f'第一项示例: {data[0]}')
                return True
            except json.JSONDecodeError:
                print(f'响应不是有效的JSON: {response.text[:200]}...')
                return False
        else:
            print(f'响应内容: {response.text[:200]}...')
            return False
    except Exception as e:
        print(f'请求错误: {str(e)}')
        return False

try:
    # 1. 先进行登录
    print('=== 开始测试 ===')
    print('\n1. 登录认证测试')
    login_data = {
        'username': 'admin',
        'password': '123456',
        'user_type': 'admin'
    }
    login_response = session.post(f'{base_url}/auth/login', json=login_data)
    print(f'登录状态码: {login_response.status_code}')
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f'登录成功: {login_result.get("message", "")}')
        print(f'用户类型: {login_result.get("user_type", "")}')
        
        # 2. 测试所有API端点
        print('\n2. API端点测试')
        success_count = 0
        total_count = len(api_endpoints)
        
        for endpoint in api_endpoints:
            if test_api_endpoint(endpoint):
                success_count += 1
        
        # 3. 输出测试汇总
        print('\n3. 测试汇总')
        print(f'总端点数: {total_count}')
        print(f'成功数: {success_count}')
        print(f'成功率: {(success_count/total_count*100):.1f}%')
        
        if success_count == total_count:
            print('✅ 所有API端点测试通过!')
        else:
            print('❌ 部分API端点测试失败，请检查。')
            
    else:
        print(f'登录失败，状态码: {login_response.status_code}')
        print(f'登录响应: {login_response.text}')
        
except Exception as e:
    print(f'测试过程中发生错误: {str(e)}')
    import traceback
    traceback.print_exc()
finally:
    print('\n=== 测试结束 ===')