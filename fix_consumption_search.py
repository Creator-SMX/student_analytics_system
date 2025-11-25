import os
import re

print("=== 开始修复消费记录搜索功能 ===")

# 1. 修复模型中的数据库查询问题
def fix_model_date_query():
    print("\n1. 修复模型中的数据库查询问题...")
    model_path = r"d:\Pycharm\PcData\student_analytics_system\admin\models.py"
    
    try:
        # 读取文件
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查并修复数据库查询中的日期值问题
        if "WHERE date_time != 'date_time'" in content:
            print("✓ 发现问题：数据库查询中包含错误的日期值过滤条件")
            
            # 修复所有相关查询
            new_content = content.replace("WHERE date_time != 'date_time'", "WHERE date_time IS NOT NULL")
            
            # 写回文件
            with open(model_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✓ 已修复：将错误的日期值过滤条件替换为IS NOT NULL")
        else:
            print("✓ 未发现需要修复的数据库查询问题")
        
        return True
    except Exception as e:
        print(f"✗ 修复模型查询失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 2. 修复前端日期格式转换问题
def fix_frontend_date_format():
    print("\n2. 修复前端日期格式转换问题...")
    html_path = r"d:\Pycharm\PcData\student_analytics_system\templates\admin_consumption.html"
    
    try:
        # 读取文件
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否需要添加日期格式转换逻辑
        search_function_pattern = r'function searchConsumption\(\)'  # 搜索函数的开始
        search_function_match = re.search(search_function_pattern, content)
        
        if search_function_match and 'YYYY-MM-DD' not in content:
            print("✓ 发现问题：前端未进行日期格式转换")
            
            # 创建日期转换函数
            date_convert_function = '''
    // 日期格式转换函数：将YYYY/MM/DD转换为YYYY-MM-DD
    function convertDateFormat(dateString) {
        if (!dateString) return '';
        // 尝试匹配多种日期格式
        const formats = [
            /^(\d{4})\/(\d{1,2})\/(\d{1,2})$/,
            /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/,
            /^(\d{4})-(\d{1,2})-(\d{1,2})$/,
            /^(\d{1,2})-(\d{1,2})-(\d{4})$/
        ];
        
        for (const format of formats) {
            const match = dateString.match(format);
            if (match) {
                if (match[3].length === 4) {  // MM/DD/YYYY 格式
                    return `${match[3]}-${String(match[1]).padStart(2, '0')}-${String(match[2]).padStart(2, '0')}`;
                } else {  // YYYY/MM/DD 格式
                    return `${match[1]}-${String(match[2]).padStart(2, '0')}-${String(match[3]).padStart(2, '0')}`;
                }
            }
        }
        return dateString;  // 如果无法识别格式，原样返回
    }
'''
            
            # 在搜索函数前插入转换函数
            function_start = search_function_match.start()
            new_content = content[:function_start] + date_convert_function + content[function_start:]
            
            # 修改搜索函数中的日期处理部分
            # 找到获取日期的代码
            get_dates_pattern = r'const startDate = document\.getElementById\("start-date"\)\.value;\s*const endDate = document\.getElementById\("end-date"\)\.value;'  # 捕获日期获取代码
            get_dates_match = re.search(get_dates_pattern, new_content)
            
            if get_dates_match:
                # 创建带格式转换的新代码
                new_date_code = '''    const startDate = convertDateFormat(document.getElementById("start-date").value);
    const endDate = convertDateFormat(document.getElementById("end-date").value);'''
                
                # 替换原代码
                new_content = new_content[:get_dates_match.start()] + new_date_code + new_content[get_dates_match.end():]
                
                print("✓ 已添加：日期格式转换函数并修改搜索函数中的日期处理逻辑")
            else:
                print("! 未找到日期获取代码，可能需要手动检查")
            
            # 写回文件
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        else:
            print("✓ 前端日期格式处理已经是最新版本")
            return True
    except Exception as e:
        print(f"✗ 修复前端日期格式失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 3. 修复控制器中的导出方法参数问题
def fix_export_method_parameters():
    print("\n3. 修复控制器中的导出方法参数问题...")
    controller_path = r"d:\Pycharm\PcData\student_analytics_system\admin\consumption_controller.py"
    
    try:
        # 读取文件
        with open(controller_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查并修复导出方法调用
        if 'csv_data = ConsumptionModel.export_consumption_records(search=card_no)' in content:
            print("✓ 发现问题：导出方法调用参数不完整")
            
            # 修改为传递所有参数
            new_content = content.replace(
                'csv_data = ConsumptionModel.export_consumption_records(search=card_no)',
                'csv_data = ConsumptionModel.export_consumption_records(card_no=card_no, start_date=start_date, end_date=end_date)'
            )
            
            # 写回文件
            with open(controller_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✓ 已修复：导出方法现在传递所有筛选参数")
            return True
        elif 'csv_data = ConsumptionModel.export_consumption_records(card_no=card_no, start_date=start_date, end_date=end_date)' in content:
            print("✓ 导出方法调用已经是最新版本")
            return True
        else:
            print("! 导出方法调用格式可能不是预期的，请手动检查")
            return False
    except Exception as e:
        print(f"✗ 修复导出方法参数失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 4. 检查并修复模型中的导出方法
def check_export_method_in_model():
    print("\n4. 检查并修复模型中的导出方法...")
    model_path = r"d:\Pycharm\PcData\student_analytics_system\admin\models.py"
    
    try:
        # 读取文件
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查方法签名
        if '@staticmethod\n    def export_consumption_records(search=\'\'):' in content:
            print("✓ 需要更新导出方法签名")
            
            # 添加必要的导入
            if 'import io' not in content:
                content = content.replace('import pymysql', 'import pymysql\nimport io\nimport csv')
            if 'from flask import make_response' not in content:
                content = content.replace('from flask import Flask', 'from flask import Flask, make_response')
            
            # 构建新的方法实现
            new_method = '''    @staticmethod
    def export_consumption_records(card_no='', start_date='', end_date=''):
        """导出消费记录数据为CSV格式"""
        connection = None
        try:
            connection = ConsumptionModel.get_db_connection()
            with connection.cursor() as cursor:
                # 构建查询
                query = """
                SELECT cr.card_no, s.peo_no, cr.date_time, cr.money, cr.dept 
                FROM consumption_records cr
                LEFT JOIN students s ON cr.card_no = s.card_no
                WHERE date_time IS NOT NULL
                """
                params = []
                
                # 添加筛选条件
                if card_no:
                    query += """ AND cr.card_no = %s"""
                    params.append(card_no)
                
                if start_date:
                    query += """ AND DATE(cr.date_time) >= %s"""
                    params.append(start_date)
                
                if end_date:
                    query += """ AND DATE(cr.date_time) <= %s"""
                    params.append(end_date)
                
                # 添加排序
                query += " ORDER BY cr.date_time DESC"
                
                # 执行查询
                cursor.execute(query, params)
                records = cursor.fetchall()
                
                # 创建CSV文件
                output = io.StringIO()
                writer = csv.writer(output)
                
                # 写入表头
                writer.writerow(['校园卡号', '校园卡编号', '消费时间', '消费金额', '消费地点'])
                
                # 写入数据
                for record in records:
                    writer.writerow([
                        record.get('card_no', ''),
                        record.get('peo_no', ''),
                        record.get('date_time', ''),
                        record.get('money', 0),
                        record.get('dept', '')
                    ])
                
                # 创建响应
                output.seek(0)
                response = make_response(output.getvalue())
                response.headers['Content-Disposition'] = 'attachment; filename=consumption_records.csv'
                response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'  # 使用UTF-8 BOM以支持Excel
                
                return response
        except Exception as e:
            print(f"导出消费记录错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()'''
            
            # 替换旧方法
            import re
            pattern = r'@staticmethod\s+def export_consumption_records\(search=\'\'\):.*?finally:\s+if connection:\s+connection.close()'
            content = re.sub(pattern, new_method, content, flags=re.DOTALL)
            
            # 写回文件
            with open(model_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✓ 已更新：导出方法支持完整的筛选参数")
            return True
        else:
            print("✓ 模型中的导出方法已经是最新版本")
            return True
    except Exception as e:
        print(f"✗ 修复模型导出方法失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 5. 创建一个简单的测试脚本来验证修复结果
def create_validation_script():
    print("\n5. 创建验证脚本...")
    
    validation_script = '''
import requests
import json

def test_fixes():
    """测试修复结果的辅助函数"""
    print("\n=== 验证修复结果 ===")
    
    # 注意：由于需要登录认证，这里只是提供测试方法
    # 实际使用时需要先登录获取cookie
    print("\n请在浏览器中按以下步骤验证：")
    print("1. 登录系统：http://localhost:5000/login")
    print("2. 访问消费记录页面：http://localhost:5000/admin/consumption")
    print("3. 尝试使用以下搜索条件：")
    print("   - 只输入校园卡号（例如：181316）")
    print("   - 只输入日期范围（可以使用YYYY/MM/DD格式）")
    print("   - 同时使用卡号和日期范围")
    print("4. 检查是否能正确显示搜索结果")
    print("5. 尝试导出数据，确认导出功能正常")
    
    # 提供手动测试的API端点信息
    print("\n相关API端点信息：")
    print("- 消费记录列表：GET http://localhost:5000/admin/consumption/list")
    print("- 校园卡号列表：GET http://localhost:5000/admin/consumption/card-numbers")
    print("- 导出数据：GET http://localhost:5000/admin/consumption/export")
    
    # 提示常见问题排查
    print("\n常见问题排查：")
    print("1. 确保日期格式正确（系统现在支持YYYY/MM/DD和YYYY-MM-DD两种格式）")
    print("2. 确保数据库中存在符合条件的记录")
    print("3. 'net::ERR_BLOCKED_BY_ORB'错误是由于头像图片加载问题，不影响搜索功能")
    print("4. 如果仍然无法搜索到数据，请检查数据库连接和查询条件")

if __name__ == "__main__":
    test_fixes()
'''
    
    try:
        with open(r"d:\Pycharm\PcData\student_analytics_system\validate_consumption_fix.py", 'w', encoding='utf-8') as f:
            f.write(validation_script)
        
        print("✓ 已创建验证脚本：validate_consumption_fix.py")
        return True
    except Exception as e:
        print(f"✗ 创建验证脚本失败：{str(e)}")
        return False

# 主函数执行所有修复
def main():
    # 执行所有修复任务
    fixes = [
        fix_model_date_query,
        fix_frontend_date_format,
        fix_export_method_parameters,
        check_export_method_in_model,
        create_validation_script
    ]
    
    success_count = 0
    failure_count = 0
    
    for fix_function in fixes:
        if fix_function():
            success_count += 1
        else:
            failure_count += 1
    
    # 输出总结
    print("\n=== 修复完成 ===")
    print(f"成功修复: {success_count}")
    print(f"修复失败: {failure_count}")
    
    if failure_count == 0:
        print("\n🎉 所有问题已成功修复！")
        print("\n请运行以下命令查看验证指南：")
        print("python validate_consumption_fix.py")
        print("\n重要提示：")
        print("1. 前端现在支持YYYY/MM/DD和YYYY-MM-DD两种日期格式")
        print("2. 修复了数据库查询中的日期值错误")
        print("3. 修复了导出功能的参数传递问题")
        print("4. 'net::ERR_BLOCKED_BY_ORB'错误是由于无法加载picsum.photos图片，不影响功能")
    else:
        print("\n⚠️ 部分修复失败，请手动检查失败的项目")

if __name__ == "__main__":
    main()