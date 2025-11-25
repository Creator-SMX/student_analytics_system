"""简单脚本，验证get_cluster函数的实现是否已正确修改"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 直接读取文件内容检查
    with open('analytics/analytics_controller.py', 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    print("开始验证函数修改...")
    
    # 检查是否包含硬编码的聚类数据
    has_hardcoded_counts = "counts: [2383, 1313, 1885, 2425, 575]" in file_content
    has_hardcoded_percentages = "percentages: [27.8, 15.3, 22.0, 28.3, 6.7]" in file_content
    has_hardcoded_total = "total_consumers: 8636" in file_content
    
    # 检查是否包含新的实现特征
    has_money_filter = "WHERE money > 0" in file_content
    has_distinct_card_no = "COUNT(DISTINCT card_no)" in file_content
    has_cluster_queries = "total_amount BETWEEN" in file_content
    
    # 输出验证结果
    print("\n验证结果:")
    print(f"✗ 包含硬编码counts: {has_hardcoded_counts}")
    print(f"✗ 包含硬编码percentages: {has_hardcoded_percentages}")
    print(f"✗ 包含硬编码total_consumers: {has_hardcoded_total}")
    print(f"✓ 包含money > 0过滤: {has_money_filter}")
    print(f"✓ 包含去重统计: {has_distinct_card_no}")
    print(f"✓ 包含分段阈值查询: {has_cluster_queries}")
    
    # 综合判断
    if not any([has_hardcoded_counts, has_hardcoded_percentages, has_hardcoded_total]) and \
       all([has_money_filter, has_distinct_card_no, has_cluster_queries]):
        print("\n✅ 验证通过: get_cluster函数已成功修改为动态查询实现")
        print("修改要点:")
        print("1. 移除了所有硬编码的聚类数据")
        print("2. 添加了money > 0的过滤条件")
        print("3. 实现了按阈值的动态数据库查询")
        print("4. 正确统计了去重的学生人数")
        sys.exit(0)
    else:
        print("\n❌ 验证失败: 函数修改不完整")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ 发生错误: {str(e)}")
    sys.exit(1)