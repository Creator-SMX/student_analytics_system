from flask import Flask, jsonify, request
import pymysql
from datetime import datetime

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'student_analytics',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 获取数据库连接
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# 关闭数据库连接
def close_db_connection(conn):
    conn.close()

# 模拟数据（仅用于开发测试）
mock_access_records = [
    {'id': 1, 'access_card_no': '12345678', 'datetime': '2019-04-01 00:00:00', 'address': '第六教学楼前门', 'access': 1, 'describe': '允许通过'},
    {'id': 2, 'access_card_no': '85881343', 'datetime': '2019-04-01 00:00:20', 'address': '第六教学楼前门', 'access': 1, 'describe': '允许通过'},
    {'id': 3, 'access_card_no': '11647252', 'datetime': '2019-04-01 00:00:00', 'address': '飞凤轩前门', 'access': 1, 'describe': '允许通过'},
    {'id': 4, 'access_card_no': '24172155', 'datetime': '2019-04-01 00:00:30', 'address': '第六教学楼前门', 'access': 1, 'describe': '允许通过'},
    {'id': 5, 'access_card_no': '18629382', 'datetime': '2019-04-01 00:00:40', 'address': '飞凤轩前门', 'access': 1, 'describe': '允许通过'},
    {'id': 6, 'access_card_no': '72232967', 'datetime': '2019-04-01 00:01:00', 'address': '飞凤轩前门', 'access': 1, 'describe': '允许通过'},
    {'id': 7, 'access_card_no': '80119856', 'datetime': '2019-04-01 00:01:50', 'address': '第六教学楼前门', 'access': 1, 'describe': '允许通过'},
    {'id': 8, 'access_card_no': '22239650', 'datetime': '2019-04-01 00:02:00', 'address': '第六教学楼前门', 'access': 1, 'describe': '允许通过'},
    {'id': 9, 'access_card_no': '24124188', 'datetime': '2019-04-01 00:01:30', 'address': '飞凤轩前门', 'access': 1, 'describe': '允许通过'},
    {'id': 10, 'access_card_no': '84241421', 'datetime': '2019-04-01 00:00:30', 'address': '第六教学楼前门', 'access': 1, 'describe': '允许通过'},
    {'id': 11, 'access_card_no': '96611912', 'datetime': '2019-04-01 00:18:30', 'address': '第六教学楼前门', 'access': 0, 'describe': '禁止通过-没有权限'},
    {'id': 12, 'access_card_no': '137899', 'datetime': '2019-04-01 00:02:00', 'address': '飞凤轩前门', 'access': 1, 'describe': '允许通过'},
    {'id': 13, 'access_card_no': '25412531', 'datetime': '2019-04-01 00:39:30', 'address': '飞凤轩前门', 'access': 1, 'describe': '允许通过'},
    {'id': 14, 'access_card_no': '6310108', 'datetime': '2019-04-01 00:45:00', 'address': '青鸾苑前门', 'access': 1, 'describe': '允许通过'},
    {'id': 15, 'access_card_no': '7423035', 'datetime': '2019-04-01 00:47:00', 'address': '第六教学楼前门', 'access': 1, 'describe': '允许通过'},
    {'id': 16, 'access_card_no': '6310108', 'datetime': '2019-04-01 00:45:30', 'address': '青鸾苑前门', 'access': 0, 'describe': '禁止通过-没有权限'},
    {'id': 17, 'access_card_no': '7423035', 'datetime': '2019-04-01 00:47:10', 'address': '第六教学楼前门', 'access': 0, 'describe': '禁止通过-没有权限'},
    {'id': 18, 'access_card_no': '7423035', 'datetime': '2019-04-01 00:47:20', 'address': '第六教学楼前门', 'access': 0, 'describe': '禁止通过-没有权限'},
    {'id': 19, 'access_card_no': '20311483', 'datetime': '2019-04-01 00:47:30', 'address': '第六教学楼前门', 'access': 0, 'describe': '禁止通过-没有权限'},
    {'id': 20, 'access_card_no': '20311483', 'datetime': '2019-04-01 00:47:40', 'address': '第六教学楼前门', 'access': 0, 'describe': '禁止通过-没有权限'}
]

# 首页
@app.route('/')
def index():
    return "门禁记录测试服务器正在运行！"

# 获取门禁记录
@app.route('/api/access-records')
def get_access_records():
    conn = None
    cursor = None
    try:
        # 获取请求参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        card_no = request.args.get('card_no')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        address = request.args.get('address')
        
        # 计算偏移量
        offset = (page - 1) * per_page
        
        # 建立数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建基础查询
        base_query = "SELECT * FROM access_records"
        count_query = "SELECT COUNT(*) as total FROM access_records"
        
        # 构建筛选条件
        conditions = []
        params = []
        
        if card_no:
            conditions.append("access_card_no LIKE %s")
            params.append(f"%{card_no}%")
        
        if start_date:
            conditions.append("DATE(date_time) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(date_time) <= %s")
            params.append(end_date)
        
        if address:
            conditions.append("address LIKE %s")
            params.append(f"%{address}%")
        
        # 应用筛选条件
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            base_query += where_clause
            count_query += where_clause
        
        # 添加排序
        base_query += " ORDER BY date_time DESC"
        
        # 添加分页
        base_query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        # 执行查询获取总数
        cursor.execute(count_query, params[:len(params)-2])
        total = cursor.fetchone()['total']
        
        # 执行查询获取数据
        cursor.execute(base_query, params)
        records = cursor.fetchall()
        
        # 计算总页数
        total_pages = (total + per_page - 1) // per_page
        
        # 返回结果
        return jsonify({
            'data': records,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages
            }
        })
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            close_db_connection(conn)

# 获取今日门禁统计
@app.route('/api/access-stats-today')
def get_access_stats_today():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 查询允许通过的次数
        query_allowed = """SELECT COUNT(*) as count 
                          FROM access_records 
                          WHERE DATE(date_time) = %s AND access = 1"""
        cursor.execute(query_allowed, (today,))
        allowed_row = cursor.fetchone()
        allowed_count = allowed_row['count'] if allowed_row else 0
        
        # 查询禁止通过的次数
        query_denied = """SELECT COUNT(*) as count 
                          FROM access_records 
                          WHERE DATE(date_time) = %s AND access = 0"""
        cursor.execute(query_denied, (today,))
        denied_row = cursor.fetchone()
        denied_count = denied_row['count'] if denied_row else 0
        
        # 计算总数
        total_count = allowed_count + denied_count
        
        # 计算百分比
        allowed_rate = round(allowed_count / total_count * 100, 2) if total_count > 0 else 0
        denied_rate = round(denied_count / total_count * 100, 2) if total_count > 0 else 0

        return jsonify({
            'allowed_count': allowed_count,
            'denied_count': denied_count,
            'allowed_rate': allowed_rate,
            'denied_rate': denied_rate
        })
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            close_db_connection(conn)

# 获取门禁卡号列表
@app.route('/api/access-card-numbers')
def get_access_card_numbers():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询所有唯一的门禁卡号
        query = "SELECT DISTINCT access_card_no FROM access_records ORDER BY access_card_no"
        cursor.execute(query)
        
        # 获取所有结果
        results = cursor.fetchall()
        
        # 提取卡号列表
        card_numbers = [result['access_card_no'] for result in results]
        
        # 返回结果
        return jsonify(card_numbers)
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            close_db_connection(conn)

if __name__ == '__main__':
    print("📊 启动门禁记录测试服务器...")
    print("🌐 访问: http://127.0.0.1:5000/")
    print("🔍 API文档:")
    print("- GET /api/access-records - 获取门禁记录")
    print("- GET /api/access-stats-today - 获取统计数据")
    print("- GET /api/access-card-numbers - 获取所有卡号")
    print("🚀 服务正在启动，按Ctrl+C停止")
    app.run(debug=True, host='0.0.0.0', port=5000)