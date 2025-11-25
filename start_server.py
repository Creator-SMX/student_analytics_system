#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
替代启动脚本 - 使用Werkzeug开发服务器直接启动应用
"""

import sys
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('start_server')

def main():
    try:
        logger.info("开始启动学生消费分析系统...")
        
        # 添加项目目录到Python路径
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # 导入应用
        logger.info("导入Flask应用...")
        from app import app
        
        # 测试数据库连接
        logger.info("测试数据库连接...")
        try:
            from utils.db_connection import get_db_connection
            conn = get_db_connection()
            if conn:
                logger.info("✅ 数据库连接成功！")
                conn.close()
            else:
                logger.warning("⚠️  数据库连接测试失败")
        except Exception as e:
            logger.error(f"数据库连接测试出错: {e}")
        
        # 使用Werkzeug的开发服务器
        logger.info("使用Werkzeug开发服务器启动应用...")
        logger.info("服务器运行地址: http://127.0.0.1:5001")
        
        from werkzeug.serving import run_simple
        
        # 使用更稳定的配置启动服务器
        run_simple(
            hostname='0.0.0.0',
            port=5001,
            application=app,
            use_reloader=False,
            use_debugger=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.critical(f"服务器启动失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()