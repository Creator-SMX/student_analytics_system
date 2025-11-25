#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""交互式应用程序调试脚本"""
import os
import sys
import traceback

print("=== 交互式应用程序调试 ===")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")

# 第1步：检查并导入必要的模块
print("\n=== 第1步：导入基础模块 ===")
try:
    import flask
    print(f"✅ Flask版本: {flask.__version__}")
except ImportError as e:
    print(f"❌ 导入Flask失败: {e}")

try:
    import pandas as pd
    print(f"✅ Pandas版本: {pd.__version__}")
except ImportError as e:
    print(f"❌ 导入Pandas失败: {e}")

try:
    import pymysql
    print(f"✅ PyMySQL版本: {pymysql.__version__}")
except ImportError as e:
    print(f"❌ 导入PyMySQL失败: {e}")

# 第2步：检查数据库连接
print("\n=== 第2步：检查数据库连接 ===")
try:
    from utils.db_connection import DatabaseConnection
    print("✅ 成功导入DatabaseConnection类")
    
    # 尝试创建数据库连接实例
    db = DatabaseConnection()
    print("✅ 成功创建数据库连接实例")
    
    # 尝试连接数据库（可选，取消注释以测试连接）
    # print("尝试连接数据库...")
    # connected = db.connect()
    # print(f"数据库连接: {'成功' if connected else '失败'}")
    # if connected:
    #     db.disconnect()
    
except Exception as e:
    print(f"❌ 数据库连接检查失败: {e}")
    traceback.print_exc()

# 第3步：检查应用程序模块
print("\n=== 第3步：检查应用程序模块 ===")
print("注意：这一步可能会启动应用程序")
print("按Ctrl+C可以随时中断执行")

# 尝试导入app模块的部分内容
print("\n正在尝试部分导入...")
try:
    # 先尝试单独导入Flask实例而不运行应用
    import importlib.util
    spec = importlib.util.spec_from_file_location("app_module", "app.py")
    app_module = importlib.util.module_from_spec(spec)
    
    # 定义一个模拟的__name__变量以避免直接运行应用
    app_module.__name__ = "__main__"
    
    print("正在加载app.py模块（不会执行）...")
    # 这行代码会执行app.py的全局代码，但不会运行app.run()
    try:
        spec.loader.exec_module(app_module)
        print("✅ 成功加载app.py模块")
        
        # 检查是否成功创建了Flask应用
        if hasattr(app_module, 'app'):
            print(f"✅ 发现Flask应用实例")
            print(f"应用名称: {app_module.app.name}")
        else:
            print("❌ 未找到Flask应用实例")
            
    except SystemExit:
        print("⚠️  应用程序尝试退出")
    except KeyboardInterrupt:
        print("⚠️  执行被用户中断")
    except Exception as e:
        print(f"❌ 加载app.py时出错: {e}")
        traceback.print_exc()
        
 except Exception as e:
    print(f"❌ 部分导入失败: {e}")
    traceback.print_exc()

print("\n=== 调试完成 ===")