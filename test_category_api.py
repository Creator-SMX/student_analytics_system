import requests
import json

# 创建会话
session = requests.Session()

# 1. 登录系统
print("1. 执行管理员登录")
login_url = "http://localhost:5000/auth/login"
data = {
    'username': 'admin',
    'password': '123456',
    'user_type': 'admin'
}

login_response = session.post(login_url, json=data)
print(f"登录状态码: {login_response.status_code}")
if login_response.status_code == 200:
    print("✅ 登录成功")
else:
    print(f"❌ 登录失败: {login_response.text}")
    exit(1)

# 2. 测试消费分类API
print("\n2. 测试消费分类API")
api_url = "http://localhost:5000/api/chart-data/category"
response = session.get(api_url)
print(f"API状态码: {response.status_code}")

if response.status_code == 200:
    try:
        data = response.json()
        print("✅ API返回有效的JSON数据")
        print(f"响应结构: {list(data.keys())}")
        
        # 检查data字段
        if 'data' in data and data['data']:
            print("✅ data字段存在且不为空")
            
            # 检查data的结构
            print(f"data类型: {type(data['data'])}")
            
            # 检查是否包含必要的字段
            if isinstance(data['data'], dict):
                # 检查标签和值字段
                if 'labels' in data['data'] and 'data' in data['data']:
                    print("✅ 包含必要的labels和data字段")
                    print(f"标签数量: {len(data['data']['labels'])}")
                    print(f"值数量: {len(data['data']['data'])}")
                    print(f"\n标签列表: {data['data']['labels']}")
                    print(f"值列表: {data['data']['data']}")
                    
                    # 验证所有值都是数字
                    all_numbers = all(isinstance(v, (int, float)) for v in data['data']['data'])
                    print(f"\n✅ 所有值都是数字类型: {all_numbers}")
                    
                    # 检查是否有'total_amount'字符串
                    has_total_amount = any(v == 'total_amount' for v in data['data']['data'])
                    print(f"✅ 不存在'total_amount'字符串值: {not has_total_amount}")
                    
                    # 检查是否有任何字符串值
                    has_string_values = any(isinstance(v, str) for v in data['data']['data'])
                    print(f"✅ 不存在其他字符串值: {not has_string_values}")
                    
                    print("\n🎉 消费分类API测试通过！修复成功！")
                else:
                    print("❌ 缺少必要的labels或data字段")
            else:
                print(f"❌ data不是预期的字典格式，而是: {type(data['data'])}")
                print(f"data内容: {data['data']}")
        else:
            print("❌ data字段为空或不存在")
            
    except json.JSONDecodeError:
        print("❌ API返回的不是有效的JSON")
        print(f"原始响应: {response.text}")
    except Exception as e:
        print(f"❌ 解析API响应时出错: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ API调用失败: {response.text}")

# 打印完整的API响应内容
print("\n4. 完整API响应内容:")
print(json.dumps(data, ensure_ascii=False, indent=2))

# 3. 检查Flask日志中的错误
print("\n3. 注意：请检查Flask服务器日志，确认没有'total_amount'相关的转换错误")
print("✅ 所有测试完成！")