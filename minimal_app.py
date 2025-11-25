#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
极简Flask应用 - 用于隔离服务器退出问题
"""

from flask import Flask, jsonify
import time

# 创建最简单的Flask应用
app = Flask(__name__)

# 添加一个简单的路由
@app.route('/')
def hello():
    return "Hello, World! 学生消费分析系统"

# 添加API状态检查路由
@app.route('/api/status')
def status():
    return jsonify({
        'status': 'ok',
        'timestamp': time.time()
    })

# 启动应用
if __name__ == '__main__':
    print("启动极简Flask应用...")
    print("运行地址: http://127.0.0.1:5003")
    # 使用最简单的配置
    app.run(host='0.0.0.0', port=5003, debug=False, threaded=False, use_reloader=False)