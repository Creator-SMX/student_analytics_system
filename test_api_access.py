import requests
import json
import time

def test_access_card_api():
    print("开始测试门禁卡号API...")
    url = "http://localhost:5000/api/access-card-numbers"
    print(f"测试API URL: {url}")
    print(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        print("准备发送GET请求...")
        # 发送请求，设置超时
        response = requests.get(url, timeout=10)
        print("请求已发送，等待响应...")
        
        # 打印响应状态码
        print(f"响应状态码: {response.status_code}")
        
        # 详细打印响应头
        print("响应头详情:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        # 打印响应内容长度
        print(f"响应内容长度: {len(response.content)} 字节")
        
        # 尝试解析JSON响应
        try:
            data = response.json()
            print(f"响应内容类型: {type(data)}")
            if isinstance(data, dict):
                print(f"响应数据键: {list(data.keys())}")
            print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError as json_error:
            print(f"JSON解析错误: {json_error}")
            print(f"无法解析JSON响应，原始内容: {response.text[:500]}...")
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
    
    print("测试结束")

if __name__ == "__main__":
    test_access_card_api()