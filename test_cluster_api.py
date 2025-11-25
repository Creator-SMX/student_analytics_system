import requests
import json

# 测试get_cluster API
def test_cluster_api():
    try:
        # 构建API URL
        url = "http://localhost:5000/api/get_cluster"
        
        # 发送GET请求
        response = requests.get(url)
        
        # 检查响应状态码
        if response.status_code == 200:
            # 解析JSON响应
            data = response.json()
            
            # 打印响应数据
            print("测试成功！获取到聚类数据：")
            print(f"总消费人数: {data.get('total_consumers')}")
            print(f"各类别人数: {data.get('counts')}")
            print(f"类别标签: {data.get('labels')}")
            print(f"各类别百分比: {data.get('percentages')}")
            print(f"阈值标准: {data.get('thresholds')}")
            
            # 验证数据完整性
            if all(field in data for field in ['counts', 'labels', 'percentages', 'total_consumers', 'thresholds']):
                print("\n数据完整性验证通过！")
                
                # 验证各类别人数总和等于总消费人数
                counts_sum = sum(data.get('counts', []))
                if counts_sum == data.get('total_consumers'):
                    print(f"人数一致性验证通过！各类别人数总和({counts_sum})等于总消费人数({data.get('total_consumers')})")
                else:
                    print(f"警告：人数不一致！各类别人数总和({counts_sum})不等于总消费人数({data.get('total_consumers')})")
                
                # 验证百分比总和
                percentages_sum = sum(data.get('percentages', []))
                if 99.9 <= percentages_sum <= 100.1:  # 允许小数误差
                    print(f"百分比一致性验证通过！百分比总和约为100%({percentages_sum:.1f}%)")
                else:
                    print(f"警告：百分比不一致！百分比总和为{percentages_sum:.1f}%")
            else:
                print("数据完整性验证失败！缺少必要字段。")
                
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    print("开始测试聚类数据API...")
    test_cluster_api()
    print("\n测试完成。")