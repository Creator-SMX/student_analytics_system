#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""数据库连接工具类 - 基于SQLAlchemy连接池"""
import pymysql
import pandas as pd
import traceback
import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 从环境变量读取数据库配置，提供默认值
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
DB_NAME = os.environ.get('DB_NAME', 'student_analytics')
DB_CHARSET = 'utf8mb4'

# 创建数据库连接URL
DATABASE_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset={DB_CHARSET}'

# 优化的连接池配置
engine = create_engine(
    DATABASE_URL,
    pool_size=15,            # 增加初始连接池大小
    max_overflow=30,         # 增加最大额外连接数
    pool_pre_ping=True,      # 连接使用前验证其有效性
    pool_recycle=1800,       # 减少连接回收时间，避免连接超时
    pool_timeout=60,         # 增加从池中获取连接的超时时间
    echo=False,              # 不打印SQL语句
    connect_args={
        'connect_timeout': 10,  # 连接超时时间
        'read_timeout': 30,     # 读取超时时间
        'write_timeout': 30     # 写入超时时间
    }
)

# 兼容旧代码的获取连接函数
def get_db_connection():
    """获取数据库连接 - 直接使用连接池"""
    try:
        return engine.connect()
    except SQLAlchemyError as e:
        logger.error(f"获取数据库连接失败: {str(e)}")
        traceback.print_exc()
        return None

class DatabaseConnection:
    """数据库连接管理类 - 基于连接池实现"""
    
    def __init__(self, host='localhost', user='root', password='123456', database='student_analytics'):
        """初始化数据库连接参数"""
        # 这里保留参数以兼容旧代码，但实际使用全局引擎
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """建立数据库连接 - 使用连接池"""
        try:
            self.connection = engine.connect()
            logger.info(f"✅ 成功从连接池获取连接: {self.database}")
            return self.connection
        except SQLAlchemyError as e:
            logger.error(f"❌ 数据库连接失败: {str(e)}")
            traceback.print_exc()
            self.connection = None
            return None
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                logger.info("✅ 数据库连接已归还连接池")
            except Exception as e:
                logger.error(f"❌ 关闭数据库连接时出错: {str(e)}")
                self.connection = None
    
    def execute_query(self, query, params=None, max_retries=3):
        """执行SQL查询并返回结果，带有自动重试机制"""
        retries = 0
        while retries <= max_retries:
            try:
                # 使用上下文管理器确保连接正确关闭
                with engine.connect() as conn:
                    # 使用SQLAlchemy的text对象包装查询
                    result = conn.execute(text(query), params or {})
                    
                    # 获取列名并转换为列表
                    columns = list(result.keys())
                    
                    # 正确转换结果为字典列表
                    rows = []
                    for row in result.fetchall():
                        # 创建行字典，确保每个值都是可序列化的
                        row_dict = {}
                        for i, value in enumerate(row):
                            col_name = columns[i]
                            # 处理可能的None值或特殊类型
                            if value is None:
                                row_dict[col_name] = None
                            else:
                                # 尝试直接使用值，如果后续有类型问题再针对性处理
                                row_dict[col_name] = value
                        rows.append(row_dict)
                    
                    return rows
            except (OperationalError, SQLAlchemyError) as e:
                retries += 1
                error_msg = str(e)
                if retries > max_retries:
                    logger.error(f"❌ 查询执行失败 (已重试{max_retries}次): {error_msg}")
                    traceback.print_exc()
                    return []  # 返回空列表而不是None，避免后续处理异常
                
                logger.warning(f"⚠️ 查询执行失败，准备重试 ({retries}/{max_retries}): {error_msg}")
                # 指数退避策略
                wait_time = 0.5 * (2 ** (retries - 1))
                time.sleep(wait_time)
                # 尝试刷新连接池
                if retries % 2 == 0:
                    logger.info("🔄 正在刷新连接池...")
                    engine.dispose()
    
    def execute_update(self, query, params=None, max_retries=3):
        """执行SQL更新操作（INSERT、UPDATE、DELETE），带有自动重试机制"""
        retries = 0
        while retries <= max_retries:
            try:
                with engine.connect() as conn:
                    with conn.begin() as transaction:
                        try:
                            conn.execute(text(query), params or {})
                            transaction.commit()
                            return True
                        except SQLAlchemyError as e:
                            transaction.rollback()
                            error_msg = str(e)
                            # 判断是否需要重试
                            if retries >= max_retries:
                                logger.error(f"❌ 更新操作失败 (已重试{max_retries}次): {error_msg}")
                                traceback.print_exc()
                                return False
                            # 某些错误可能不需要重试，如唯一键冲突等
                            if "Duplicate entry" in error_msg or "foreign key constraint" in error_msg.lower():
                                logger.warning(f"❌ 数据冲突错误，无需重试: {error_msg}")
                                return False
                            raise  # 重新抛出异常以触发重试
            except (OperationalError, SQLAlchemyError) as e:
                retries += 1
                if retries > max_retries:
                    logger.error(f"❌ 更新操作重试失败: {str(e)}")
                    return False
                
                logger.warning(f"⚠️ 更新操作失败，准备重试 ({retries}/{max_retries}): {str(e)}")
                # 指数退避策略
                wait_time = 0.5 * (2 ** (retries - 1))
                time.sleep(wait_time)
                # 尝试刷新连接池
                if retries % 2 == 0:
                    logger.info("🔄 正在刷新连接池...")
                    engine.dispose()
        return False
    
    def get_dataframe(self, query, params=None):
        """执行查询并返回Pandas DataFrame"""
        try:
            # 使用pandas的read_sql函数直接从引擎获取DataFrame
            df = pd.read_sql(query, engine, params=params)
            return df
        except Exception as e:
            logger.error(f"❌ 获取DataFrame失败: {str(e)}")
            traceback.print_exc()
            raise Exception(f"查询执行失败: {str(e)}")
    
    def execute_many(self, query, params_list, max_retries=3):
        """批量执行SQL操作，带有自动重试机制"""
        retries = 0
        while retries <= max_retries:
            try:
                with engine.connect() as conn:
                    with conn.begin() as transaction:
                        try:
                            conn.execute(text(query), params_list)
                            transaction.commit()
                            return True
                        except SQLAlchemyError as e:
                            transaction.rollback()
                            error_msg = str(e)
                            if retries >= max_retries:
                                logger.error(f"❌ 批量执行失败 (已重试{max_retries}次): {error_msg}")
                                traceback.print_exc()
                                return False
                            # 对于批量操作，数据冲突错误通常也不需要重试
                            if "Duplicate entry" in error_msg or "foreign key constraint" in error_msg.lower():
                                logger.warning(f"❌ 批量操作数据冲突，无需重试: {error_msg}")
                                return False
                            raise
            except (OperationalError, SQLAlchemyError) as e:
                retries += 1
                if retries > max_retries:
                    logger.error(f"❌ 批量执行重试失败: {str(e)}")
                    return False
                
                logger.warning(f"⚠️ 批量执行失败，准备重试 ({retries}/{max_retries}): {str(e)}")
                wait_time = 0.5 * (2 ** (retries - 1))
                time.sleep(wait_time)
                if retries % 2 == 0:
                    logger.info("🔄 正在刷新连接池...")
                    engine.dispose()
        return False
    
    def begin_transaction(self):
        """开始事务 - 使用上下文管理器替代手动事务管理"""
        logger.warning("注意: 建议使用上下文管理器处理事务，而非手动调用")
        return self.connect()
    
    def commit_transaction(self):
        """提交事务 - 保留以兼容旧代码"""
        logger.warning("注意: 建议使用上下文管理器处理事务，而非手动调用")
        if self.connection:
            try:
                self.connection.commit()
                return True
            except Exception as e:
                logger.error(f"❌ 提交事务失败: {str(e)}")
                traceback.print_exc()
                return False
        return False
    
    def rollback_transaction(self):
        """回滚事务 - 保留以兼容旧代码"""
        logger.warning("注意: 建议使用上下文管理器处理事务，而非手动调用")
        if self.connection:
            try:
                self.connection.rollback()
                return True
            except Exception as e:
                logger.error(f"❌ 回滚事务失败: {str(e)}")
                traceback.print_exc()
                return False
        return False

# 创建单例实例，但内部使用连接池
db_conn = DatabaseConnection(user='root', password='123456', database='student_analytics')

# 导出主要功能函数供其他模块使用
def execute_query(query, params=None, max_retries=3):
    """便捷的查询执行函数，支持重试参数"""
    try:
        result = db_conn.execute_query(query, params, max_retries)
        # 确保返回的始终是列表类型
        return result if isinstance(result, list) else []
    except Exception as e:
        logger.error(f"❌ 执行查询时发生异常: {str(e)}")
        return []

def execute_update(query, params=None, max_retries=3):
    """便捷的更新执行函数，支持重试参数"""
    return db_conn.execute_update(query, params, max_retries)

def get_dataframe(query, params=None):
    """便捷的DataFrame获取函数"""
    try:
        # 为DataFrame查询也添加重试机制
        max_retries = 3
        retries = 0
        while retries <= max_retries:
            try:
                return pd.read_sql(query, engine, params=params)
            except (OperationalError, SQLAlchemyError) as e:
                retries += 1
                if retries > max_retries:
                    logger.error(f"❌ 获取DataFrame失败 (已重试{max_retries}次): {str(e)}")
                    traceback.print_exc()
                    raise Exception(f"查询执行失败: {str(e)}")
                
                logger.warning(f"⚠️ 获取DataFrame失败，准备重试 ({retries}/{max_retries}): {str(e)}")
                time.sleep(0.5 * (2 ** (retries - 1)))
                if retries % 2 == 0:
                    logger.info("🔄 正在刷新连接池...")
                    engine.dispose()
    except Exception as e:
        logger.error(f"❌ 获取DataFrame异常: {str(e)}")
        traceback.print_exc()
        raise