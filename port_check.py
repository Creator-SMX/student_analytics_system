#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""端口检查和应用启动脚本"""
import socket
import subprocess
import time

def check_port(port):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def main():
    """主函数"""
    port = 5000
    print(f"检查端口 {port} 是否被占用...")
    
    if check_port(port):
        print(f"❌ 端口 {port} 已被占用，请关闭占用该端口的进程后重试。")
    else:
        print(f"✅ 端口 {port} 可用。")
        print("尝试启动应用程序...")
        
        # 尝试使用不同的方式启动应用程序
        try:
            # 使用subprocess启动应用程序
            process = subprocess.Popen(
                ['python', 'app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待一段时间让应用程序启动
            time.sleep(3)
            
            # 检查进程是否还在运行
            if process.poll() is None:
                print("✅ 应用程序似乎已成功启动！")
                print("应用程序正在运行中，请访问 http://localhost:5000")
                # 不终止进程，让它继续运行
            else:
                print(f"❌ 应用程序启动失败，退出码: {process.returncode}")
                # 打印错误输出
                stdout, stderr = process.communicate()
                if stdout:
                    print("标准输出:", stdout)
                if stderr:
                    print("错误输出:", stderr)
        except Exception as e:
            print(f"启动过程中出错: {str(e)}")

if __name__ == "__main__":
    main()