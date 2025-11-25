"""极简测试脚本：只测试基础导入和环境配置"""
import sys
import os

print("===== 开始极简测试 =====")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")

# 检查是否能导入基本模块
print("\n测试基础导入:")
try:
    import flask
    print("✓ Flask已安装")
except ImportError:
    print("✗ 缺少Flask模块")

try:
    import sqlalchemy
    print("✓ SQLAlchemy已安装")
except ImportError:
    print("✗ 缺少SQLAlchemy模块")

try:
    import pymysql
    print("✓ PyMySQL已安装")
except ImportError:
    print("✗ 缺少PyMySQL模块")

# 检查是否能导入项目模块
print("\n测试项目模块导入:")
try:
    # 添加项目根目录到Python路径
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from analytics.analytics_controller import db_conn
    print("✓ 成功导入analytics_controller")
except ImportError as e:
    print(f"✗ 导入analytics_controller失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n===== 测试完成 =====")