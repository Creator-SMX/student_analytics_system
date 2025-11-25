import sqlite3

# 连接到数据库
conn = sqlite3.connect('student_analytics.db')
cursor = conn.cursor()

print("=== 数据库表结构 ===")

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

if not tables:
    print("数据库中没有表")
else:
    print(f"找到 {len(tables)} 个表:")
    for table in tables:
        table_name = table[0]
        print(f"\n--- 表: {table_name} ---")
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print("列信息:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 显示前3行数据作为示例
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            rows = cursor.fetchall()
            if rows:
                print("\n示例数据 (前3行):")
                headers = [col[1] for col in columns]
                print("  " + " | ".join(headers))
                print("  " + "-" * (sum(len(h) for h in headers) + len(headers) * 3 - 1))
                for row in rows:
                    print("  " + " | ".join(str(r)[:20] + '...' if len(str(r)) > 20 else str(r) for r in row))
        except Exception as e:
            print(f"无法获取示例数据: {e}")

# 检查是否有Excel文件数据
print("\n=== Excel文件内容预览 ===")
try:
    import pandas as pd
    
    # 尝试读取data1.xlsx（学生基本信息）
    try:
        df = pd.read_excel('data1.xlsx')
        print("data1.xlsx (学生基本信息) 的列:", df.columns.tolist())
        print(f"数据行数: {len(df)}")
        print("前3行数据:")
        print(df.head(3))
    except Exception as e:
        print(f"无法读取data1.xlsx: {e}")
        
    # 尝试读取data2.xlsx（可能是消费数据）
    try:
        df = pd.read_excel('data2.xlsx')
        print("\ndata2.xlsx (可能包含消费数据) 的列:", df.columns.tolist())
        print(f"数据行数: {len(df)}")
        print("前3行数据:")
        print(df.head(3))
    except Exception as e:
        print(f"无法读取data2.xlsx: {e}")
        
    # 尝试读取data3.xlsx
    try:
        df = pd.read_excel('data3.xlsx')
        print("\ndata3.xlsx 的列:", df.columns.tolist())
        print(f"数据行数: {len(df)}")
        print("前3行数据:")
        print(df.head(3))
    except Exception as e:
        print(f"无法读取data3.xlsx: {e}")
        
except ImportError:
    print("pandas库未安装，无法预览Excel文件")

conn.close()