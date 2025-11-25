import requests
import json

# 登录URL
login_url = "http://localhost:5000/auth/login"

# 管理员登录凭据
data = {
    'username': 'admin',
    'password': '123456',
    'user_type': 'admin'
}

print(f"执行管理员登录测试: {data}")

try:
    # 创建会话对象以保存Cookie
    session = requests.Session()
    
    # 发送POST请求进行登录
    response = session.post(login_url, json=data)
    
    print(f"登录状态码: {response.status_code}")
    print(f"登录响应: {response.text}")
    
    # 尝试解析JSON响应
    try:
        result = response.json()
        print(f"JSON解析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success'):
            print("✅ 登录成功！")
            
            # 测试访问报告页面
            report_url = "http://localhost:5000/analytics/report"
            print(f"\n尝试访问报告页面: {report_url}")
            report_response = session.get(report_url)
            print(f"报告页面状态码: {report_response.status_code}")
            
            if report_response.status_code == 200:
                print("✅ 成功访问报告页面！")
                
                # 测试消费分类API
                api_url = "http://localhost:5000/api/chart-data/category"
                print(f"\n测试消费分类API: {api_url}")
                api_response = session.get(api_url)
                print(f"API状态码: {api_response.status_code}")
                
                if api_response.status_code == 200:
                    print("✅ API调用成功！")
                    api_data = api_response.json()
                    print(f"API数据类型: {type(api_data)}")
                    print(f"API数据概览: {api_data.keys() if isinstance(api_data, dict) else '非字典格式'}")
                else:
                    print(f"❌ API调用失败: {api_response.text}")
            else:
                print(f"❌ 访问报告页面失败: {report_response.text}")
        else:
            print(f"❌ 登录失败: {result.get('message')}")
            
    except json.JSONDecodeError:
        print("❌ 响应不是有效的JSON格式")
        print(f"原始响应: {response.text}")
        
    # 查看所有Cookie
    print("\n会话Cookie:")
    for cookie in session.cookies:
        print(f"- {cookie.name}: {cookie.value}")
        
except Exception as e:
    print(f"❌ 请求失败: {str(e)}")
    import traceback
    traceback.print_exc()