import requests
import json

# API端点列表
api_endpoints = [
    '/analytics/api/get_overview',
    '/analytics/api/get_time_analysis',
    '/analytics/api/get_access_pattern',
    '/analytics/api/get_cluster',
    '/analytics/api/get_canteen_analysis'
]

# 基础URL（假设应用运行在本地5000端口）
base_url = 'http://localhost:5000'

# 测试结果
results = []

print("开始测试analytics API接口...")
print("="*60)

for endpoint in api_endpoints:
    url = base_url + endpoint
    try:
        response = requests.get(url)
        
        # 检查状态码
        if response.status_code == 200:
            # 尝试解析JSON
            data = response.json()
            results.append({
                'endpoint': endpoint,
                'status': '✅ 成功',
                'status_code': response.status_code,
                'has_data': len(data) > 0,  # 检查是否返回了数据
                'data_sample': json.dumps(data, ensure_ascii=False, indent=2)[:200] + '...'
            })
        else:
            results.append({
                'endpoint': endpoint,
                'status': '❌ 失败',
                'status_code': response.status_code,
                'has_data': False,
                'data_sample': f'错误: {response.text}'
            })
    except Exception as e:
        results.append({
            'endpoint': endpoint,
            'status': '❌ 异常',
            'status_code': None,
            'has_data': False,
            'data_sample': f'异常: {str(e)}'
        })

# 打印测试结果
print("测试结果汇总:")
print("="*60)
for result in results:
    print(f"端点: {result['endpoint']}")
    print(f"状态: {result['status']}")
    print(f"状态码: {result['status_code']}")
    print(f"包含data字段: {result['has_data']}")
    print(f"数据样本: {result['data_sample']}")
    print("-"*60)

# 总结
all_success = all(r['status_code'] == 200 and r['has_data'] for r in results)
print("\n测试总结:")
print(f"总测试端点数: {len(api_endpoints)}")
print(f"成功端点数: {sum(1 for r in results if r['status_code'] == 200 and r['has_data'])}")
print(f"失败端点数: {sum(1 for r in results if not (r['status_code'] == 200 and r['has_data']))}")
print(f"测试结果: {'全部通过' if all_success else '部分失败'}")