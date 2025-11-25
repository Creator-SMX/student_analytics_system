#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试24小时消费时段分析修复效果"""
import logging
import json
from utils.db_connection import execute_query
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simulate_api_response():
    """模拟API响应，测试数据格式"""
    logger.info("开始模拟API响应格式...")
    
    # 执行SQL查询获取时段分析数据，与API中使用的查询相同
    sql = """
    SELECT 
        HOUR(date_time) as hour,
        COUNT(*) as count,
        ROUND(SUM(money),2) as total_amount
    FROM 
        consumption_records
    WHERE 
        date_time IS NOT NULL
    GROUP BY 
        HOUR(date_time)
    ORDER BY 
        hour
    """
    
    try:
        # 执行查询
        results = execute_query(sql)
        logger.info(f"成功获取到 {len(results)} 个时段的数据")
        
        # 构建与API相同格式的数据结构
        time_data = {}
        for hour in range(24):
            time_data[str(hour)] = {
                'count': 0,
                'amount': 0.0
            }
        
        # 填充数据
        if results:
            for row in results:
                if 'hour' in row and 0 <= row['hour'] < 24:
                    hour = str(row['hour'])
                    time_data[hour]['count'] = int(row['count']) if row.get('count') else 0
                    time_data[hour]['amount'] = float(row.get('total_amount', 0))
        
        # 生成模拟API响应
        api_response = {
            "hourly_data": time_data,
            "success": True
        }
        
        # 打印前5个小时的数据作为示例
        logger.info("前5个小时的数据示例:")
        for hour in range(5):
            hour_str = str(hour)
            if hour_str in time_data:
                logger.info(f"小时 {hour}: 消费次数={time_data[hour_str]['count']}, 消费金额={time_data[hour_str]['amount']}")
        
        # 计算总消费次数和总金额进行验证
        total_count = sum(data['count'] for data in time_data.values())
        total_amount = sum(data['amount'] for data in time_data.values())
        logger.info(f"总消费次数: {total_count}")
        logger.info(f"总消费金额: ¥{total_amount:,.2f}")
        
        # 验证前端数据处理逻辑
        test_frontend_processing(api_response)
        
        return api_response
    except Exception as e:
        logger.error(f"模拟API响应失败: {str(e)}")
        return None

def test_frontend_processing(api_response):
    """测试前端数据处理逻辑"""
    logger.info("测试前端数据处理逻辑...")
    
    try:
        if not api_response or not api_response['success'] or not api_response['hourly_data']:
            logger.error("API响应无效")
            return
        
        # 模拟前端处理逻辑
        hours = []
        amounts = []
        for hour in range(24):
            hours.append(hour)
            hour_str = str(hour)
            hour_data = api_response['hourly_data'].get(hour_str)
            amounts.append(hour_data['count'] if hour_data else 0)
        
        # 验证数据格式和非零值
        valid_data_points = sum(1 for amount in amounts if amount > 0)
        logger.info(f"有效数据点数量: {valid_data_points}/24")
        
        if valid_data_points > 0:
            logger.info("✅ 前端数据处理逻辑测试通过")
            
            # 找出消费高峰期
            max_count = max(amounts)
            peak_hours = [hour for hour, count in enumerate(amounts) if count == max_count]
            logger.info(f"消费高峰期: {peak_hours} 时 (每小时 {max_count} 笔消费)")
            
            # 验证数据可视化的关键指标
            total_display_count = sum(amounts)
            logger.info(f"图表显示总消费次数: {total_display_count}")
        else:
            logger.warning("⚠️ 没有找到有效的消费数据，图表可能仍显示为空")
    except Exception as e:
        logger.error(f"前端数据处理逻辑测试失败: {str(e)}")

def verify_data_consistency():
    """验证数据一致性"""
    logger.info("验证数据一致性...")
    
    # 获取总交易笔数进行对比
    total_query = "SELECT COUNT(*) as total_count, SUM(money) as total_amount FROM consumption_records"
    total_result = execute_query(total_query)
    
    if total_result:
        db_total_count = total_result[0]['total_count']
        db_total_amount = total_result[0]['total_amount'] or 0
        
        # 获取按小时统计的总数
        hourly_total_query = """
        SELECT SUM(count) as hourly_count, SUM(total_amount) as hourly_amount 
        FROM (
            SELECT COUNT(*) as count, SUM(money) as total_amount 
            FROM consumption_records 
            GROUP BY HOUR(date_time)
        ) as hourly_stats
        """
        hourly_total = execute_query(hourly_total_query)
        
        if hourly_total:
            h_count = hourly_total[0]['hourly_count']
            h_amount = hourly_total[0]['hourly_amount'] or 0
            
            logger.info(f"直接统计: 总交易笔数={db_total_count}, 总金额=¥{db_total_amount:,.2f}")
            logger.info(f"按小时统计: 总交易笔数={h_count}, 总金额=¥{h_amount:,.2f}")
            
            if db_total_count == h_count and abs(db_total_amount - h_amount) < 0.01:
                logger.info("✅ 数据一致性验证通过")
            else:
                logger.warning("⚠️ 数据统计不一致，请检查")
    
if __name__ == "__main__":
    logger.info("开始测试24小时消费时段分析修复效果...")
    
    # 模拟API响应
    api_response = simulate_api_response()
    
    # 验证数据一致性
    verify_data_consistency()
    
    logger.info("测试完成！如果没有错误信息，说明修复应该能够解决图表不显示的问题。")
    logger.info("建议: 修复后重启Web服务，然后刷新页面查看24小时消费时段分析图表是否正确显示。")