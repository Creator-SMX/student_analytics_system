#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库数据状态"""
import logging
from utils.db_connection import execute_query

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_tables():
    """检查数据库表结构和数据"""
    try:
        # 检查门禁记录表
        logger.info("\n=== 检查门禁记录表 ===")
        access_tables_sql = "SHOW TABLES LIKE 'access_records'"
        access_tables = execute_query(access_tables_sql)
        
        if access_tables:
            logger.info("✅ 门禁记录表存在")
            
            # 检查门禁表结构
            access_structure_sql = "DESCRIBE access_records"
            access_structure = execute_query(access_structure_sql)
            logger.info(f"门禁表结构: {len(access_structure)} 个字段")
            for field in access_structure[:3]:  # 只显示前3个字段
                logger.info(f"  - {field}")
            
            # 检查门禁数据
            access_count_sql = "SELECT COUNT(*) as count FROM access_records"
            access_count = execute_query(access_count_sql)
            logger.info(f"门禁记录总数: {access_count[0]['count'] if access_count else 0}")
            
            # 检查24小时分布数据
            access_hourly_sql = "SELECT HOUR(date_time) h, COUNT(*) cnt FROM access_records GROUP BY h ORDER BY h LIMIT 5"
            access_hourly = execute_query(access_hourly_sql)
            logger.info(f"门禁数据前5个小时: {access_hourly}")
        else:
            logger.error("❌ 门禁记录表不存在")
        
        # 检查消费记录表
        logger.info("\n=== 检查消费记录表 ===")
        consumption_tables_sql = "SHOW TABLES LIKE 'consumption_records'"
        consumption_tables = execute_query(consumption_tables_sql)
        
        if consumption_tables:
            logger.info("✅ 消费记录表存在")
            
            # 检查消费数据
            consumption_count_sql = "SELECT COUNT(*) as count FROM consumption_records WHERE money > 0"
            consumption_count = execute_query(consumption_count_sql)
            logger.info(f"有效消费记录数: {consumption_count[0]['count'] if consumption_count else 0}")
            
            # 检查总金额
            consumption_amount_sql = "SELECT SUM(money) as total FROM consumption_records WHERE money > 0"
            consumption_amount = execute_query(consumption_amount_sql)
            total = consumption_amount[0]['total'] if consumption_amount and consumption_amount[0]['total'] else 0
            logger.info(f"总交易金额: {total}")
            
            # 检查24小时消费数据
            consumption_hourly_sql = "SELECT HOUR(date_time) h, COUNT(*) cnt FROM consumption_records GROUP BY h ORDER BY h LIMIT 5"
            consumption_hourly = execute_query(consumption_hourly_sql)
            logger.info(f"消费数据前5个小时: {consumption_hourly}")
        else:
            logger.error("❌ 消费记录表不存在")
        
        return True
        
    except Exception as e:
        logger.error(f"检查数据库时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("开始检查数据库状态...")
    check_database_tables()
    logger.info("检查完成")