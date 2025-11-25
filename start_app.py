#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
学生消费分析系统增强启动脚本
专为Windows环境优化，添加全面的错误处理和日志记录
"""

import os
import sys
import logging
import traceback
import time
import signal

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log")  # 同时输出到文件便于分析
    ]
)
logger = logging.getLogger('app_launcher')

# Windows信号处理
def signal_handler(sig, frame):
    logger.info(f"接收到信号 {sig}，正在安全关闭...")
    # 这里可以添加清理代码
    sys.exit(0)

# 注册信号处理（Windows支持有限）
if hasattr(signal, 'SIGINT'):
    signal.signal(signal.SIGINT, signal_handler)

# 禁用Windows错误报告对话框
if os.name == 'nt':  # Windows系统
    try:
        import ctypes
        # 设置Windows错误模式为不显示对话框
        SEM_NOGPFAULTERRORBOX = 0x0002
        ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
        logger.info("已禁用Windows错误报告对话框")
    except Exception as e:
        logger.warning(f"无法禁用Windows错误报告: {e}")

def main():
    logger.info("======= 学生消费分析系统启动 =======")
    
    # 显示Python环境信息
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"当前工作目录: {os.getcwd()}")
    
    # 确认app.py存在
    if not os.path.exists('app.py'):
        logger.critical("错误: 找不到app.py文件！")
        sys.exit(1)
    
    # 导入应用的函数方式
    try:
        # 动态导入app模块
        logger.info("开始导入应用...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_module", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        sys.modules["app_module"] = app_module
        
        # 尝试执行模块导入（捕获其中可能的错误）
        try:
            spec.loader.exec_module(app_module)
            logger.info("应用模块导入成功")
            
            # 验证Flask应用实例
            if hasattr(app_module, 'app'):
                app = app_module.app
                logger.info("成功获取Flask应用实例")
                
                # 直接启动Flask应用（不使用debug模式）
                logger.info("准备启动Flask服务器...")
                logger.info("服务器地址: http://127.0.0.1:5001/")
                logger.info("按Ctrl+C停止服务器")
                
                # 添加运行前的钩子
                logger.info("初始化完成，启动服务器...")
                
                # 使用try-except捕获服务器运行时的所有错误
                try:
                    # 直接调用app.run，禁用debug和自动重载
                    app.run(
                        host='0.0.0.0',
                        port=5001,
                        debug=False,
                        use_reloader=False,
                        threaded=True
                    )
                except Exception as server_error:
                    logger.critical(f"服务器运行时错误: {server_error}")
                    logger.debug(traceback.format_exc())
                    
                    # 尝试优雅退出
                    logger.info("尝试优雅退出...")
                    time.sleep(2)
            else:
                logger.critical("错误: app.py中没有找到'app'实例")
                sys.exit(1)
                
        except Exception as import_error:
            logger.critical(f"应用导入错误: {import_error}")
            logger.debug(traceback.format_exc())
            
            # 尝试直接执行app.py作为脚本（备用方法）
            logger.info("尝试作为脚本直接执行app.py...")
            try:
                # 这里我们模拟直接执行，实际上会退出当前进程
                logger.info("请手动运行: python app.py")
                # 或者使用subprocess启动（但这可能会继承同样的问题）
            except Exception as exec_error:
                logger.critical(f"执行脚本错误: {exec_error}")
                logger.debug(traceback.format_exc())
                
    except Exception as e:
        logger.critical(f"启动过程中的致命错误: {e}")
        logger.debug(traceback.format_exc())
    finally:
        logger.info("======= 应用退出 =======")

if __name__ == '__main__':
    main()