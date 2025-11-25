"""测试get_cluster函数的脚本"""
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from analytics.analytics_controller import get_cluster
from flask import Flask
from unittest.mock import patch, MagicMock

# 创建一个测试Flask应用
app = Flask(__name__)

# 设置测试上下文
def test_get_cluster_function():
    """使用模拟数据测试get_cluster函数"""
    print("开始测试get_cluster函数...")
    
    try:
        # 构建模拟的数据库连接和结果
        mock_conn = MagicMock()
        
        # 模拟总消费人数查询结果
        mock_total_result = MagicMock()
        mock_total_result.total_count = 8636
        
        # 模拟各类型查询结果
        mock_result1 = MagicMock()
        mock_result1.count = 2383  # 节约型
        
        mock_result2 = MagicMock()
        mock_result2.count = 1313  # 极简型
        
        mock_result3 = MagicMock()
        mock_result3.count = 1885  # 普通型
        
        mock_result4 = MagicMock()
        mock_result4.count = 2425  # 活跃型
        
        mock_result5 = MagicMock()
        mock_result5.count = 575   # 土豪型
        
        # 设置execute方法按顺序返回不同的模拟结果
        mock_conn.execute.side_effect = [
            mock_total_result,
            mock_result1,
            mock_result2,
            mock_result3,
            mock_result4,
            mock_result5
        ]
        
        # 使用patch模拟db_conn
        with patch('analytics.analytics_controller.db_conn') as mock_db_conn:
            mock_db_conn.connect.return_value = mock_conn
            
            # 进入Flask应用上下文
            with app.test_request_context('/api/get_cluster'):
                # 调用函数
                response = get_cluster()
                
                # 解析响应数据
                response_data = response.get_json()
                
                # 打印响应数据以便查看
                print("\n响应数据:")
                print(json.dumps(response_data, ensure_ascii=False, indent=2))
                
                # 验证响应数据
                if response_data:
                    # 检查必要字段
                    required_fields = ['counts', 'labels', 'percentages', 'total_consumers', 'thresholds']
                    all_fields_present = all(field in response_data for field in required_fields)
                    
                    if all_fields_present:
                        # 验证总消费人数
                        if response_data['total_consumers'] == 8636:
                            print("✓ 总消费人数正确")
                        else:
                            print(f"✗ 总消费人数不正确: 期望8636, 得到{response_data['total_consumers']}")
                        
                        # 验证各类别数量总和
                        total_count = sum(response_data['counts'])
                        if total_count == 8636:
                            print("✓ 各类别数量总和正确")
                        else:
                            print(f"✗ 各类别数量总和不正确: 期望8636, 得到{total_count}")
                        
                        # 验证百分比总和
                        total_percentage = sum(response_data['percentages'])
                        if 99.9 <= total_percentage <= 100.1:  # 允许小数点误差
                            print("✓ 百分比总和正确")
                        else:
                            print(f"✗ 百分比总和不正确: 期望约100%, 得到{total_percentage}%")
                        
                        print("\n测试成功: get_cluster函数返回了预期的结构和数据格式")
                        return True
                    else:
                        print(f"✗ 缺少必要字段: {[field for field in required_fields if field not in response_data]}")
                else:
                    print("✗ 响应数据为空")
                    
    except Exception as e:
        print(f"✗ 测试过程中出现错误: {str(e)}")
    
    print("\n测试失败: 函数未按预期工作")
    return False

# 执行测试
if __name__ == "__main__":
    test_get_cluster_function()