from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)  # 启用CORS，允许所有跨域请求

# 测试门禁记录数据
mock_access_records = [
    {'id': 1, 'access_card_no': '12345678', 'datetime': '2019-04-01 00:00:00', 'address': '第六教学楼前门', 'access': 1, 'describe': '允许通过'},
    {'id': 2, 'access_card_no': '85881343', 'datetime': '2019-04-01 00:00:20', 'address': '第六教学楼前门', 'access': 1, 'describe': '允许通过'},
    {'id': 3, 'access_card_no': '11647252', 'datetime': '2019-04-01 00:00:00', 'address': '飞凤轩前门', 'access': 1, 'describe': '允许通过'}
]

@app.route('/')
def index():
    return "简单门禁记录测试服务器"

@app.route('/api/simple-records')
def get_simple_records():
    try:
        return jsonify({
            'data': mock_access_records,
            'meta': {'page': 1, 'per_page': 10, 'total': len(mock_access_records), 'total_pages': 1}
        })
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simple-card-numbers')
def get_simple_card_numbers():
    try:
        # 提取所有唯一的卡号
        card_numbers = list(set(record['access_card_no'] for record in mock_access_records))
        return jsonify(card_numbers)
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simple-stats')
def get_simple_stats():
    try:
        # 计算统计数据
        total_count = len(mock_access_records)
        allowed_count = sum(1 for record in mock_access_records if record['access'] == 1)
        denied_count = total_count - allowed_count
        
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

if __name__ == '__main__':
    print("启动简单测试服务器...")
    print("访问: http://127.0.0.1:5001/")
    print("API端点:")
    print("- GET /api/simple-records - 获取门禁记录")
    print("- GET /api/simple-card-numbers - 获取卡号列表")
    print("- GET /api/simple-stats - 获取统计数据")
    app.run(debug=True, port=5001)