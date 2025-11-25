#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
学生消费分析系统监控程序
此脚本会持续监控应用程序进程，并在它退出时自动重启，确保服务持续可用
"""

import os
import sys
import subprocess
import time
import logging
import signal
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app_monitor.log")
    ]
)
logger = logging.getLogger('app_monitor')

def get_timestamp():
    """获取当前时间戳"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def signal_handler(sig, frame):
    """处理终止信号"""
    logger.info(f"收到信号 {sig}，正在停止监控进程...")
    sys.exit(0)

def main():
    # 注册信号处理
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("===== 学生消费分析系统监控程序启动 =====")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"当前工作目录: {os.getcwd()}")
    
    # 确认app.py存在
    if not os.path.exists('app.py'):
        logger.critical("错误: 找不到app.py文件！")
        sys.exit(1)
    
    restart_count = 0
    
    try:
        while True:
            restart_count += 1
            logger.info(f"[{restart_count}] 启动应用程序...")
            
            # 使用subprocess启动应用程序
            # 设置shell=False以避免额外的命令解释器
            process = subprocess.Popen(
                [sys.executable, 'app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # 实时输出应用程序的日志
            logger.info(f"应用程序已启动 (PID: {process.pid})")
            
            # 读取并记录应用程序的输出
            for line in process.stdout:
                line = line.strip()
                if line:
                    logger.info(f"[APP] {line}")
            
            # 等待进程结束并获取退出代码
            process.wait()
            exit_code = process.returncode
            
            if exit_code == 0:
                logger.warning(f"应用程序正常退出 (退出代码: {exit_code})")
            else:
                logger.error(f"应用程序异常退出 (退出代码: {exit_code})")
            
            # 等待一段时间后重启
            restart_delay = 2
            logger.info(f"{restart_delay}秒后自动重启应用程序...")
            time.sleep(restart_delay)
            
            logger.info("=" * 50)
    
    except KeyboardInterrupt:
        logger.info("用户中断，正在停止监控进程...")
    except Exception as e:
        logger.critical(f"监控进程出错: {e}", exc_info=True)
    finally:
        logger.info("===== 监控进程已停止 =====")

if __name__ == '__main__':
    main()