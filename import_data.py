import pandas as pd
import mysql.connector
from mysql.connector import Error
import hashlib
import time
import sys

# 数据库连接信息
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'student_analytics',
    'charset': 'utf8mb4'
}

def md5_hash(text):
    """计算MD5哈希值"""
    return hashlib.md5(str(text).encode()).hexdigest()

def connect_to_db():
    """连接到数据库"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print(f"✅ 成功连接到数据库: {DB_CONFIG['database']}")
            return connection
    except Error as e:
        print(f"❌ 数据库连接失败: {e}")
        sys.exit(1)

def import_students(cursor, batch_size=1000):
    """导入学生数据"""
    try:
        print("\n📥 开始导入学生数据...")
        # 读取CSV文件
        df = pd.read_csv('data1.csv', encoding='gbk')
        total_rows = len(df)
        print(f"读取到 {total_rows} 条学生数据")
        
        # 清空表
        cursor.execute("TRUNCATE TABLE students")
        
        # 去重处理
        print("正在处理重复数据...")
        # 基于校园卡号去重
        df_clean = df.drop_duplicates(subset=['CardNo'], keep='first')
        duplicates_removed = total_rows - len(df_clean)
        print(f"已移除 {duplicates_removed} 条重复数据")
        
        # 准备插入数据
        start_time = time.time()
        inserted_count = 0
        failed_count = 0
        
        # 批量插入
        for i in range(0, len(df_clean), batch_size):
            batch = df_clean.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                try:
                    # 生成默认密码（卡号后6位）
                    default_password = str(row['CardNo'])[-6:] if len(str(row['CardNo'])) >= 6 else '123456'
                    hashed_password = md5_hash(default_password)
                    
                    # 执行单条插入，避免一条错误影响整批
                    sql = """
                        INSERT INTO students (card_no, sex, major, access_card_no, password)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        row['CardNo'],
                        row['Sex'],
                        row['Major'],
                        row['AccessCardNo'],
                        hashed_password
                    ))
                    inserted_count += 1
                    
                    # 显示进度
                    if inserted_count % 100 == 0 or inserted_count == len(df_clean):
                        progress = (inserted_count / len(df_clean)) * 100
                        print(f"进度: {progress:.1f}% - 已导入 {inserted_count} 条数据")
                except Exception as e:
                    failed_count += 1
                    # 继续处理下一条数据
                    continue
        
        end_time = time.time()
        print(f"✅ 学生数据导入完成!")
        print(f"总共导入: {inserted_count} 条")
        print(f"导入失败: {failed_count} 条")
        print(f"耗时: {end_time - start_time:.2f} 秒")
        
    except Exception as e:
        print(f"❌ 学生数据导入失败: {e}")
        raise

def import_consumption_records(cursor, batch_size=10000):
    """导入消费记录数据"""
    try:
        print("\n📥 开始导入消费记录数据...")
        # 读取CSV文件
        df = pd.read_csv('data2.csv', encoding='gbk')
        total_rows = len(df)
        print(f"读取到 {total_rows} 条消费记录数据")
        
        # 清空表
        cursor.execute("TRUNCATE TABLE consumption_records")
        
        # 准备插入数据
        start_time = time.time()
        inserted_count = 0
        failed_count = 0
        
        # 批量插入
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                try:
                    # 处理日期时间
                    date_time = None
                    if 'Date' in row and pd.notna(row['Date']):
                        try:
                            date_time = pd.to_datetime(row['Date'])
                        except:
                            pass
                    
                    # 执行单条插入
                    sql = """
                        INSERT INTO consumption_records 
                        (card_no, peo_no, date_time, money, term_no, term_ser_no, con_oper_no, oper_no, dept)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        row['CardNo'] if pd.notna(row['CardNo']) else None,
                        row['PeoNo'] if pd.notna(row['PeoNo']) else None,
                        date_time,
                        row['Money'] if pd.notna(row['Money']) else 0,
                        row['TermNo'] if pd.notna(row['TermNo']) else None,
                        row['TermSerNo'] if pd.notna(row['TermSerNo']) else None,
                        row['conOperNo'] if pd.notna(row['conOperNo']) else None,
                        row['OperNo'] if pd.notna(row['OperNo']) else None,
                        row['Dept'] if pd.notna(row['Dept']) else None
                    ))
                    inserted_count += 1
                    
                    # 显示进度
                    if inserted_count % 1000 == 0 or inserted_count == total_rows:
                        progress = (inserted_count / total_rows) * 100
                        print(f"进度: {progress:.1f}% - 已导入 {inserted_count} 条数据")
                except Exception as e:
                    failed_count += 1
                    # 继续处理下一条数据
                    continue
        
        end_time = time.time()
        print(f"✅ 消费记录数据导入完成!")
        print(f"总共导入: {inserted_count} 条")
        print(f"导入失败: {failed_count} 条")
        print(f"耗时: {end_time - start_time:.2f} 秒")
        
    except Exception as e:
        print(f"❌ 消费记录数据导入失败: {e}")
        raise

def import_access_records(cursor, batch_size=10000):
    """导入门禁记录数据"""
    try:
        print("\n📥 开始导入门禁记录数据...")
        # 读取CSV文件
        df = pd.read_csv('data3.csv', encoding='gbk')
        total_rows = len(df)
        print(f"读取到 {total_rows} 条门禁记录数据")
        
        # 清空表
        cursor.execute("TRUNCATE TABLE access_records")
        
        # 准备插入数据
        start_time = time.time()
        inserted_count = 0
        failed_count = 0
        
        # 批量插入
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                try:
                    # 处理日期时间
                    date_time = None
                    if 'Date' in row and pd.notna(row['Date']):
                        try:
                            date_time = pd.to_datetime(row['Date'])
                        except:
                            pass
                    
                    # 执行单条插入
                    sql = """
                        INSERT INTO access_records 
                        (card_no, access_time, location)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql, (
                        row['AccessCardNo'] if pd.notna(row['AccessCardNo']) else None,
                        date_time,
                        row['Address'] if pd.notna(row['Address']) else None
                    ))
                    inserted_count += 1
                    
                    # 显示进度
                    if inserted_count % 1000 == 0 or inserted_count == total_rows:
                        progress = (inserted_count / total_rows) * 100
                        print(f"进度: {progress:.1f}% - 已导入 {inserted_count} 条数据")
                except Exception as e:
                    failed_count += 1
                    # 继续处理下一条数据
                    continue
        
        end_time = time.time()
        print(f"✅ 门禁记录数据导入完成!")
        print(f"总共导入: {inserted_count} 条")
        print(f"导入失败: {failed_count} 条")
        print(f"耗时: {end_time - start_time:.2f} 秒")
        
    except Exception as e:
        print(f"❌ 门禁记录数据导入失败: {e}")
        raise

def main():
    """主函数"""
    print("====================================")
    print("学生消费行为分析系统 - 数据导入")
    print("====================================")
    
    connection = connect_to_db()
    
    try:
        cursor = connection.cursor()
        
        # 导入数据
        import_students(cursor)
        import_consumption_records(cursor)
        import_access_records(cursor)
        
        # 提交事务
        connection.commit()
        print("\n🎉 所有数据导入成功!")
        
        # 显示数据统计
        print("\n📊 数据统计:")
        cursor.execute("SELECT COUNT(*) FROM students")
        print(f"学生数量: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM consumption_records")
        print(f"消费记录数量: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM access_records")
        print(f"门禁记录数量: {cursor.fetchone()[0]}")
        
    except Exception as e:
        print(f"\n❌ 数据导入过程中发生错误: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n数据库连接已关闭")

if __name__ == "__main__":
    main()