import requests
import json

# 测试API - 使用正确的URL格式
url = 'http://127.0.0.1:5000/analytics/api/test_price_distribution'

print(f"测试API: {url}")
try:
    # 使用更简单的请求，不添加额外的头部
    response = requests.get(url, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应内容类型: {response.headers.get('Content-Type')}")
    
    # 只打印前200字符，避免输出过长
    response_text = response.text
    print(f"响应内容前200字符: {response_text[:200]}...")
    
    # 如果是JSON，打印解析结果
    if 'application/json' in response.headers.get('Content-Type', ''):
        try:
            data = response.json()
            print("\nJSON数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"\nJSON解析错误: {e}")
    
    # 检查是否是HTML错误页面
    elif '<html' in response_text.lower():
        print("\n这是一个HTML页面，可能是错误页面")
        if '404' in response_text:
            print("检测到404错误")
        elif '403' in response_text:
            print("检测到403错误")
        elif '401' in response_text:
            print("检测到401错误")
        
except Exception as e:
    print(f"请求失败: {e}")

# 尝试使用curl命令（如果可用）
print("\n尝试使用curl命令:")
try:
    import subprocess
    result = subprocess.run(
        ['curl', '-s', url],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"Curl退出码: {result.returncode}")
    print(f"Curl输出前200字符: {result.stdout[:200]}...")
except Exception as e:
    print(f"Curl命令失败: {e}")