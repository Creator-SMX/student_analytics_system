import requests
import json

# 测试API端点结构
def test_api_endpoints():
    print("=== 测试API端点数据结构 ===\n")
    
    # 1. 获取登录token - 尝试GET方法
    try:
        login_url = 'http://localhost:5000/login?username=admin&password=admin123'
        login_response = requests.get(login_url)
        
        if login_response.status_code == 200 or login_response.status_code == 302:
            print("✅ 登录成功!")
            cookies = login_response.cookies
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录错误: {str(e)}")
        return None
    
    # 2. 测试get_cluster端点（聚类数据）
    try:
        cluster_url = 'http://localhost:5000/analytics/analytics/api/get_cluster'
        cluster_response = requests.get(cluster_url, cookies=cookies)
        
        if cluster_response.status_code == 200:
            cluster_data = cluster_response.json()
            print("\n✅ get_cluster 端点测试成功")
            print(f"数据结构: {list(cluster_data.keys())}")
            print(f"标签: {cluster_data.get('labels')}")
            print(f"计数: {cluster_data.get('counts')}")
            print(f"百分比: {cluster_data.get('percentages')}")
            
            # 计算总数
            total_count = sum(cluster_data.get('counts', []))
            print(f"\n📊 聚类数据计算的学生总数: {total_count}")
        else:
            print(f"\n❌ get_cluster 端点失败: {cluster_response.status_code}")
            print(f"响应: {cluster_response.text}")
    except Exception as e:
        print(f"\n❌ get_cluster 端点错误: {str(e)}")
    
    # 3. 测试get_consumption_query端点（食堂消费数据）
    try:
        query_url = 'http://localhost:5000/analytics/analytics/api/get_consumption_query'
        query_response = requests.get(query_url, cookies=cookies)
        
        if query_response.status_code == 200:
            query_data = query_response.json()
            print("\n✅ get_consumption_query 端点测试成功")
            print(f"数据结构: {list(query_data.keys())}")
            print(f"示例数据: {json.dumps(query_data, ensure_ascii=False, indent=2)[:300]}...")
        else:
            print(f"\n❌ get_consumption_query 端点失败: {query_response.status_code}")
            print(f"响应: {query_response.text}")
    except Exception as e:
        print(f"\n❌ get_consumption_query 端点错误: {str(e)}")
    
    return cookies

if __name__ == '__main__':
    test_api_endpoints()