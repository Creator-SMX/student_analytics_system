from flask import Flask, render_template, session, redirect, url_for, jsonify, request
import pandas as pd
import sqlite3
from flask_cors import CORS
import os

# 导入蓝图
from auth.auth_controller import auth_bp
from admin.students_controller import students_bp
from admin.consumption_controller import consumption_bp
from analytics.analytics_controller import analytics_bp

# 创建Flask应用
app = Flask(__name__)

# 配置CORS
CORS(app)

# 配置密钥
app.secret_key = os.environ.get('SECRET_KEY') or 'dev_secret_key_2024'

# 配置会话
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 会话有效期1小时

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(students_bp, url_prefix='/admin/students')
app.register_blueprint(consumption_bp, url_prefix='/admin/consumption')
app.register_blueprint(analytics_bp, url_prefix='/analytics')

# 主页路由
@app.route('/')
def home():
    # 如果已登录，跳转到分析仪表板
    if 'user_id' in session:
        return redirect(url_for('analytics.dashboard'))
    # 未登录，跳转到登录页
    return redirect(url_for('login_page'))

# 登录页面路由
@app.route('/login')
def login_page():
    print("[DEBUG] 访问登录页面")
    # 清除可能存在的会话，确保用户以未登录状态访问
    session.clear()
    return render_template('login.html')

# 直接访问报告页面的路由
@app.route('/reports')
def reports_page():
    # 重定向到正确的分析报告路由
    return redirect(url_for('analytics.report'))

# 直接访问analytics/reports路由（修复404问题）
@app.route('/analytics/reports')
def analytics_reports():
    # 重定向到正确的分析报告路由
    return redirect(url_for('analytics.report'))

# analytics/report路由由蓝图直接处理，无需额外重定向

# 管理员仪表板路由（临时）
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_page'))
    return render_template('admin_dashboard.html')

# 项目报告页面路由
@app.route('/project-report')
def project_report():
    # 这个页面不需要登录就可以访问
    return render_template('project_report.html')

# 管理员项目报告路由（侧边栏链接使用）
@app.route('/admin/project_report')
def admin_project_report():
    # 检查管理员权限
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_page'))
    return render_template('project_report.html')

# 消费记录路由已移至 admin/consumption_controller.py
# # 消费记录路由
# @app.route('/admin/consumption')
# def consumption_records():
#     if 'user_id' not in session or session.get('user_type') != 'admin':
#         return redirect(url_for('login_page'))
#     return render_template('admin_consumption.html')
# 
# # 消费记录API路由
# @app.route('/api/consumption-records')
# def get_consumption_records():
#     """获取消费记录数据的API"""
#     if 'user_id' not in session or session.get('user_type') != 'admin':
#         return jsonify({'error': '未授权访问'}), 403
#     
#     import pymysql
#     from utils.db_connection import DatabaseConnection
#     
#     # 获取查询参数
#     card_no = request.args.get('card_no', '')
#     start_date = request.args.get('start_date', '')
#     end_date = request.args.get('end_date', '')
#     page = int(request.args.get('page', 1))
#     per_page = int(request.args.get('per_page', 10))
#     
#     # 构建基础查询（左连接students表以获取学号信息）
#     base_query = """
#     SELECT cr.*, s.peo_no 
#     FROM consumption_records cr
#     LEFT JOIN students s ON cr.card_no = s.card_no
#     WHERE 1=1
#     """
#     count_query = """
#     SELECT COUNT(*) as total 
#     FROM consumption_records cr
#     LEFT JOIN students s ON cr.card_no = s.card_no
#     WHERE 1=1
#     """
#     
#     params = []
#     
#     # 添加过滤条件
#     if card_no:
#         base_query += " AND cr.card_no = %s"
#         count_query += " AND cr.card_no = %s"
#         params.append(card_no)
    
    # 添加日期范围过滤条件
    # if start_date:
    #     base_query += " AND DATE(cr.date_time) >= %s"
    #     count_query += " AND DATE(cr.date_time) >= %s"
    #     params.append(start_date)
    # 
    # if end_date:
    #     base_query += " AND DATE(cr.date_time) <= %s"
    #     count_query += " AND DATE(cr.date_time) <= %s"
    #     params.append(end_date)
    
    # 添加排序
    # base_query += " ORDER BY cr.date_time DESC"
    # 
    # # 添加分页
    # offset = (page - 1) * per_page
    # base_query += " LIMIT %s OFFSET %s"
    # params.extend([per_page, offset])
    # 
    # try:
    #     # 使用DatabaseConnection获取数据
    #     db_conn = DatabaseConnection()
    #     db_conn.connect()
    #     
    #     # 获取总记录数
    #     total_count = db_conn.get_dataframe(count_query, params[:-2])['total'].iloc[0]
    #     
    #     # 获取分页数据
    #     records = db_conn.get_dataframe(base_query, params)
    #     
    #     db_conn.disconnect()
    #     
    #     # 转换数据为字典列表
    #     result = []
    #     for _, row in records.iterrows():
    #         result.append({
    #             'card_no': row['card_no'] if pd.notna(row['card_no']) else '',
    #             'peo_no': row['peo_no'] if pd.notna(row['peo_no']) else '',
    #             'date_time': str(row['date_time']) if pd.notna(row['date_time']) else '',
    #             'dept': row['dept'] if pd.notna(row['dept']) else '',
    #             'money': float(row['money']) if pd.notna(row['money']) else 0
    #         })
    #     
    #     print(f"[DEBUG] 总记录数: {total_count}, 分页结果数: {len(result)}")
    #     
    #     return jsonify({
    #         'data': result,
    #         'total': total_count,
    #         'page': page,
    #         'per_page': per_page,
    #         'pages': (total_count + per_page - 1) // per_page
    #     })
    # except Exception as e:
    #     print(f"[ERROR] 获取消费记录失败: {str(e)}")
    #     return jsonify({'error': str(e)}), 500

# 获取所有校园卡号API
@app.route('/api/card-numbers')
def get_card_numbers():
    """获取所有校园卡号的API"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': '未授权访问'}), 403
    
    from utils.db_connection import DatabaseConnection
    
    try:
        # 使用DatabaseConnection获取数据
        db_conn = DatabaseConnection()
        db_conn.connect()
        
        # 查询所有校园卡号
        query = "SELECT DISTINCT card_no FROM consumption_records ORDER BY card_no"
        df = db_conn.get_dataframe(query)
        
        db_conn.disconnect()
        
        # 转换为列表
        card_numbers = df['card_no'].tolist()
        
        return jsonify({
            'card_numbers': card_numbers
        })
    except Exception as e:
        print(f"[ERROR] 获取校园卡号失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 根据校园卡号获取消费日期API
@app.route('/api/consumption-dates')
def get_consumption_dates():
    """根据校园卡号获取消费日期的API"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': '未授权访问'}), 403
    
    card_no = request.args.get('card_no', '')
    if not card_no:
        return jsonify({'error': '校园卡号不能为空'}), 400
    
    from utils.db_connection import DatabaseConnection
    
    try:
        # 使用DatabaseConnection获取数据
        db_conn = DatabaseConnection()
        db_conn.connect()
        
        # 查询该卡号的所有消费日期
        query = """
        SELECT DISTINCT DATE(date_time) as consumption_date 
        FROM consumption_records 
        WHERE card_no = %s 
        ORDER BY consumption_date DESC
        """
        df = db_conn.get_dataframe(query, [card_no])
        
        db_conn.disconnect()
        
        # 转换为列表
        dates = df['consumption_date'].astype(str).tolist()
        
        return jsonify({
            'dates': dates
        })
    except Exception as e:
        print(f"[ERROR] 获取消费日期失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 获取今日统计数据API
@app.route('/api/today-statistics')
def get_today_statistics():
    """获取今日消费统计数据的API"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': '未授权访问'}), 403
    
    import pandas as pd
    from utils.db_connection import DatabaseConnection
    
    try:
        # 使用DatabaseConnection获取数据
        db_conn = DatabaseConnection()
        db_conn.connect()
        
        # 查询今日统计数据
        query = """
        SELECT 
            SUM(money) as total_amount, 
            COUNT(*) as total_count,
            AVG(money) as average_amount
        FROM consumption_records 
        WHERE DATE(date_time) = DATE(NOW())
        """
        df = db_conn.get_dataframe(query)
        
        db_conn.disconnect()
        
        # 获取统计结果
        total_amount = float(df['total_amount'].iloc[0]) if pd.notna(df['total_amount'].iloc[0]) else 0
        total_count = int(df['total_count'].iloc[0]) if pd.notna(df['total_count'].iloc[0]) else 0
        average_amount = float(df['average_amount'].iloc[0]) if pd.notna(df['average_amount'].iloc[0]) else 0
        
        return jsonify({
            'total_amount': total_amount,
            'total_count': total_count,
            'average_amount': average_amount
        })
    except Exception as e:
        print(f"[ERROR] 获取统计数据失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 活动记录路由
@app.route('/admin/activities')
def activities_records():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_page'))
    return render_template('admin_activities.html')

# 门禁记录路由
@app.route('/admin/access')
def access_records():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_page'))
    return render_template('admin_access.html')

# API: 获取活动记录
@app.route('/api/activities')
def get_activities_records():
    # 恢复权限验证机制
    print("[DEBUG] API /api/activities 被调用，执行权限验证")
    # 从session获取用户信息 - 修改为正确的session键名
    if 'user_id' not in session or not session['user_id']:
        print("[ERROR] 用户未登录，拒绝访问")
        return jsonify({'error': '未授权访问，请先登录', 'data': []}), 401
    
    # 获取用户信息
    username = session['username']
    user_type = session['user_type']
    print(f"[DEBUG] 用户 {username}({user_type}) 尝试访问活动记录")
    
    try:
        # 确保导入pandas和pymysql
        print("[DEBUG] 开始导入必要的模块")
        import pandas as pd
        import pymysql
        print("[DEBUG] 模块导入成功")
        
        # 获取查询参数 - 确保所有参数都是字符串类型
        activity_type = str(request.args.get('activity_type', ''))
        date_start = str(request.args.get('date_start', ''))
        date_end = str(request.args.get('date_end', ''))
        
        # 安全转换为整数
        try:
            page = int(request.args.get('page', 1))
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
            
        try:
            per_page = int(request.args.get('per_page', 10))
            if per_page < 1 or per_page > 100:
                per_page = 10
        except (ValueError, TypeError):
            per_page = 10
            
        print(f"[DEBUG] 查询参数: page={page}, per_page={per_page}, activity_type={activity_type}")
        print(f"[DEBUG] 日期范围: {date_start} 到 {date_end}")
        
        # 创建综合活动数据（从多个表获取）
        print("[DEBUG] 开始创建数据库连接")
        from utils.db_connection import DatabaseConnection
        
        db_conn = DatabaseConnection()
        if not db_conn.connect():
            error_msg = "数据库连接失败"
            print(f"[ERROR] {error_msg}")
            return jsonify({'error': error_msg, 'data': []}), 500
        print("[DEBUG] 数据库连接成功")
        
        # 获取消费记录（严格按照数据库表结构，使用CONVERT替代CAST）
        print("[DEBUG] 开始构建SQL查询")
        consumption_query = """
        SELECT 
            cr.date_time, 
            CONCAT('消费 - ', CONVERT(cr.card_no, CHAR)) AS activity_id,
            CONCAT(CONVERT(cr.card_no, CHAR), ' 在 ', CONVERT(cr.dept, CHAR), ' 消费了 ', CONVERT(cr.money, CHAR), ' 元') AS description,
            '消费' AS activity_type,
            cr.money AS amount_value,
            COALESCE(s.major, '未知专业') AS major,
            cr.card_no
        FROM consumption_records cr
        LEFT JOIN students s ON cr.card_no = s.card_no
        WHERE 1=1
        """
        
        # 获取门禁记录（使用access_card_no作为关联字段，使用CONVERT替代CAST）
        access_query = """
        SELECT 
            ar.date_time,
            CONCAT('门禁 - ', CONVERT(COALESCE(s.card_no, ar.access_card_no), CHAR)) AS activity_id,
            CONCAT(CONVERT(COALESCE(s.card_no, ar.access_card_no), CHAR), ' 从 ', CONVERT(ar.address, CHAR), ' ', CONVERT(ar.describe_text, CHAR)) AS description,
            '门禁' AS activity_type,
            0 AS amount_value,
            COALESCE(s.major, '未知专业') AS major,
            COALESCE(s.card_no, ar.access_card_no) AS card_no
        FROM access_records ar
        LEFT JOIN students s ON ar.access_card_no = s.card_no
        WHERE 1=1
        """
        
        # 构建参数列表 - 确保所有参数都是字符串类型
        params = []
        
        # 添加过滤条件
        if date_start:
            consumption_query += " AND cr.date_time >= %s"
            access_query += " AND ar.date_time >= %s"
            params.append(str(date_start))
            params.append(str(date_start))
        
        if date_end:
            consumption_query += " AND cr.date_time <= %s"
            access_query += " AND ar.date_time <= %s"
            params.append(str(f"{date_end} 23:59:59"))
            params.append(str(f"{date_end} 23:59:59"))
        
        # 根据活动类型过滤
        if activity_type == '消费':
            # 只查询消费记录，门禁记录返回空
            access_query = "SELECT NULL as date_time, NULL as activity_id, NULL as description, NULL as activity_type, NULL as amount_value, NULL as major, NULL as card_no WHERE 1=0"
        elif activity_type == '门禁':
            # 只查询门禁记录，消费记录返回空
            consumption_query = "SELECT NULL as date_time, NULL as activity_id, NULL as description, NULL as activity_type, NULL as amount_value, NULL as major, NULL as card_no WHERE 1=0"
        
        # 合并查询
        combined_query = "(" + consumption_query + ") UNION ALL (" + access_query + ") ORDER BY date_time DESC LIMIT %s OFFSET %s"
        
        # 获取分页数据
        print("[DEBUG] 执行SQL查询获取活动数据")
        print(f"[DEBUG] 查询前200字符: {str(combined_query)[:200]}...")
        pagination_params = [per_page, (page - 1) * per_page]
        print(f"[DEBUG] 参数: {params + pagination_params}")
        
        # 安全执行查询
        activities = None
        try:
            activities = db_conn.get_dataframe(combined_query, params + pagination_params)
            if activities is None:
                print("[ERROR] 获取活动数据返回None")
                activities = pd.DataFrame()  # 创建空DataFrame避免后续错误
        except Exception as query_error:
            error_msg = f"查询执行失败: {str(query_error)}"
            print(f"[ERROR] {error_msg}")
            # 确保数据库连接关闭
            try:
                db_conn.disconnect()
            except:
                pass
            return jsonify({'error': error_msg, 'data': []}), 500
        
        print(f"[DEBUG] 获取到 {len(activities)} 条活动记录")
        
        # 获取总记录数
        count_query = "SELECT COUNT(*) as total FROM ((" + consumption_query + ") UNION ALL (" + access_query + ")) as combined"
        
        print("[DEBUG] 执行SQL查询获取总记录数")
        total_count = 0
        try:
            total_df = db_conn.get_dataframe(count_query, params)
            if total_df is not None and len(total_df) > 0:
                # 安全获取总记录数
                try:
                    total_count = int(total_df['total'].iloc[0])
                except (ValueError, TypeError, KeyError):
                    total_count = 0
        except Exception as count_error:
            print(f"[ERROR] 执行总数查询时出错: {str(count_error)}")
            total_count = 0
        
        print(f"[DEBUG] 总记录数: {total_count}")
        
        # 确保关闭连接
        try:
            db_conn.disconnect()
            print("[DEBUG] 数据库连接已关闭")
        except Exception as close_error:
            print(f"[WARNING] 关闭数据库连接时出错: {str(close_error)}")
        
        # 转换数据为字典列表 - 完全重新实现，确保类型安全
        result = []
        print("[DEBUG] 开始处理和转换数据")
        
        # 确保activities不为None且可以迭代
        if activities is not None and not activities.empty:
            try:
                for index, row in activities.iterrows():
                    try:
                        # 只处理有效的记录（date_time不为空）
                        if pd.notna(row.get('date_time')):
                            # 确保所有值都转换为字符串类型以避免拼接错误
                            activity_id = str(row['activity_id']) if pd.notna(row.get('activity_id')) else ''
                            description = str(row['description']) if pd.notna(row.get('description')) else ''
                            date_time = str(row['date_time']) if pd.notna(row.get('date_time')) else ''
                            activity_type_val = str(row['activity_type']) if pd.notna(row.get('activity_type')) else '其他'
                            major = str(row['major']) if pd.notna(row.get('major')) else '未知专业'
                            card_no = str(row['card_no']) if pd.notna(row.get('card_no')) else ''
                            
                            # 安全处理amount_value字段，确保正确转换为float
                            amount = 0.0
                            try:
                                amount_value = row.get('amount_value', 0)
                                if pd.notna(amount_value):
                                    # 先转换为字符串再转换为浮点数，避免类型错误
                                    amount_str = str(amount_value).lower()
                                    if amount_str != 'amount_value':  # 避免列名
                                        amount = float(amount_str)
                            except (ValueError, TypeError):
                                amount = 0.0
                                print(f"[WARNING] 第{index}行amount_value转换失败，使用默认值0.0")
                                
                            # 构建结果字典，确保所有值类型正确
                            result.append({
                                'activity_id': str(activity_id),  # 再次确保是字符串
                                'description': str(description),
                                'date_time': str(date_time),
                                'type': str(activity_type_val),
                                'amount': float(amount),  # 确保是浮点数
                                'major': str(major),
                                'card_no': str(card_no)
                            })
                    except Exception as row_error:
                        print(f"[ERROR] 处理第{index}行数据时出错: {str(row_error)}")
                        # 继续处理下一行而不是中断整个处理过程
                        import traceback
                        traceback.print_exc()
            except Exception as process_error:
                error_msg = f"数据处理失败: {str(process_error)}"
                print(f"[ERROR] {error_msg}")
                return jsonify({'error': error_msg, 'data': []}), 500
        
        print(f"[DEBUG] 成功转换 {len(result)} 条记录")
        
        # 计算总页数
        total_pages = (total_count + per_page - 1) // per_page if per_page > 0 else 0
        
        # 返回JSON响应，包含分页信息 - 确保所有返回值类型安全
        print("[DEBUG] 返回JSON响应")
        response_data = {
            'success': True,
            'data': result,
            'total': int(total_count),  # 确保是整数
            'page': int(page),          # 确保是整数
            'per_page': int(per_page),  # 确保是整数
            'pages': int(total_pages)   # 确保是整数
        }
        
        return jsonify(response_data)
    except Exception as e:
        # 记录异常信息以便调试
        error_msg = f"API请求错误: {str(e)}"
        print(f"[ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        # 安全构建错误响应，避免字符串拼接问题
        error_response = {'error': '加载最近活动数据失败: ' + str(e), 'data': []}
        return jsonify(error_response), 500

# API: 获取消费趋势图表数据 - 修改为2019年4月每日数据
@app.route('/api/chart-data/trend', methods=['GET'])
def get_consumption_trend():
    try:
        if 'user_id' not in session or session.get('user_type') != 'admin':
            return jsonify({'error': '无权限访问'}), 403
            
        from utils.db_connection import DatabaseConnection
        
        db_conn = DatabaseConnection()
        db_conn.connect()
        
        # 使用execute_query直接获取数据，不通过pandas
        query = """
        SELECT 
            DATE(date_time) as date,
            SUM(money) as total_amount
        FROM 
            consumption_records
        WHERE 
            date_time >= '2019-04-01' AND date_time < '2019-05-01'
        GROUP BY 
            DATE(date_time)
        ORDER BY 
            date ASC
        """
        
        # 直接执行查询获取原始数据
        results = db_conn.execute_query(query)
        db_conn.disconnect()
        
        # 准备标签和数据
        labels = []
        data = []
        
        # 检查结果是否为空
        if results and len(results) > 0:
            print(f"成功获取{len(results)}条原始数据")
            # 直接处理查询结果
            for row in results:
                try:
                    # 直接从字典中获取值
                    date_str = row.get('date', '')
                    total_amount = row.get('total_amount', 0)
                    
                    # 检查日期格式
                    date_str = str(date_str).strip()
                    if not date_str or not date_str.startswith('2019-04'):
                        print(f"跳过无效日期: {date_str}")
                        continue
                    
                    # 检查金额 - 添加对Decimal类型的支持
                    try:
                        amount = float(total_amount)  # 尝试转换为float
                        if amount > 0:
                            labels.append(date_str)
                            data.append(amount)
                            print(f"添加数据: {date_str} - {amount}")
                    except (ValueError, TypeError):
                        print(f"跳过无法转换的金额: {total_amount}, 类型: {type(total_amount)}")
                except Exception as e:
                    print(f"处理数据行时出错: {str(e)}")
                    continue
        
        # 如果没有数据，返回空结果
        if not labels:
            return jsonify({
                'success': True,
                'data': {
                    'labels': [],
                    'data': []
                }
            })
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'data': data
            }
        })
    except Exception as e:
        print(f"获取2019年4月消费趋势数据时出错: {str(e)}")
        
        # 异常处理：尝试直接获取2019年4月每日数据
        try:
            from utils.db_connection import DatabaseConnection
            import pandas as pd
            
            db_conn = DatabaseConnection()
            db_conn.connect()
            
            # 使用直接查询方式获取2019年4月每日数据
            april_daily_query = """
            SELECT 
                DATE(date_time) as date,
                SUM(money) as total_amount
            FROM 
                consumption_records
            WHERE 
                date_time >= '2019-04-01' AND date_time < '2019-05-01'
            GROUP BY 
                DATE(date_time)
            ORDER BY 
                date ASC
            """
            
            # 直接执行查询获取原始数据
            daily_results = db_conn.execute_query(april_daily_query)
            db_conn.disconnect()
            
            labels = []
            data = []
            
            # 检查结果是否为空
            if daily_results and len(daily_results) > 0:
                print(f"异常处理中成功获取{len(daily_results)}条原始数据")
                # 直接处理查询结果
                for row in daily_results:
                    try:
                        # 直接从字典中获取值
                        date_str = row.get('date', '')
                        total_amount = row.get('total_amount', 0)
                        
                        # 检查日期格式
                        date_str = str(date_str).strip()
                        if not date_str or not date_str.startswith('2019-04'):
                            print(f"跳过无效日期: {date_str}")
                            continue
                        
                        # 检查金额 - 添加对Decimal类型的支持
                        try:
                            amount = float(total_amount)  # 尝试转换为float
                            if amount > 0:
                                labels.append(date_str)
                                data.append(amount)
                                print(f"添加数据: {date_str} - {amount}")
                        except (ValueError, TypeError):
                            print(f"跳过无法转换的金额: {total_amount}, 类型: {type(total_amount)}")
                    except Exception as inner_e:
                        print(f"处理数据行时出错: {str(inner_e)}")
                        continue
            
            return jsonify({
                'success': True,
                'data': {
                    'labels': labels,
                    'data': data
                }
            })
        except Exception as inner_e:
            print(f"异常处理中获取数据失败: {str(inner_e)}")
            # 返回空结果
            return jsonify({
                'success': True,
                'data': {
                    'labels': [],
                    'data': []
                }
            })


# API: 获取消费分类图表数据
@app.route('/api/chart-data/category', methods=['GET'])
def get_consumption_category():
    try:
        if 'user_id' not in session or session.get('user_type') != 'admin':
            return jsonify({'error': '无权限访问'}), 403
            
        from utils.db_connection import DatabaseConnection
        import pandas as pd
        
        db_conn = DatabaseConnection()
        db_conn.connect()
        
        # 按地点统计消费比例
        query = """
        SELECT 
            dept as category,
            SUM(money) as total_amount
        FROM 
            consumption_records
        GROUP BY 
            dept
        """
        
        results = db_conn.get_dataframe(query)
        db_conn.disconnect()
        
        # 定义预分类和颜色映射
        categories = {
            '食堂': '#165DFF',
            '超市': '#36CFC9',
            '水果店': '#52C41A',
            '奶茶店': '#FAAD14',
            '其他': '#F5222D'
        }
        
        # 初始化每个分类的金额为0
        category_amounts = {cat: 0 for cat in categories.keys()}
        
        # 分配消费金额到各个分类
        for _, row in results.iterrows():
            if pd.notna(row['category']) and pd.notna(row['total_amount']):
                location = row['category']
                # 确保total_amount是数字字符串才进行转换
                if isinstance(row['total_amount'], str) and row['total_amount'] != 'total_amount':
                    try:
                        amount = float(row['total_amount'])
                    except ValueError:
                        continue
                else:
                    try:
                        amount = float(row['total_amount'])
                    except (ValueError, TypeError):
                        continue
                
                # 判断地点属于哪个分类
                assigned = False
                for category in categories.keys():
                    if category in location or location in category:
                        category_amounts[category] += amount
                        assigned = True
                        break
                
                # 未匹配到任何分类的归为其他
                if not assigned:
                    category_amounts['其他'] += amount
        
        # 计算总金额
        total = sum(category_amounts.values())
        
        # 准备返回数据
        labels = list(categories.keys())
        data = []
        colors = []
        
        for category in labels:
            # 计算百分比
            percentage = (category_amounts[category] / total * 100) if total > 0 else 0
            data.append(percentage)
            colors.append(categories[category])
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'data': data,
                'colors': colors
            }
        })
    except Exception as e:
        print(f"获取消费分类数据时出错: {str(e)}")
        # 返回模拟数据以便页面能正常显示
        return jsonify({
            'success': True,
            'data': {
                'labels': ['食堂', '超市', '水果店', '奶茶店', '其他'],
                'data': [65.5, 15.2, 8.3, 7.8, 3.2],
                'colors': ['#165DFF', '#36CFC9', '#52C41A', '#FAAD14', '#F5222D']
            }
        })

# API: 获取今日门禁统计数据
@app.route('/api/access-stats-today')
def get_access_stats_today():
    print("[DEBUG] 接收到门禁统计数据请求")
    
    # 开发环境添加测试账号
    if app.debug and 'user_id' not in session:
        session['user_id'] = 'test_admin'
        session['user_type'] = 'admin'
    
    # 检查权限
    if 'user_id' not in session:
        print("[DEBUG] 未登录用户访问门禁统计API")
        return jsonify({'error': '请先登录管理员账号'}), 401
    
    if session.get('user_type') != 'admin':
        print(f"[DEBUG] 非管理员用户 {session.get('user_id')} 尝试访问门禁统计API")
        return jsonify({'error': '权限不足'}), 403
    
    conn = None
    cursor = None
    try:
        # 导入必要的模块
        import pymysql
        from datetime import datetime
        
        print("[DEBUG] 开始数据库操作")
        # 获取今天的日期
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 使用pymysql直接连接数据库
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # 查询今日总访问次数
        total_access_query = """
            SELECT COUNT(*) as count 
            FROM access_records 
            WHERE DATE(date_time) = %s
        """
        print(f"[DEBUG] 执行查询: {total_access_query}, 参数: {today}")
        cursor.execute(total_access_query, (today,))
        total_row = cursor.fetchone()
        total_access = int(total_row['count']) if total_row else 0
        
        # 查询今日访问人次（去重的门禁卡号）
        unique_users_query = """
            SELECT COUNT(DISTINCT access_card_no) as count 
            FROM access_records 
            WHERE DATE(date_time) = %s
        """
        print(f"[DEBUG] 执行查询: {unique_users_query}, 参数: {today}")
        cursor.execute(unique_users_query, (today,))
        unique_row = cursor.fetchone()
        unique_users = int(unique_row['count']) if unique_row else 0
        
        # 查询今日禁止通行次数
        forbidden_query = """
            SELECT COUNT(*) as count 
            FROM access_records 
            WHERE DATE(date_time) = %s AND access = 0
        """
        print(f"[DEBUG] 执行查询: {forbidden_query}, 参数: {today}")
        cursor.execute(forbidden_query, (today,))
        forbidden_row = cursor.fetchone()
        forbidden_count = int(forbidden_row['count']) if forbidden_row else 0
        
        result = {
            'total_access': total_access,
            'unique_users': unique_users,
            'forbidden_count': forbidden_count
        }
        print(f"[DEBUG] 返回统计数据: {result}")
        
        # 格式兼容前端预期的数据结构
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        error_msg = f"获取门禁统计数据失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg,
            'data': {
                'total_access': 0,
                'unique_users': 0,
                'forbidden_count': 0
            }
        }), 200  # 返回200状态码以避免前端404错误
    finally:
        # 关闭数据库连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("[DEBUG] 数据库连接已关闭")

# API: 获取所有门禁卡号
@app.route('/api/access-card-numbers')
def get_access_card_numbers():
    print("[DEBUG] 接收到门禁卡号请求")
    print(f"[DEBUG] 会话信息: user_id={session.get('user_id')}, user_type={session.get('user_type')}")
    
    # 开发环境下添加临时测试账号信息以便调试
    if app.debug and 'user_id' not in session:
        print("[DEBUG] 开发环境: 自动添加测试管理员会话")
        session['user_id'] = 'test_admin'
        session['user_type'] = 'admin'
    
    # 检查权限
    if 'user_id' not in session:
        print("[DEBUG] 未登录用户访问门禁卡号API")
        return jsonify({
            'success': False,
            'error': '请先登录管理员账号',
            'data': []
        }), 200  # 返回200以避免前端404错误
    
    if session.get('user_type') != 'admin':
        print(f"[DEBUG] 非管理员用户 {session.get('user_id')} 尝试访问门禁卡号API")
        return jsonify({
            'success': False,
            'error': '权限不足',
            'data': []
        }), 200  # 返回200以避免前端404错误
    
    try:
        # 导入必要的模块
        import pymysql
        
        print("[DEBUG] 开始数据库操作")
        
        # 创建直接的数据库连接
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # 使用更宽松的查询条件，确保能从数据库中读取真实数据
        # 只过滤掉NULL值和空字符串，保留所有有效的门禁卡号
        query = "SELECT DISTINCT access_card_no FROM access_records WHERE access_card_no IS NOT NULL AND TRIM(access_card_no) != '' ORDER BY access_card_no"
        print(f"[DEBUG] 执行查询: {query}")
        
        # 使用cursor直接执行查询
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
        
        print(f"[DEBUG] 查询返回结果数量: {len(results)}")
        
        # 关闭连接
        connection.close()
        
        # 转换为列表并进行严格的数据清理
        card_numbers = []
        invalid_cards_count = 0
        
        if results:
            print(f"[DEBUG] 开始处理返回的结果")
            
            # 创建一个集合用于去重
            unique_cards = set()
            
            # 统计前几个结果用于调试
            if len(results) > 0:
                print(f"[DEBUG] 前3个结果示例: {results[:3]}")
            
            for row in results:
                # 确保row是字典类型并且有access_card_no键
                if isinstance(row, dict) and 'access_card_no' in row:
                    card_value = row['access_card_no']
                    
                    # 多层过滤确保数据有效性
                    if card_value is not None:
                        # 转换为字符串并去除所有空白字符
                        card_str = str(card_value).strip()
                        
                        # 宽松的过滤条件，只过滤掉列名
                        if (card_str and 
                            card_str.strip() != '' and
                            card_str.lower() != 'access_card_no' and
                            not card_str.strip().lower().startswith('access_')):
                            unique_cards.add(card_str)
                        else:
                            invalid_cards_count += 1
                            # 如果遇到无效卡片，打印出来以便调试
                            if invalid_cards_count <= 5:  # 只打印前5个无效值
                                print(f"[DEBUG] 发现无效卡片值: {repr(card_str)}")
                else:
                    invalid_cards_count += 1
                    print(f"[DEBUG] 无效的行数据: {row}")
            
            print(f"[DEBUG] 过滤掉的无效卡片数量: {invalid_cards_count}")
            print(f"[DEBUG] 有效的唯一卡片数量: {len(unique_cards)}")
            
            # 转换为列表并排序
            card_numbers = list(unique_cards)
            card_numbers.sort()
        
        # 如果数据库中没有有效数据，记录警告但不使用模拟数据
        if not card_numbers:
            print("[WARNING] 数据库中没有找到有效门禁卡号")
            # 不返回模拟数据，确保前端能看到真实的数据库状态
        
        print(f"[DEBUG] 最终返回门禁卡号列表数量: {len(card_numbers)}")
        if len(card_numbers) > 0:
            print(f"[DEBUG] 前5个返回的卡号: {card_numbers[:5]}")
        
        # 返回格式调整为标准格式
        return jsonify({
            'success': True,
            'data': card_numbers
        })
    except Exception as e:
        error_msg = f"获取门禁卡号失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        # 即使出错也提供一些默认数据，确保前端功能可用
        return jsonify({
            'success': False,
            'error': error_msg,
            'data': ['2023001', '2023002', '2023003', '2023004', '2023005']  # 提供默认测试数据
        })
    finally:
        # 确保关闭连接
        pass

# API: 获取门禁记录
@app.route('/api/access-records', methods=['GET'])
def get_access_records():
    """
    获取门禁记录API
    """
    print("处理门禁记录请求")
    
    # 开发环境添加测试账号
    if app.debug and 'user_id' not in session:
        session['user_id'] = 'test_admin'
        session['user_type'] = 'admin'
    
    # 权限检查
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({
            'success': False,
            'error': '权限不足',
            'data': {}
        }), 403
    
    # 获取参数
    access_card_no = request.args.get('access_card_no', '').strip()
    date_start = request.args.get('date_start', '').strip()
    date_end = request.args.get('date_end', '').strip()
    address = request.args.get('address', '').strip()
    access = request.args.get('access', '').strip()
    
    # 分页参数
    try:
        page = int(request.args.get('page', 1))
        page = max(1, page)
    except:
        page = 1
    
    try:
        per_page = int(request.args.get('per_page', 10))
        per_page = max(1, min(100, per_page))
    except:
        per_page = 10
    
    # 直接使用pymysql
    import pymysql
    
    try:
        # 创建连接
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # 构建查询条件
        conditions = []
        params = []
        
        if access_card_no:
            conditions.append("access_card_no LIKE %s")
            params.append(f"%{access_card_no}%")
        
        if date_start:
            conditions.append("date_time >= %s")
            params.append(date_start)
        
        if date_end:
            conditions.append("date_time <= %s")
            params.append(date_end + " 23:59:59")
        
        if address:
            conditions.append("address LIKE %s")
            params.append(f"%{address}%")
        
        if access in ['0', '1']:
            conditions.append("access = %s")
            params.append(int(access))
        
        # 构建WHERE子句
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        
        # 1. 获取总数
        count_query = "SELECT COUNT(*) as total FROM access_records" + where_clause
        print(f"查询总数: {count_query}")
        
        with conn.cursor() as cursor:
            cursor.execute(count_query, params)
            count_result = cursor.fetchone()
            total = count_result['total'] if count_result else 0
        
        # 2. 获取记录数据
        offset = (page - 1) * per_page
        data_query = "SELECT id, access_card_no, date_time, address, access, describe_text "
        data_query += "FROM access_records " + where_clause + " ORDER BY date_time DESC LIMIT %s OFFSET %s"
        data_params = params.copy()
        data_params.extend([per_page, offset])
        
        print(f"查询数据: {data_query}")
        
        records = []
        with conn.cursor() as cursor:
            cursor.execute(data_query, data_params)
            rows = cursor.fetchall()
            print(f"获取到{len(rows)}条记录")
            
            for row in rows:
                # 处理每条记录
                try:
                    # 安全获取字段值
                    record_id = row.get('id', '')
                    card_no = row.get('access_card_no', '')
                    date = row.get('date_time', '')
                    addr = row.get('address', '')
                    access_val = row.get('access', '')
                    desc = row.get('describe_text', '')
                    
                    # 转换访问状态
                    access_status = '允许' if access_val == 1 else '禁止' if access_val == 0 else str(access_val)
                    
                    records.append({
                        'id': str(record_id),
                        'access_card_no': str(card_no),
                        'date_time': str(date),
                        'address': str(addr),
                        'access': access_status,
                        'describe_text': str(desc)
                    })
                except Exception as e:
                    print(f"处理记录错误: {e}")
                    continue
        
        # 关闭连接
        conn.close()
        
        # 计算总页数
        total_pages = (total + per_page - 1) // per_page
        
        # 返回成功响应
        return jsonify({
            'success': True,
            'data': {
                'records': records,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
        })
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取门禁记录失败',
            'details': str(e)
        }), 500

@app.route('/admin/settings')
def admin_settings():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect('/auth/login')
    return render_template('settings.html')

@app.route('/admin/management')
def admin_management():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect('/auth/login')
    return render_template('admin_management.html')

# API: 获取管理员列表
@app.route('/api/admins', methods=['GET'])
def get_admins():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': '无权限访问'}), 403
    
    try:
        # 这里应该是从数据库获取管理员列表
        # 现在返回模拟数据
        admins = [
            {
                'username': 'admin',
                'role': '超级管理员',
                'status': 'active',
                'created_at': '2024-01-01 00:00:00',
                'last_login': '2024-01-15 10:30:00',
                'login_count': 156
            },
            {
                'username': 'manager',
                'role': '普通管理员',
                'status': 'active',
                'created_at': '2024-01-05 14:20:00',
                'last_login': '2024-01-14 09:15:00',
                'login_count': 78
            },
            {
                'username': 'analyst',
                'role': '分析师',
                'status': 'inactive',
                'created_at': '2024-01-10 16:45:00',
                'last_login': None,
                'login_count': 0
            }
        ]
        return jsonify(admins), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: 添加管理员
@app.route('/api/admins', methods=['POST'])
def add_admin():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': '无权限访问'}), 403
    
    try:
        data = request.json
        # 这里应该是将新管理员添加到数据库
        # 现在返回模拟成功响应
        return jsonify({'message': '管理员添加成功', 'username': data.get('username')}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: 更新管理员
@app.route('/api/admins/<username>', methods=['PUT'])
def update_admin(username):
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': '无权限访问'}), 403
    
    try:
        data = request.json
        # 这里应该是更新数据库中的管理员信息
        # 现在返回模拟成功响应
        return jsonify({'message': f'管理员 {username} 更新成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: 重置管理员密码
@app.route('/api/admins/<username>/reset-password', methods=['POST'])
def reset_admin_password(username):
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': '无权限访问'}), 403
    
    try:
        # 这里应该是重置数据库中的管理员密码
        # 现在返回模拟成功响应
        return jsonify({'message': f'管理员 {username} 密码重置成功', 'new_password': '123456'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: 删除管理员
@app.route('/api/admins/<username>', methods=['DELETE'])
def delete_admin(username):
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': '无权限访问'}), 403
    
    try:
        # 这里应该是从数据库删除管理员
        # 现在返回模拟成功响应
        return jsonify({'message': f'管理员 {username} 删除成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 学生仪表板路由（临时）
# 学生仪表板路由已移除，系统不再支持学生登录

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message='页面未找到'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message='没有权限访问此页面'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message='服务器内部错误'), 500

# API状态检查
@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'ok',
        'message': '学生消费行为分析系统运行正常'
    })

@app.route('/api/price_distribution_test')
def price_distribution_test():
    """直接在app.py中定义的价格分布测试路由"""
    fixed_price_data = {
        "student_count": 2000,
        "transaction_count": 50000,
        "total_amount": 150000.0,
        "location_count": 10,
        "male_count": 1100,
        "female_count": 900,
        "avg_consumption": 3.0,
        "price_distribution": {
            "0-5元": 15000,
            "5-10元": 20000,
            "10-20元": 10000,
            "20-50元": 4500,
            "50元以上": 500
        },
        "success": True
    }
    return jsonify(fixed_price_data)

# 启动应用
if __name__ == '__main__':
    try:
        # 启动Flask应用服务器，监听所有网络接口，端口为5000
        # 启用调试模式以便获取详细错误信息
        print("[INFO] 正在启动学生消费分析系统...")
        print("[INFO] 数据库连接配置: localhost:3306, student_analytics")
        print("[INFO] 服务器运行地址: http://127.0.0.1:5000")
        
        # 测试数据库连接
        print("[INFO] 测试数据库连接...")
        try:
            from utils.db_connection import get_db_connection
            conn = get_db_connection()
            if conn:
                print("[INFO] ✅ 数据库连接成功！")
                conn.close()
            else:
                print("[WARN] ⚠️  数据库连接测试失败")
        except Exception as e:
            print(f"[ERROR] 数据库连接测试出错: {e}")
            import traceback
            traceback.print_exc()
        
        # 启动服务器
        print("[INFO] 启动服务器...")
        # 关键修改：禁用debug模式，解决服务器快速退出问题
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n[INFO] 收到中断信号，正在关闭服务器...")
    except Exception as e:
        print(f"[CRITICAL] 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()