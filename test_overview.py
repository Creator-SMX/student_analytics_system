import requests
import json

url = 'http://127.0.0.1:5000/analytics/api/get_overview'

print(f"测试 {url}")

response = requests.get(url, timeout=10)
print(f"状态码: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("价格分布数据:")
    print(json.dumps(data.get('price_distribution', {}), ensure_ascii=False, indent=2))
else:
    print(f"响应内容: {response.text}")