import requests

url = "http://127.0.0.1:5000/analytics/api/test_price_distribution"

try:
    response = requests.get(url, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"JSON数据: {data}")
        except Exception as e:
            print(f"JSON解析失败: {e}")
except Exception as e:
    print(f"请求失败: {e}")