"""诊断脚本：检查analytics_controller.py的修改和潜在问题"""
import os
import re

print("===== 开始诊断analytics_controller.py =====")

try:
    # 读取文件内容
    file_path = 'analytics/analytics_controller.py'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✓ 成功读取文件: {file_path}")
        
        # 检查get_cluster函数的修改
        print("\n----- 检查get_cluster函数修改 -----")
        
        # 检查是否还有硬编码数据
        hardcoded_patterns = [
            r'counts:\s*\[\s*2383\s*,\s*1313\s*,\s*1885\s*,\s*2425\s*,\s*575\s*\]',
            r'percentages:\s*\[\s*27\.8\s*,\s*15\.3\s*,\s*22\.0\s*,\s*28\.3\s*,\s*6\.7\s*\]',
            r'total_consumers:\s*8636'
        ]
        
        has_hardcoded = False
        for pattern in hardcoded_patterns:
            if re.search(pattern, content):
                has_hardcoded = True
                print(f"✗ 发现硬编码数据模式: {pattern}")
        
        if not has_hardcoded:
            print("✓ 未发现硬编码数据")
        
        # 检查是否包含money > 0过滤
        if 'WHERE money > 0' in content:
            print("✓ 包含money > 0过滤条件")
        else:
            print("✗ 缺少money > 0过滤条件")
        
        # 检查是否包含正确的查询结构
        query_patterns = [
            r'SELECT COUNT\(DISTINCT card_no\)',
            r'total_amount BETWEEN',
            r'total_amount < 122.90',
            r'total_amount >= 491.62'
        ]
        
        for pattern in query_patterns:
            if pattern in content:
                print(f"✓ 包含查询模式: {pattern}")
            else:
                print(f"✗ 缺少查询模式: {pattern}")
        
        # 检查import语句
        print("\n----- 检查import语句 -----")
        if 'from sqlalchemy import text' in content:
            print("✓ 包含必要的sqlalchemy import")
        else:
            print("✗ 缺少sqlalchemy text导入")
        
        # 检查try-finally结构
        if 'finally:' in content and 'db_conn.disconnect()' in content:
            print("✓ 包含正确的连接关闭机制")
        else:
            print("✗ 缺少连接关闭机制")
        
        # 检查函数结构完整性
        print("\n----- 检查函数结构完整性 -----")
        function_start = content.find('def get_cluster():')
        function_end = content.find('finally:', function_start)
        
        if function_start != -1 and function_end != -1:
            print("✓ get_cluster函数结构完整")
        else:
            print("✗ get_cluster函数结构不完整")
        
        # 检查是否有明显的语法错误
        print("\n----- 检查常见语法问题 -----")
        common_issues = [
            ('print(f"获取聚类数据错误:', '✓ 包含错误日志输出'),
            ('return jsonify(', '✓ 包含正确的返回语句'),
            ('for count in counts:', '✓ 包含百分比计算循环'),
            ('thresholds = {', '✓ 包含阈值定义')
        ]
        
        for text, message in common_issues:
            if text in content:
                print(message)
            else:
                print(f"✗ 缺少: {text}")
        
        print("\n===== 诊断完成 =====")
    else:
        print(f"✗ 文件不存在: {file_path}")
except Exception as e:
    print(f"✗ 诊断过程中出现错误: {str(e)}")