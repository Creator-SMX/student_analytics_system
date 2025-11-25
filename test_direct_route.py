import requests
import json

url = "http://127.0.0.1:5000/api/price_distribution_test"

def test_direct_route():
    print(f"测试直接路由: {url}")
    
    try:
        # 发送请求
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        # 检查状态码
        if response.status_code == 200:
            print("✅ 请求成功！")
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return True
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求出错: {e}")
        return False

if __name__ == "__main__":
    test_direct_route()