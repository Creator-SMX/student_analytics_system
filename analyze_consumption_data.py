import pymysql
import pandas as pd
import numpy as np
from collections import defaultdict

# 连接到MySQL数据库
print("正在连接到MySQL数据库...")
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',  # 用户提供的正确密码
    database='student_analytics',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()
print("数据库连接成功")

print("=== 数据库结构和数据检查 ===")

# 获取所有表
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()

if tables:
    print(f"找到 {len(tables)} 个表:")
    for table in tables:
        # DictCursor返回字典，需要获取表名的正确键
        table_name = list(table.values())[0]  # 获取字典的第一个值
        print(f"\n--- 表: {table_name} ---")
        
        # 获取表结构
        cursor.execute(f"DESCRIBE {table_name};")
        columns = cursor.fetchall()
        print("列信息:")
        for col in columns:
            print(f"  {col['Field']} ({col['Type']})")
        
        # 获取表数据量
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
        count = cursor.fetchone()['count']  # 使用别名获取计数
        print(f"数据行数: {count}")
        
        # 显示前5行数据作为示例
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
            rows = cursor.fetchall()
            if rows:
                print("前5行数据:")
                headers = [col['Field'] for col in columns]
                print("  " + " | ".join(headers[:3]) + " | ...")
                print("  " + "-" * 70)
                for row in rows:
                    row_values = list(row.values())[:3]
                    print("  " + " | ".join(str(r)[:20] for r in row_values) + " | ...")
        except Exception as e:
            print(f"无法获取示例数据: {e}")
else:
    print("数据库中没有表，需要从CSV文件导入数据")

# 检查CSV文件是否存在并准备导入
has_csv_data = False
csv_files = ['data1.csv', 'data2.csv', 'data3.csv']
for csv_file in csv_files:
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            print(f"\nCSV文件 {csv_file} 存在")
            has_csv_data = True
    except:
        try:
            with open(csv_file, 'r', encoding='gbk') as f:
                print(f"\nCSV文件 {csv_file} 存在 (使用gbk编码)")
                has_csv_data = True
        except:
            print(f"\nCSV文件 {csv_file} 不存在或无法读取")

# 获取表名列表
table_names = [list(table.values())[0] for table in tables]
print(f"\n数据库中的表名: {table_names}")

# 如果数据库中没有消费记录表但有CSV文件，创建表并导入数据
if has_csv_data and 'consumption_records' not in table_names:
    print("\n=== 从CSV文件导入数据到数据库 ===")
    
    # 创建students表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id_index INTEGER,
        CardNo INTEGER PRIMARY KEY,
        Sex TEXT,
        Major TEXT,
        AccessCardNo INTEGER
    )''')
    print("创建students表")
    
    # 创建consumption_records表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consumption_records (
        id_index INTEGER,
        CardNo INTEGER,
        PeoNo INTEGER,
        Date TEXT,
        Money REAL,
        FundMoney REAL,
        Surplus REAL,
        CardCount INTEGER,
        Type TEXT,
        TermNo TEXT,
        TermSerNo INTEGER,
        conOperNo TEXT,
        OperNo TEXT,
        Dept TEXT,
        FOREIGN KEY (CardNo) REFERENCES students(CardNo)
    )''')
    print("创建consumption_records表")
    
    # 创建access_records表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_records (
        id_index INTEGER,
        AccessCardNo INTEGER,
        Date TEXT,
        Address TEXT,
        Access TEXT,
        Describe TEXT
    )''')
    print("创建access_records表")
    
    # 导入数据
    try:
        # 导入学生数据
        print("导入学生数据...")
        try:
            df_students = pd.read_csv('data1.csv', encoding='utf-8')
        except:
            df_students = pd.read_csv('data1.csv', encoding='gbk')
        
        for _, row in df_students.iterrows():
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO students (Index, CardNo, Sex, Major, AccessCardNo) VALUES (?, ?, ?, ?, ?)",
                    (row['Index'], row['CardNo'], row['Sex'], row['Major'], row['AccessCardNo'])
                )
            except:
                pass
        print(f"导入学生数据完成，共 {len(df_students)} 条")
        
        # 导入消费数据
        print("导入消费数据...")
        try:
            df_consumption = pd.read_csv('data2.csv', encoding='utf-8')
        except:
            df_consumption = pd.read_csv('data2.csv', encoding='gbk')
        
        # 批量导入以提高速度
        batch_size = 10000
        for i in range(0, len(df_consumption), batch_size):
            batch = df_consumption.iloc[i:i+batch_size]
            values = []
            for _, row in batch.iterrows():
                try:
                    values.append((
                        row.get('Index', None),
                        row.get('CardNo', None),
                        row.get('PeoNo', None),
                        row.get('Date', None),
                        row.get('Money', 0),
                        row.get('FundMoney', 0),
                        row.get('Surplus', 0),
                        row.get('CardCount', 0),
                        row.get('Type', None),
                        row.get('TermNo', None),
                        row.get('TermSerNo', None),
                        row.get('conOperNo', None),
                        row.get('OperNo', None),
                        row.get('Dept', None)
                    ))
                except:
                    pass
            
            if values:
                cursor.executemany(
                    "INSERT INTO consumption_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    values
                )
                conn.commit()
                print(f"已导入 {min(i+batch_size, len(df_consumption))}/{len(df_consumption)} 条消费数据")
        
        print(f"导入消费数据完成，共 {len(df_consumption)} 条")
        
        # 导入门禁数据
        print("导入门禁数据...")
        try:
            df_access = pd.read_csv('data3.csv', encoding='utf-8')
        except:
            df_access = pd.read_csv('data3.csv', encoding='gbk')
        
        for _, row in df_access.iterrows():
            try:
                cursor.execute(
                    "INSERT INTO access_records VALUES (?, ?, ?, ?, ?, ?)",
                    (row['Index'], row['AccessCardNo'], row['Date'], row['Address'], row['Access'], row['Describe'])
                )
            except:
                pass
        print(f"导入门禁数据完成，共 {len(df_access)} 条")
        
    except Exception as e:
        print(f"导入数据时出错: {e}")

# 执行消费数据分析和聚类计算
print("\n=== 学生消费数据分析和聚类计算 ===")
try:
    # 查询学生月消费统计
    print("计算每位学生的月平均消费金额...")
    cursor.execute('''
    SELECT 
        card_no,
        SUM(money) as monthly_consumption
    FROM 
        consumption_records
    GROUP BY 
        card_no
    ''')
    student_consumption = cursor.fetchall()
    
    print(f"找到 {len(student_consumption)} 位有消费记录的学生")
    
    if student_consumption:
        # 直接将查询结果转换为DataFrame
        consumption_data = pd.DataFrame(student_consumption)
        
        # 确保使用正确的字段名
        if 'monthly_consumption' in consumption_data.columns:
            # 重命名列以便与后续分析代码保持一致
            consumption_data = consumption_data.rename(columns={'monthly_consumption': 'total_monthly_consumption'})
        
        # 计算消费统计信息
        avg_consumption = consumption_data['total_monthly_consumption'].mean()
        median_consumption = consumption_data['total_monthly_consumption'].median()
        min_consumption = consumption_data['total_monthly_consumption'].min()
        max_consumption = consumption_data['total_monthly_consumption'].max()
        
        print(f"消费统计：")
        print(f"  平均消费: {avg_consumption:.2f} 元")
        print(f"  中位数消费: {median_consumption:.2f} 元")
        print(f"  最小消费: {min_consumption:.2f} 元")
        print(f"  最大消费: {max_consumption:.2f} 元")
        
        # 定义消费类型的划分标准
        # 1. 节约型: 消费金额 < 平均消费的50%
        # 2. 极简型: 平均消费的50% ≤ 消费金额 < 平均消费的80%
        # 3. 普通型: 平均消费的80% ≤ 消费金额 < 平均消费的120%
        # 4. 活跃型: 平均消费的120% ≤ 消费金额 < 平均消费的200%
        # 5. 土豪型: 消费金额 ≥ 平均消费的200%
        
        threshold1 = avg_consumption * 0.5
        threshold2 = avg_consumption * 0.8
        threshold3 = avg_consumption * 1.2
        threshold4 = avg_consumption * 2.0
        
        print(f"\n聚类阈值：")
        print(f"  节约型阈值: < {threshold1:.2f} 元")
        print(f"  极简型阈值: {threshold1:.2f} - {threshold2:.2f} 元")
        print(f"  普通型阈值: {threshold2:.2f} - {threshold3:.2f} 元")
        print(f"  活跃型阈值: {threshold3:.2f} - {threshold4:.2f} 元")
        print(f"  土豪型阈值: ≥ {threshold4:.2f} 元")
        
        # 进行聚类统计
        consumption_categories = defaultdict(int)
        
        for _, row in consumption_data.iterrows():
            consumption = row['total_monthly_consumption']
            if consumption < threshold1:
                consumption_categories['节约型'] += 1
            elif consumption < threshold2:
                consumption_categories['极简型'] += 1
            elif consumption < threshold3:
                consumption_categories['普通型'] += 1
            elif consumption < threshold4:
                consumption_categories['活跃型'] += 1
            else:
                consumption_categories['土豪型'] += 1
        
        # 确保所有类型都有值
        category_order = ['节约型', '极简型', '普通型', '活跃型', '土豪型']
        for category in category_order:
            if category not in consumption_categories:
                consumption_categories[category] = 0
        
        # 计算百分比
        total_students = len(consumption_data)
        print(f"\n聚类结果 (总学生数: {total_students}):")
        
        counts = []
        percentages = []
        labels = []
        
        for category in category_order:
            count = consumption_categories[category]
            percentage = (count / total_students * 100) if total_students > 0 else 0
            counts.append(count)
            percentages.append(percentage)
            labels.append(category)
            print(f"  {category}: {count} 人 ({percentage:.1f}%)")
        
        # 生成用于饼图的数据结构
        chart_data = {
            'labels': labels,
            'counts': counts,
            'percentages': percentages,
            'totalStudents': total_students
        }
        
        print("\n饼图数据结构:")
        print(f"  labels: {labels}")
        print(f"  counts: {counts}")
        print(f"  percentages: {[f'{p:.1f}' for p in percentages]}")
        print(f"  totalStudents: {total_students}")
        
        # 将聚类结果保存到数据库供API使用
        print("\n保存聚类结果到数据库...")
        
        # 使用try-except避免表已存在错误
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumption_clusters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category VARCHAR(50),
                count INT,
                percentage DOUBLE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
        except Exception as e:
            print(f"表已存在或创建表时出错: {e}")
        
        # 清空旧数据
        cursor.execute("DELETE FROM consumption_clusters")
        
        # 插入新数据
        for i, category in enumerate(category_order):
            cursor.execute(
                "INSERT INTO consumption_clusters (category, count, percentage) VALUES (%s, %s, %s)",
                (category, counts[i], percentages[i])
            )
        conn.commit()
        print("聚类结果保存成功")
        
        # 创建用于API的视图
        cursor.execute('''
        CREATE OR REPLACE VIEW vw_consumption_clusters AS
        SELECT 
            GROUP_CONCAT(category SEPARATOR ',') as labels,
            GROUP_CONCAT(count SEPARATOR ',') as counts,
            GROUP_CONCAT(percentage SEPARATOR ',') as percentages,
            SUM(count) as total_students
        FROM 
            consumption_clusters
        ORDER BY 
            FIELD(category, '节约型', '极简型', '普通型', '活跃型', '土豪型')
        ''')
        conn.commit()
        print("创建聚类视图成功")
        
        # 测试视图数据
        cursor.execute("SELECT * FROM vw_consumption_clusters")
        view_data = cursor.fetchone()
        if view_data:
            print(f"\n聚类视图数据测试:")
            print(f"  labels: {view_data[0]}")
            print(f"  counts: {view_data[1]}")
            print(f"  percentages: {view_data[2]}")
            print(f"  total_students: {view_data[3]}")
        else:
            print("\n未能获取聚类视图数据")
    else:
        print("没有找到消费记录，无法进行聚类分析")
        
except Exception as e:
    print(f"分析过程中出错: {e}")

conn.close()
print("\n数据库分析和聚类计算完成")