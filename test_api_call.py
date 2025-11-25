import requests
import json

def test_consumption_api():
    """测试消费记录API调用"""
    try:
        # API URL
        url = "http://localhost:5000/admin/consumption/list"
        
        # 直接使用requests调用（注意：这可能需要先登录获取session cookie）
        print("尝试调用消费记录API...")
        
        # 先尝试不带筛选条件的调用
        response = requests.get(url, params={
            'page': 1,
            'per_page': 10
        })
        
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nAPI返回数据:")
            print(f"成功状态: {data.get('success')}")
            print(f"总记录数: {data.get('total_count')}")
            print(f"返回记录数: {len(data.get('data', []))}")
            
            if data.get('data'):
                print("\n前3条返回记录:")
                for i, record in enumerate(data['data'][:3]):
                    print(f"记录 {i+1}:")
                    print(f"  校园卡号: {record.get('card_no')}")
                    print(f"  学号: {record.get('peo_no')}")
                    print(f"  消费时间: {record.get('date_time')}")
                    print(f"  消费金额: {record.get('money')}")
                    print(f"  消费地点: {record.get('dept')}")
        else:
            print(f"API调用失败: {response.text}")
            print("\n可能需要先登录，请检查是否有认证问题。")
            
    except Exception as e:
        print(f"API调用过程中发生错误: {str(e)}")

def check_api_with_authentication():
    """尝试登录后再调用API"""
    try:
        session = requests.Session()
        
        # 登录URL
        login_url = "http://localhost:5000/auth/login"
        
        print("\n尝试登录系统...")
        login_response = session.post(login_url, data={
            'username': 'admin',
            'password': 'admin123'  # 假设默认密码
        })
        
        print(f"登录状态码: {login_response.status_code}")
        
        if login_response.status_code in [200, 302]:  # 200成功或302重定向
            print("登录成功！")
            
            # 使用登录后的session调用消费记录API
            api_url = "http://localhost:5000/admin/consumption/list"
            response = session.get(api_url, params={
                'page': 1,
                'per_page': 10
            })
            
            print(f"\n消费记录API状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n登录后API返回数据:")
                print(f"成功状态: {data.get('success')}")
                print(f"总记录数: {data.get('total_count')}")
                print(f"返回记录数: {len(data.get('data', []))}")
                
                # 测试带筛选条件的调用
                filtered_response = session.get(api_url, params={
                    'page': 1,
                    'per_page': 10,
                    'card_no': '181316'
                })
                
                if filtered_response.status_code == 200:
                    filtered_data = filtered_response.json()
                    print(f"\n筛选后返回记录数: {len(filtered_data.get('data', []))}")
            else:
                print(f"API调用失败: {response.text}")
        else:
            print("登录失败，请检查用户名密码")
            
    except Exception as e:
        print(f"认证过程中发生错误: {str(e)}")

if __name__ == "__main__":
    print("===== 消费记录API测试 =====\n")
    test_consumption_api()
    check_api_with_authentication()