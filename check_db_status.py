#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库状态和表结构"""

# 导入数据库连接类
from utils.db_connection import DatabaseConnection

# 创建数据库连接
print("正在连接到数据库...")
db = DatabaseConnection()

# 尝试连接数据库
if db.connect():
    print("数据库连接成功！")
    
    # 获取数据库中的所有表
    try:
        query = "SHOW TABLES;"
        tables = db.execute_query(query)
        
        if tables:
            print("\n数据库中的表：")
            table_list = []
            for table in tables:
                for key, value in table.items():
                    table_list.append(value)
                    print(f"- {value}")
            
            # 显示每个表的结构
            print("\n表结构详情：")
            for table_name in table_list:
                print(f"\n{table_name} 表结构：")
                desc_query = f"DESCRIBE {table_name};"
                structure = db.execute_query(desc_query)
                if structure:
                    # 格式化输出表结构
                    print("字段名\t类型\t是否为空\t键\t默认值\t额外信息")
                    print("-" * 80)
                    for field in structure:
                        field_name = field['Field']
                        field_type = field['Type']
                        null = field['Null']
                        key = field['Key']
                        default = field['Default'] if field['Default'] else ''
                        extra = field['Extra']
                        print(f"{field_name}\t{field_type}\t{null}\t{key}\t{default}\t{extra}")
        else:
            print("数据库中没有表！")
            
    except Exception as e:
        print(f"获取表信息时出错: {str(e)}")
    
    # 检查是否有数据
    if table_list:
        print("\n表数据量检查：")
        for table_name in table_list:
            count_query = f"SELECT COUNT(*) as count FROM {table_name};"
            result = db.execute_query(count_query)
            if result:
                count = result[0]['count']
                print(f"{table_name} 表中有 {count} 条记录")
    
    # 关闭数据库连接
    db.disconnect()
else:
    print("数据库连接失败，请检查数据库配置！")