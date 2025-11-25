import requests
import time

# 等待服务器启动
time.sleep(2)

try:
    # 测试/project-report路由
    response = requests.get('http://127.0.0.1:5000/project-report')
    
    if response.status_code == 200:
        print("✅ 测试成功：/project-report路由可正常访问")
        print(f"页面内容长度：{len(response.text)} 字符")
        print("\n页面头部内容：")
        print(response.text[:500] + "...")
        
        # 检查是否包含AI提示词章节
        if "十一、AI提示词" in response.text:
            print("\n✅ 验证成功：页面包含'十一、AI提示词'章节")
        else:
            print("\n❌ 验证失败：页面不包含'十一、AI提示词'章节")
            
    else:
        print(f"❌ 测试失败：/project-report路由返回状态码 {response.status_code}")
        print(f"响应内容：{response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ 连接错误：无法连接到服务器，请检查服务器是否正常运行")
except Exception as e:
    print(f"❌ 测试失败：发生未知错误 - {str(e)}")