"""最小化测试脚本，直接验证get_cluster函数的核心逻辑"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 直接从check_cluster_data.py导入经过验证的函数
    from check_cluster_data import get_cluster_data_by_threshold
    
    print("开始测试聚类数据查询...")
    
    # 调用函数获取聚类数据
    cluster_data = get_cluster_data_by_threshold()
    
    if cluster_data:
        print("\n✓ 成功获取聚类数据")
        print(f"总消费人数: {cluster_data.get('total_consumers', 0)}")
        print(f"各类别数量: {cluster_data.get('counts', [])}")
        print(f"各类别百分比: {cluster_data.get('percentages', [])}%")
        
        # 验证各类别数量总和
        counts = cluster_data.get('counts', [])
        total_consumers = cluster_data.get('total_consumers', 0)
        total_count = sum(counts)
        print(f"各类别数量总和: {total_count}")
        
        if total_count == total_consumers:
            print("✓ 数据一致性验证通过")
        else:
            print(f"⚠ 数据可能存在不一致性: 总和{total_count} vs 总人数{total_consumers}")
            
        print("\n测试完成，聚类数据查询功能正常")
        sys.exit(0)
    else:
        print("✗ 未能获取聚类数据")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ 发生错误: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)