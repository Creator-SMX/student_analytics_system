import requests
import json

def test_api_endpoints():
    print("测试API端点...")
    
    # 测试价格分布API
    print("\n测试 /analytics/api/test_price_distribution:")
    try:
        response = requests.get("http://127.0.0.1:5000/analytics/api/test_price_distribution")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容类型: {response.headers.get('Content-Type')}")
        print(f"响应内容前1000字符: {response.text[:1000]}...")
        
        # 尝试解析JSON
        try:
            data = response.json()
            print("\nJSON解析成功:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("\nJSON解析失败")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {str(e)}")
    
    # 测试门禁卡号API
    print("\n测试 /api/access-card-numbers:")
    try:
        response = requests.get("http://127.0.0.1:5000/api/access-card-numbers")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {str(e)}")
    
    # 测试今日统计API
    print("\n测试 /api/access-stats-today:")
    try:
        response = requests.get("http://127.0.0.1:5000/api/access-stats-today")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {str(e)}")
    
    # 测试门禁记录API
    print("\n测试 /api/access-records:")
    try:
        response = requests.get("http://127.0.0.1:5000/api/access-records")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {str(e)}")

if __name__ == "__main__":
    test_api_endpoints()