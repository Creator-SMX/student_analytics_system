#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强版测试服务器 - 用于诊断Flask应用退出问题
"""

import sys
import os
import logging
from datetime import datetime

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'server_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('test_server')

try:
    # 添加项目目录到Python路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 导入必要的模块
    from flask import Flask, request, jsonify
    from utils.db_connection import get_db_connection, execute_query
    
    logger.info("初始化Flask应用...")
    app = Flask(__name__)
    app.config['DEBUG'] = True
    
    # 测试路由
    @app.route('/')
    def home():
        logger.info("收到首页请求")
        return "学生消费分析系统 - 测试服务器"
    
    @app.route('/status')
    def status():
        logger.info("收到状态检查请求")
        try:
            # 测试数据库连接
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            db_status = "正常"
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            db_status = f"错误: {str(e)}"
        
        return jsonify({
            "status": "运行中",
            "timestamp": datetime.now().isoformat(),
            "database": db_status
        })
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"捕获到异常: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
    # 使用更兼容的钩子方法
    @app.before_request
    def before_request():
        if not hasattr(app, 'has_processed_first_request'):
            logger.info("处理第一个请求前的初始化")
            app.has_processed_first_request = True
    
    @app.teardown_request
    def teardown_request(exception):
        if exception:
            logger.error(f"请求处理异常: {str(exception)}")
    
    logger.info("启动测试服务器...")
    logger.info(f"Python版本: {sys.version}")
    
    # 使用简化配置启动服务器
    try:
        app.run(
            host='0.0.0.0',
            port=5002,
            debug=False,  # 禁用调试模式可能解决某些问题
            threaded=True
        )
    except Exception as run_error:
        logger.critical(f"服务器运行时错误: {str(run_error)}", exc_info=True)
    
    logger.info("服务器正常退出")
    
except KeyboardInterrupt:
    logger.info("接收到键盘中断，正在关闭服务器...")
except Exception as e:
    logger.critical(f"服务器启动失败: {str(e)}", exc_info=True)
    print(f"严重错误: {str(e)}")
    sys.exit(1)