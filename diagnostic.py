#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""环境诊断和应用启动脚本"""
import os
import sys
import subprocess
import traceback

print("=== 环境诊断开始 ===")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"Python路径: {sys.executable}")

# 检查必要的文件是否存在
required_files = ['app.py', 'utils/db_connection.py']
for file in required_files:
    if os.path.exists(file):
        print(f"✅ 文件存在: {file}")
    else:
        print(f"❌ 文件不存在: {file}")

# 尝试直接导入app模块
print("\n=== 尝试导入应用模块 ===")
try:
    # 添加当前目录到Python路径
    sys.path.append(os.getcwd())
    
    # 尝试导入app模块
    print("正在导入app模块...")
    from app import app as flask_app
    print("✅ 成功导入app模块")
    
    # 打印应用程序的基本信息
    print(f"应用程序名称: {flask_app.name}")
    print(f"调试模式: {flask_app.debug}")
    print(f"密钥设置: {'是' if flask_app.secret_key else '否'}")
    
    # 列出所有注册的路由
    print("\n=== 注册的路由 ===")
    for rule in flask_app.url_map.iter_rules():
        print(f"{rule}")
    
    print("\n=== 诊断完成 ===")
    print("准备启动应用程序...")
    
    # 启动应用程序
    if __name__ == "__main__":
        print("正在启动应用程序...")
        print("访问地址: http://localhost:5000")
        flask_app.run(host='0.0.0.0', port=5000, debug=True)
        
 except Exception as e:
    print(f"❌ 导入失败: {str(e)}")
    print("\n详细错误信息:")
    traceback.print_exc()