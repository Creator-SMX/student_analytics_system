#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""环境检查脚本"""

print("=== 环境检查开始 ===")

# 检查Python版本
import sys
print(f"Python版本: {sys.version}")

# 检查pymysql模块是否安装
try:
    import pymysql
    print(f"✅ pymysql模块已安装，版本: {pymysql.__version__}")
except ImportError:
    print("❌ pymysql模块未安装")

# 检查是否有其他必要模块
try:
    import pandas
    print(f"✅ pandas模块已安装")
except ImportError:
    print("❌ pandas模块未安装")

print("\n=== 环境检查结束 ===")