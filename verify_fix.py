import requests
import json

url = "http://127.0.0.1:5000/analytics/api/test_price_distribution"

def test_price_distribution_api():
    print(f"测试API: {url}")
    
    try:
        # 发送请求
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容类型: {response.headers.get('content-type')}")
        
        # 检查状态码
        if response.status_code != 200:
            print(f"❌ 错误: API返回状态码 {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        # 检查内容类型
        if 'application/json' not in response.headers.get('content-type', ''):
            print(f"❌ 错误: 响应不是JSON格式")
            print(f"响应内容: {response.text}")
            return False
        
        # 解析JSON
        try:
            data = response.json()
            print(f"✅ 成功解析JSON数据")
        except Exception as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"响应内容: {response.text}")
            return False
        
        # 验证数据结构
        print(f"数据结构: {list(data.keys())}")
        
        # 检查price_distribution字段
        if 'price_distribution' not in data:
            print(f"❌ 错误: 缺少price_distribution字段")
            return False
        
        price_distribution = data['price_distribution']
        print(f"✅ 价格分布数据存在: {price_distribution}")
        
        # 验证价格区间数据
        expected_ranges = ['0-5元', '5-10元', '10-20元', '20-50元', '50元以上']
        all_found = True
        
        for range_name in expected_ranges:
            if range_name in price_distribution:
                print(f"  ✅ {range_name}: {price_distribution[range_name]}")
            else:
                print(f"  ❌ 缺少 {range_name} 数据")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    print("开始验证价格分布API修复...")
    result = test_price_distribution_api()
    
    if result:
        print("\n🎉 API修复验证成功！价格分布数据已正确返回。")
    else:
        print("\n❌ API修复验证失败。")