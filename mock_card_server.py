from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/access-card-numbers')
def get_access_card_numbers():
    # 提供模拟的门禁卡号数据
    mock_card_numbers = [
        '2023001', '2023002', '2023003', '2023004', '2023005',
        '2023006', '2023007', '2023008', '2023009', '2023010'
    ]
    
    print(f"[DEBUG] 返回模拟门禁卡号: {mock_card_numbers}")
    
    # 返回标准格式的响应
    return jsonify({
        'success': True,
        'data': mock_card_numbers
    })

if __name__ == '__main__':
    print("启动模拟门禁卡号服务器...")
    print("访问: http://127.0.0.1:5000/api/access-card-numbers")
    app.run(debug=True, host='0.0.0.0', port=5000)