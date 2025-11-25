import requests
import json
import pymysql
from sqlalchemy import create_engine, text

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'student_analytics'
}

# 获取数据库连接
def get_db_connection():
    try:
        # 创建数据库引擎
        engine = create_engine(
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        )
        return engine.connect()
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        return None

# 根据正确阈值获取聚类数据
def get_cluster_data_by_threshold():
    conn = None
    try:
        # 连接数据库
        conn = get_db_connection()
        if not conn:
            raise Exception("数据库连接失败")
        
        # 定义正确的聚类阈值
        thresholds = {
            '节约型': '< 122.90',
            '极简型': 'BETWEEN 122.90 AND 196.65',
            '普通型': 'BETWEEN 196.65 AND 294.97',
            '活跃型': 'BETWEEN 294.97 AND 491.62',
            '土豪型': '>= 491.62'
        }
        
        # 首先获取总消费人数（去重）
        total_sql = """
        SELECT COUNT(DISTINCT card_no) AS total_count 
        FROM consumption_records
        WHERE money > 0
        """
        total_result = conn.execute(text(total_sql)).fetchone()
        total_consumers = total_result.total_count if total_result else 0
        
        print(f"总消费人数(去重): {total_consumers}")
        
        # 定义正确的聚类标签顺序
        correct_labels = ['节约型', '极简型', '普通型', '活跃型', '土豪型']
        counts = []
        
        # 为每个聚类查询符合条件的学生人数（去重）
        for label in correct_labels:
            if label == '节约型':
                sql = f"""
                SELECT COUNT(DISTINCT card_no) AS count 
                FROM (
                    SELECT card_no, SUM(money) AS total_amount
                    FROM consumption_records
                    WHERE money > 0
                    GROUP BY card_no
                ) AS student_totals
                WHERE total_amount < 122.90
                """
            elif label == '极简型':
                sql = f"""
                SELECT COUNT(DISTINCT card_no) AS count 
                FROM (
                    SELECT card_no, SUM(money) AS total_amount
                    FROM consumption_records
                    WHERE money > 0
                    GROUP BY card_no
                ) AS student_totals
                WHERE total_amount BETWEEN 122.90 AND 196.65
                """
            elif label == '普通型':
                sql = f"""
                SELECT COUNT(DISTINCT card_no) AS count 
                FROM (
                    SELECT card_no, SUM(money) AS total_amount
                    FROM consumption_records
                    WHERE money > 0
                    GROUP BY card_no
                ) AS student_totals
                WHERE total_amount BETWEEN 196.65 AND 294.97
                """
            elif label == '活跃型':
                sql = f"""
                SELECT COUNT(DISTINCT card_no) AS count 
                FROM (
                    SELECT card_no, SUM(money) AS total_amount
                    FROM consumption_records
                    WHERE money > 0
                    GROUP BY card_no
                ) AS student_totals
                WHERE total_amount BETWEEN 294.97 AND 491.62
                """
            elif label == '土豪型':
                sql = f"""
                SELECT COUNT(DISTINCT card_no) AS count 
                FROM (
                    SELECT card_no, SUM(money) AS total_amount
                    FROM consumption_records
                    WHERE money > 0
                    GROUP BY card_no
                ) AS student_totals
                WHERE total_amount >= 491.62
                """
            
            result = conn.execute(text(sql)).fetchone()
            count = result.count if result else 0
            counts.append(count)
            print(f"{label}: {count} 人 (阈值: {thresholds[label]})")
        
        # 计算总和并验证
        cluster_sum = sum(counts)
        print(f"\n聚类总和: {cluster_sum}")
        print(f"差异: {total_consumers - cluster_sum}")
        
        # 计算百分比
        percentages = []
        for count in counts:
            percentage = round((count / total_consumers) * 100, 1) if total_consumers > 0 else 0.0
            percentages.append(percentage)
        
        # 构建修正后的数据
        corrected_data = {
            "counts": counts,
            "labels": correct_labels,
            "percentages": percentages,
            "total_consumers": total_consumers,
            "thresholds": thresholds
        }
        
        return corrected_data
    
    except Exception as e:
        print(f"获取聚类数据时出错: {str(e)}")
        # 返回空数据作为默认值
        return {
            "counts": [0, 0, 0, 0, 0],
            "labels": ['节约型', '极简型', '普通型', '活跃型', '土豪型'],
            "percentages": [0.0, 0.0, 0.0, 0.0, 0.0],
            "total_consumers": 0
        }
    finally:
        # 确保关闭数据库连接
        if conn:
            try:
                conn.close()
            except:
                pass

# 主函数
def main():
    print("=== 学生消费行为聚类分析 ===")
    print("使用正确的阈值标准进行聚类分析")
    print("\n阈值标准：")
    print("节约型阈值: < 122.90 元")
    print("极简型阈值: 122.90 - 196.65 元")
    print("普通型阈值: 196.65 - 294.97 元")
    print("活跃型阈值: 294.97 - 491.62 元")
    print("土豪型阈值: ≥ 491.62 元")
    print("\n正在查询数据...")
    
    # 获取修正后的聚类数据
    corrected_data = get_cluster_data_by_threshold()
    
    print("\n=== 修正后的聚类分析结果 ===")
    print(f"总消费人数: {corrected_data['total_consumers']}")
    print(f"聚类人数: {corrected_data['counts']}")
    print(f"聚类标签: {corrected_data['labels']}")
    print(f"聚类百分比: {corrected_data['percentages']}")
    
    # 输出JSON格式，便于在analytics_controller.py中使用
    print("\n修正后的数据JSON格式 (用于analytics_controller.py):")
    print(json.dumps(corrected_data, indent=2, ensure_ascii=False))
    
    # 现在也可以测试API调用
    print("\n=== 测试API调用 ===")
    try:
        cluster_url = 'http://localhost:5000/analytics/api/get_cluster'
        response = requests.get(cluster_url)
        print(f"API状态码: {response.status_code}")
        if response.status_code == 200:
            api_data = response.json()
            print("API返回数据:")
            print(json.dumps(api_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"API测试失败: {str(e)}")

if __name__ == "__main__":
    main()