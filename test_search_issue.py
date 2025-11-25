import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/admin/consumption"
LIST_API = f"{BASE_URL}/list"
CARD_API = f"{BASE_URL}/card-numbers"

# 设置会话
session = requests.Session()

# 测试获取校园卡号
def test_get_card_numbers():
    print("\n测试获取校园卡号:")
    response = session.get(CARD_API)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 获取成功")
        if data.get('success') and data.get('card_numbers'):
            print(f"  找到 {len(data['card_numbers'])} 个校园卡号")
            print(f"  示例卡号: {data['card_numbers'][:5]}")
            return data['card_numbers']
        else:
            print(f"  但没有找到卡号数据: {data}")
            return []
    else:
        print(f"✗ 获取失败: {response.status_code} - {response.text[:200]}...")
        return []

# 测试搜索消费记录
def test_search_consumption_records(card_numbers, conditions):
    print(f"\n测试搜索条件: {conditions}")
    
    # 构建查询参数
    params = {}
    if conditions.get('card_no'):
        params['card_no'] = conditions['card_no']
    if conditions.get('start_date'):
        params['start_date'] = conditions['start_date']
    if conditions.get('end_date'):
        params['end_date'] = conditions['end_date']
    params['page'] = 1
    params['per_page'] = 10
    
    # 记录请求信息
    print(f"  请求URL: {LIST_API}")
    print(f"  请求参数: {params}")
    
    # 发送请求
    response = session.get(LIST_API, params=params)
    
    # 处理响应
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 请求成功")
        print(f"  总记录数: {data.get('total_count', 0)}")
        print(f"  当前页: {data.get('page', 0)} / {data.get('total_pages', 0)}")
        
        # 打印前几条记录作为示例
        records = data.get('data', [])
        print(f"  返回记录数: {len(records)}")
        if len(records) > 0:
            print("  前3条记录示例:")
            for i, record in enumerate(records[:3]):
                print(f"    {i+1}. 卡号: {record.get('card_no')}, 时间: {record.get('date_time')}, 金额: {record.get('money')}, 部门: {record.get('dept')}")
        else:
            print("  无返回记录")
        
        return data
    else:
        print(f"✗ 请求失败: {response.status_code} - {response.text[:200]}...")
        return None

# 测试直接查询数据库中的数据范围
def test_direct_db_query():
    print("\n测试数据库连接并查询数据范围:")
    import pymysql
    
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # 查询日期范围
            cursor.execute("SELECT MIN(date_time) as min_date, MAX(date_time) as max_date FROM consumption_records WHERE date_time != 'date_time'")
            date_range = cursor.fetchone()
            print(f"  数据库中的日期范围: {date_range}")
            
            # 查询总记录数
            cursor.execute("SELECT COUNT(*) as total FROM consumption_records WHERE date_time != 'date_time'")
            total_records = cursor.fetchone()['total']
            print(f"  数据库中的总记录数: {total_records}")
            
            # 查询前5条记录
            cursor.execute("SELECT card_no, date_time, money, dept FROM consumption_records WHERE date_time != 'date_time' ORDER BY date_time DESC LIMIT 5")
            sample_records = cursor.fetchall()
            print("  前5条记录示例:")
            for record in sample_records:
                print(f"    卡号: {record.get('card_no')}, 时间: {record.get('date_time')}, 金额: {record.get('money')}, 部门: {record.get('dept')}")
        
        connection.close()
    except Exception as e:
        print(f"✗ 数据库查询失败: {str(e)}")

# 修复export_consumption_records方法的调用参数问题
def fix_export_method():
    print("\n检查并修复export_consumption_records方法的参数问题:")
    try:
        # 读取当前的controller文件
        controller_path = "d:\\Pycharm\\PcData\\student_analytics_system\\admin\\consumption_controller.py"
        with open(controller_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查并修复调用问题
        if 'csv_data = ConsumptionModel.export_consumption_records(search=card_no)' in content:
            print("✓ 发现问题: 导出方法调用参数不完整")
            
            # 修改为正确的调用方式
            new_content = content.replace(
                'csv_data = ConsumptionModel.export_consumption_records(search=card_no)',
                'csv_data = ConsumptionModel.export_consumption_records(card_no=card_no, start_date=start_date, end_date=end_date)'
            )
            
            # 写回文件
            with open(controller_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✓ 已修复: export_consumption_records方法调用，现在传递所有筛选参数")
        else:
            print("✓ 未发现需要修复的导出方法调用问题")
            
        # 更新模型中的export_consumption_records方法
        model_path = "d:\\Pycharm\\PcData\\student_analytics_system\\admin\\models.py"
        with open(model_path, 'r', encoding='utf-8') as f:
            model_content = f.read()
        
        # 检查方法签名
        if '@staticmethod\n    def export_consumption_records(search=\'\'):' in model_content:
            print("✓ 需要更新模型中的导出方法以支持完整的筛选参数")
            
            # 添加必要的导入
            if 'import io' not in model_content:
                model_content = model_content.replace('import pymysql', 'import pymysql\nimport io\nimport csv')
            if 'from flask import make_response' not in model_content:
                model_content = model_content.replace('from flask import Flask', 'from flask import Flask, make_response')
            
            # 更新方法
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
                WHERE 1=1
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
            
            # 使用精确的正则替换
            import re
            pattern = r'@staticmethod\s+def export_consumption_records\(search=\'\'\):.*?finally:\s+if connection:\s+connection.close()'
            model_content = re.sub(pattern, new_method, model_content, flags=re.DOTALL)
            
            # 写回文件
            with open(model_path, 'w', encoding='utf-8') as f:
                f.write(model_content)
            
            print("✓ 已更新: 模型中的导出方法现在支持完整的筛选功能")
        else:
            print("✓ 模型中的导出方法已经是最新版本")
    except Exception as e:
        print(f"✗ 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()

# 主函数
def main():
    print("=== 消费记录搜索功能测试 ===")
    print("注意：为了简化测试，我们直接测试API而不通过登录流程")
    
    # 2. 修复方法参数问题
    fix_export_method()
    
    # 3. 获取校园卡号
    card_numbers = test_get_card_numbers()
    
    # 4. 查询数据库数据范围
    test_direct_db_query()
    
    # 5. 测试不同的搜索条件
    
    # 测试1: 不带任何筛选条件（查询所有数据）
    test_search_consumption_records(card_numbers, {})
    
    # 测试2: 只使用校园卡号筛选
    if card_numbers:
        test_search_consumption_records(card_numbers, {"card_no": card_numbers[0]})
    
    # 测试3: 只使用日期范围筛选（使用2019年4月）
    test_search_consumption_records(card_numbers, {"start_date": "2019-04-01", "end_date": "2019-04-30"})
    
    # 测试4: 组合条件筛选（卡号+日期范围）
    if card_numbers:
        test_search_consumption_records(card_numbers, {
            "card_no": card_numbers[0], 
            "start_date": "2019-04-01", 
            "end_date": "2019-04-30"
        })
    
    print("\n=== 测试完成 ===")
    print("\n问题分析:")
    print("1. 请检查日期格式是否正确 - 前端使用YYYY/MM/DD，后端期望YYYY-MM-DD")
    print("2. 请检查数据库中是否存在符合条件的数据")
    print("3. 前端页面中的错误信息 'net::ERR_BLOCKED_BY_ORB' 是由于无法加载头像图片，不会影响搜索功能")
    print("4. 可能的API权限问题 - 需要先登录才能访问API")
    print("5. 数据库连接或查询问题 - 检查日期字段格式和数据库索引")

if __name__ == "__main__":
    main()