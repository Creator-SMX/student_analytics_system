# 直接测试get_cluster函数，不依赖Flask服务器

# 添加项目根目录到Python路径
import sys
import os

# 获取当前脚本所在目录的父目录
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入需要的模块
from analytics.analytics_controller import analytics_bp, get_cluster
from flask import Flask, json

# 创建一个最小的Flask应用实例用于测试
app = Flask(__name__)
app.register_blueprint(analytics_bp, url_prefix='/analytics')

# 测试函数
def test_cluster_function():
    print("开始测试get_cluster函数...")
    
    try:
        # 使用Flask测试客户端调用API
        with app.test_client() as client:
            # 发送GET请求到聚类数据API
            response = client.get('/analytics/api/get_cluster')
            
            # 检查响应状态码
            if response.status_code == 200:
                # 解析JSON响应
                data = json.loads(response.data)
                
                # 打印响应数据
                print("测试成功！获取到聚类数据：")
                print(f"总消费人数: {data.get('total_consumers')}")
                print(f"各类别人数: {data.get('counts')}")
                print(f"类别标签: {data.get('labels')}")
                print(f"各类别百分比: {data.get('percentages')}")
                
                # 验证数据完整性
                if all(field in data for field in ['counts', 'labels', 'percentages', 'total_consumers', 'thresholds']):
                    print("\n数据完整性验证通过！")
                    
                    # 验证各类别人数总和等于总消费人数
                    counts_sum = sum(data.get('counts', []))
                    if counts_sum == data.get('total_consumers'):
                        print(f"人数一致性验证通过！各类别人数总和({counts_sum})等于总消费人数({data.get('total_consumers')})")
                    else:
                        print(f"警告：人数不一致！各类别人数总和({counts_sum})不等于总消费人数({data.get('total_consumers')})")
                    
                    return True
                else:
                    print("数据完整性验证失败！缺少必要字段。")
                    return False
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.data.decode('utf-8')}")
                return False
                
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cluster_function()
    print(f"\n测试{'通过' if success else '失败'}")