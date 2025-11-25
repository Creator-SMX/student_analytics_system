import requests

url = "http://127.0.0.1:5000/analytics/api/test_price_distribution"

print(f"测试API: {url}")
try:
    response = requests.get(url, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应内容类型: {response.headers.get('content-type')}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        if response.headers.get('content-type') == 'application/json':
            try:
                data = response.json()
                print(f"成功获取JSON数据")
                print(f"数据结构: {list(data.keys())}")
                if 'price_distribution' in data:
                    print(f"价格分布数据: {data['price_distribution']}")
            except Exception as e:
                print(f"JSON解析失败: {str(e)}")
        else:
            print(f"响应不是JSON格式")
except Exception as e:
    print(f"请求失败: {str(e)}")