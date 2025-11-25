#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证消费数据的准确性"""
import logging
from utils.db_connection import execute_query, get_dataframe
import pandas as pd
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局变量存储表结构信息
table_structures = {}

# 字段映射 - 用于处理可能的不同命名
field_mappings = {
    'time': ['consumption_time', 'time', 'transaction_time', 'datetime'],
    'gender': ['gender', 'sex', 'student_gender'],
    'amount': ['amount', 'money', 'cost', 'price'],
    'location': ['location', 'place', 'shop', 'store']
}

def check_database_connection():
    """检查数据库连接状态"""
    logger.info("开始检查数据库连接状态...")
    try:
        # 执行简单的查询测试连接
        result = execute_query("SELECT 1 AS test_connection")
        if result and result[0]['test_connection'] == 1:
            logger.info("✅ 数据库连接正常")
            return True
        else:
            logger.error("❌ 数据库连接测试失败")
            return False
    except Exception as e:
        logger.error(f"❌ 检查数据库连接时出错: {str(e)}")
        return False

def get_table_structure(table_name):
    """获取指定表的结构"""
    logger.info(f"开始检查 {table_name} 表结构...")
    
    # 查询表结构
    structure_query = f"SHOW COLUMNS FROM {table_name}"
    
    try:
        columns = execute_query(structure_query)
        
        logger.info(f"{table_name} 表包含 {len(columns)} 个字段")
        for col in columns:
            logger.info(f"字段: {col['Field']}, 类型: {col['Type']}, 允许NULL: {col['Null']}")
        
        table_structures[table_name] = columns
        return columns
    except Exception as e:
        logger.error(f"❌ 查询 {table_name} 表结构时出错: {str(e)}")
        return []

def find_field_by_mapping(table_name, field_type):
    """根据映射关系在表中查找可能的字段名"""
    if table_name not in table_structures:
        get_table_structure(table_name)
    
    columns = table_structures.get(table_name, [])
    if not columns:
        return None
    
    # 获取列名列表
    column_names = [col['Field'].lower() for col in columns]
    
    # 尝试找到匹配的字段
    for possible_name in field_mappings.get(field_type, []):
        if possible_name.lower() in column_names:
            # 返回原始字段名
            for col in columns:
                if col['Field'].lower() == possible_name.lower():
                    return col['Field']
    
    # 如果没有精确匹配，尝试相似匹配
    for possible_name in field_mappings.get(field_type, []):
        for col in columns:
            if possible_name.lower() in col['Field'].lower():
                logger.warning(f"⚠️ 找到相似字段: {col['Field']} (匹配 {possible_name})")
                return col['Field']
    
    logger.warning(f"❌ 未找到 {field_type} 类型的字段")
    return None

def get_consumption_summary():
    """获取消费数据汇总信息，使用动态字段名"""
    logger.info("开始获取消费数据汇总信息...")
    
    # 确保我们有表结构信息
    if 'consumption_records' not in table_structures:
        get_table_structure('consumption_records')
    
    if 'students' not in table_structures:
        get_table_structure('students')
    
    # 动态查找字段名
    amount_field = find_field_by_mapping('consumption_records', 'amount') or 'amount'
    location_field = find_field_by_mapping('consumption_records', 'location') or 'location'
    gender_field = find_field_by_mapping('students', 'gender')
    
    logger.info(f"使用的字段映射: 金额字段={amount_field}, 位置字段={location_field}, 性别字段={gender_field}")
    
    # 获取总交易金额
    total_amount_query = f"SELECT SUM({amount_field}) AS total_amount FROM consumption_records"
    total_amount_result = execute_query(total_amount_query)
    total_amount = total_amount_result[0]['total_amount'] if total_amount_result and total_amount_result[0]['total_amount'] else 0
    
    # 获取交易笔数
    transaction_count_query = "SELECT COUNT(*) AS transaction_count FROM consumption_records"
    transaction_count_result = execute_query(transaction_count_query)
    transaction_count = transaction_count_result[0]['transaction_count'] if transaction_count_result else 0
    
    # 计算平均消费
    avg_consumption = total_amount / transaction_count if transaction_count > 0 else 0
    
    # 获取学生总数
    student_count_query = "SELECT COUNT(*) AS student_count FROM students"
    student_count_result = execute_query(student_count_query)
    student_count = student_count_result[0]['student_count'] if student_count_result else 0
    
    # 获取消费地点数量
    location_count = 0
    if location_field:
        location_count_query = f"SELECT COUNT(DISTINCT {location_field}) AS location_count FROM consumption_records"
        location_count_result = execute_query(location_count_query)
        location_count = location_count_result[0]['location_count'] if location_count_result else 0
    else:
        logger.warning("⚠️ 未找到位置字段，无法统计消费地点数量")
    
    # 按性别统计学生数量
    male_count = 0
    female_count = 0
    if gender_field:
        try:
            gender_count_query = f"SELECT {gender_field}, COUNT(*) AS count FROM students GROUP BY {gender_field}"
            gender_count_result = execute_query(gender_count_query)
            for item in gender_count_result:
                gender_value = str(item[gender_field])
                if gender_value in ['男', '1', 'M', 'male']:
                    male_count = item['count']
                elif gender_value in ['女', '0', 'F', 'female']:
                    female_count = item['count']
        except Exception as e:
            logger.error(f"❌ 统计性别时出错: {str(e)}")
    else:
        logger.warning("⚠️ 未找到性别字段，无法统计男女生数量")
    
    logger.info(f"总交易金额: ¥{total_amount:,.2f}")
    logger.info(f"交易笔数: {transaction_count}")
    logger.info(f"平均消费: ¥{avg_consumption:.2f}")
    logger.info(f"学生总数: {student_count}")
    logger.info(f"消费地点数量: {location_count}")
    logger.info(f"男生数量: {male_count}")
    logger.info(f"女生数量: {female_count}")
    
    return {
        'total_amount': total_amount,
        'transaction_count': transaction_count,
        'avg_consumption': avg_consumption,
        'student_count': student_count,
        'location_count': location_count,
        'male_count': male_count,
        'female_count': female_count
    }

def check_time_series_data():
    """检查24小时消费时段数据，使用动态字段名"""
    logger.info("开始检查24小时消费时段数据...")
    
    # 动态查找时间字段
    time_field = find_field_by_mapping('consumption_records', 'time')
    
    if not time_field:
        logger.error("❌ 未找到时间字段，无法分析消费时段数据")
        return []
    
    # 查询按小时统计的消费数据
    time_series_query = f"""
    SELECT 
        HOUR({time_field}) AS hour, 
        COUNT(*) AS consumption_count 
    FROM 
        consumption_records 
    WHERE 
        {time_field} IS NOT NULL
    GROUP BY 
        HOUR({time_field}) 
    ORDER BY 
        hour
    """
    
    try:
        time_series_data = execute_query(time_series_query)
        
        if not time_series_data:
            logger.warning("⚠️ 未找到有效的消费时段数据")
            # 检查是否有消费记录
            check_records_query = "SELECT COUNT(*) AS count FROM consumption_records"
            records_count = execute_query(check_records_query)
            logger.info(f"消费记录总数: {records_count[0]['count'] if records_count else 0}")
            return []
        
        # 确保数据覆盖24小时
        full_hour_data = {i: 0 for i in range(24)}
        for record in time_series_data:
            hour = int(record['hour'])
            full_hour_data[hour] = record['consumption_count']
        
        # 转换为列表格式
        result = [{'hour': hour, 'consumption_count': count} for hour, count in sorted(full_hour_data.items())]
        
        logger.info(f"获取到24小时消费时段数据: {len(result)} 个小时的数据")
        for item in result[:5]:  # 只显示前5个小时的数据作为示例
            logger.info(f"小时 {item['hour']}: {item['consumption_count']} 笔消费")
        
        return result
    except Exception as e:
        logger.error(f"❌ 查询时间序列数据时出错: {str(e)}")
        return []

def sample_consumption_records(limit=5):
    """获取消费记录样本，使用动态字段名"""
    logger.info(f"获取 {limit} 条消费记录样本...")
    
    # 动态查找字段
    time_field = find_field_by_mapping('consumption_records', 'time')
    amount_field = find_field_by_mapping('consumption_records', 'amount') or 'amount'
    location_field = find_field_by_mapping('consumption_records', 'location') or 'location'
    
    # 构建动态查询
    fields = ['id', 'student_id', amount_field]
    if time_field:
        fields.append(time_field)
    if location_field:
        fields.append(location_field)
    
    fields_str = ', '.join(fields)
    sample_query = f"SELECT {fields_str} FROM consumption_records LIMIT {limit}"
    
    try:
        samples = execute_query(sample_query)
        
        for sample in samples:
            log_parts = [
                f"记录ID: {sample.get('id')}",
                f"学生ID: {sample.get('student_id')}",
                f"金额: ¥{sample.get(amount_field, 0)}"
            ]
            if time_field and time_field in sample:
                log_parts.append(f"时间: {sample[time_field]}")
            if location_field and location_field in sample:
                log_parts.append(f"地点: {sample[location_field]}")
            
            logger.info(", ".join(log_parts))
        
        return samples
    except Exception as e:
        logger.error(f"❌ 获取样本数据时出错: {str(e)}")
        return []

def check_all_tables_structure():
    """检查所有相关表的结构"""
    logger.info("检查所有相关表的结构...")
    
    tables = ['consumption_records', 'students']
    
    for table in tables:
        get_table_structure(table)
    
    return table_structures

if __name__ == "__main__":
    logger.info("开始验证消费数据准确性...")
    
    # 1. 检查数据库连接
    if check_database_connection():
        # 2. 检查所有相关表的结构
        check_all_tables_structure()
        
        # 3. 获取样本数据
        sample_consumption_records()
        
        # 4. 获取汇总数据
        summary = get_consumption_summary()
        
        # 5. 检查时间序列数据（使用动态字段名）
        time_series_data = check_time_series_data()
        
        logger.info("数据验证完成!")
    else:
        logger.error("数据库连接失败，无法继续验证")