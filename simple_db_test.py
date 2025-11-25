#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单的数据库测试脚本"""
import pymysql

# 输出文件
with open('db_test_output.txt', 'w', encoding='utf-8') as f:
    f.write("=== 数据库连接测试开始 ===\n")
    
    try:
        # 尝试连接数据库
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='student_analytics',
            charset='utf8mb4'
        )
        f.write("✅ 数据库连接成功！\n")
        
        # 检查数据库中的表
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            f.write(f"数据库中的表数量: {len(tables)}\n")
            for table in tables:
                table_name = table[0]
                f.write(f"- 表名: {table_name}\n")
                
                # 检查每个表的结构
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                f.write(f"  字段数量: {len(columns)}\n")
                for col in columns:
                    f.write(f"  - {col[0]}: {col[1]}\n")
                
                # 检查记录数量
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                f.write(f"  记录数量: {count}\n")
        
        conn.close()
        f.write("\n✅ 数据库连接已关闭\n")
        
    except Exception as e:
        f.write(f"❌ 错误: {str(e)}\n")
        import traceback
        f.write(f"错误详情: {traceback.format_exc()}\n")
    
    f.write("\n=== 数据库连接测试结束 ===\n")

print("测试完成，请查看 db_test_output.txt 文件获取结果")