# 数据库连接池最佳实践

## 概述
本文档提供了在学生消费行为分析系统中使用数据库连接池的最佳实践指南，旨在帮助开发人员正确、高效地使用连接池，避免连接泄露和性能问题。

## 核心原则

1. **始终使用连接池**：不要在每个请求中创建新的数据库连接，使用统一的连接池管理连接。
2. **自动资源管理**：利用上下文管理器（`with`语句）确保连接正确关闭和归还。
3. **避免长连接**：尽量缩短持有连接的时间，查询完成后立即释放。
4. **异常处理**：捕获并正确处理数据库操作中可能出现的异常。
5. **使用参数化查询**：防止SQL注入，提高查询效率。

## 代码示例

### 正确的查询方式

```python
from utils.db_connection import execute_query

def get_some_data(params=None):
    """获取数据的示例函数"""
    try:
        sql = "SELECT * FROM some_table WHERE id = :id"
        # 直接使用execute_query函数，内部已处理连接管理
        results = execute_query(sql, params)
        return results
    except Exception as e:
        # 记录错误日志
        logger.error(f"查询失败: {str(e)}")
        # 适当处理异常，返回默认值或抛出
        return []
```

### 正确的更新方式

```python
from utils.db_connection import execute_update

def update_some_data(data):
    """更新数据的示例函数"""
    try:
        sql = "UPDATE some_table SET name = :name WHERE id = :id"
        # 使用execute_update函数，内部已处理事务和连接管理
        success = execute_update(sql, data)
        return success
    except Exception as e:
        logger.error(f"更新失败: {str(e)}")
        return False
```

### 错误的做法（避免）

```python
# 错误：在函数内创建新的连接而不使用连接池
def bad_example():
    conn = pymysql.connect(...)  # 不要这样做！
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM some_table")
        # 可能忘记关闭连接
        return cursor.fetchall()
    finally:
        # 即使有关闭代码，也不如连接池管理高效
        conn.close()

# 错误：长事务持有连接时间过长
def another_bad_example():
    with engine.connect() as conn:
        # 开始事务
        conn.begin()
        # 执行一些操作
        # ...
        # 执行耗时的非数据库操作
        time.sleep(60)  # 避免这样做！
        # 继续执行数据库操作
        # ...
        conn.commit()
```

## 连接池配置建议

当前连接池配置位于 `utils/db_connection.py` 文件中：

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,            # 初始连接池大小
    max_overflow=20,         # 最大额外连接数
    pool_pre_ping=True,      # 连接有效性验证
    pool_recycle=3600,       # 连接回收时间（秒）
    pool_timeout=30,         # 连接获取超时时间
    echo=False               # SQL语句打印开关
)
```

### 配置调整建议

- **pool_size**: 根据并发用户数和数据库服务器性能调整，建议初始值为 `(核心数 * 2) + 有效磁盘数`
- **max_overflow**: 最大峰值连接数，通常设为 `pool_size * 2`
- **pool_recycle**: 建议设为小于数据库服务器配置的 `wait_timeout` 值，避免连接超时
- **pool_pre_ping**: 生产环境建议开启，确保获取的连接是有效的
- **pool_timeout**: 获取连接的超时时间，避免线程长时间等待

## 监控与维护

1. **监控连接使用情况**：定期检查连接池的使用情况，包括活跃连接数、等待连接的线程数等
2. **日志记录**：记录数据库操作的关键信息，包括查询时间、影响行数等
3. **性能调优**：根据实际运行情况调整SQL查询和连接池配置
4. **定期重启**：在低峰期可以考虑重启应用或重置连接池，避免潜在的资源泄漏

## 其他注意事项

1. **避免事务嵌套**：SQLAlchemy的事务管理已经很完善，避免手动嵌套事务
2. **使用会话管理**：对于ORM操作，使用SQLAlchemy的Session对象管理连接和事务
3. **批量操作优化**：对于大量数据的插入或更新，使用批量操作减少连接开销
4. **异常隔离**：一个查询的异常不应该影响其他查询的执行

## 总结

通过正确使用连接池，可以显著提高系统的性能和稳定性。遵循上述最佳实践，避免常见的错误模式，确保数据库连接得到高效管理和正确释放。

---

最后更新时间：2024年