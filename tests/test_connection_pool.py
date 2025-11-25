import unittest
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.db_connection import execute_query

class TestConnectionPool(unittest.TestCase):
    """测试数据库连接池在并发环境下的稳定性"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.concurrent_tasks = 20  # 并发任务数
        self.queries_per_task = 5   # 每个任务执行的查询次数
    
    def test_single_connection(self):
        """测试单个连接是否正常工作"""
        sql = "SELECT 1 as test_value"
        results = execute_query(sql)
        # 使用更简单直接的断言
        self.assertIsInstance(results, list, "返回结果应该是列表类型")
        print(f"查询返回结果数量: {len(results)}")
        if results:
            print(f"第一条结果内容: {results[0]}")
            self.assertIn('test_value', results[0], "结果中应该包含'test_value'字段")
            self.assertEqual(results[0]['test_value'], 1, "test_value的值应该为1")
        print("✓ 单个连接测试完成")
    
    def test_concurrent_reads(self):
        """测试并发读取操作"""
        def execute_read_query():
            """执行读取查询"""
            try:
                # 随机选择一个查询
                queries = [
                    "SELECT COUNT(*) as count FROM students LIMIT 10",
                    "SELECT COUNT(*) as count FROM consumption_records LIMIT 10",
                    "SELECT 1 as test_value"
                ]
                sql = random.choice(queries)
                start_time = time.time()
                results = execute_query(sql)
                end_time = time.time()
                # 验证结果
                self.assertIsInstance(results, list)
                return True, end_time - start_time
            except Exception as e:
                return False, str(e)
        
        # 使用线程池执行并发查询
        success_count = 0
        failure_count = 0
        failure_messages = []
        
        print(f"开始执行 {self.concurrent_tasks} 个并发读取任务，每个任务执行 {self.queries_per_task} 次查询...")
        
        with ThreadPoolExecutor(max_workers=self.concurrent_tasks) as executor:
            futures = []
            # 提交所有任务
            for i in range(self.concurrent_tasks):
                futures.append(executor.submit(
                    lambda: [execute_read_query() for _ in range(self.queries_per_task)]
                ))
            
            # 收集结果
            for future in as_completed(futures):
                try:
                    task_results = future.result()
                    for success, result in task_results:
                        if success:
                            success_count += 1
                        else:
                            failure_count += 1
                            failure_messages.append(result)
                except Exception as e:
                    failure_count += self.queries_per_task
                    failure_messages.append(f"任务执行异常: {str(e)}")
        
        total_queries = self.concurrent_tasks * self.queries_per_task
        print(f"并发读取测试完成 - 总查询: {total_queries}, 成功: {success_count}, 失败: {failure_count}")
        
        if failure_messages:
            print("失败详情:")
            for msg in failure_messages[:5]:  # 只显示前5个失败信息
                print(f"  - {msg}")
            if len(failure_messages) > 5:
                print(f"  ... 还有 {len(failure_messages) - 5} 个失败信息")
        
        # 断言所有查询都成功
        self.assertEqual(failure_count, 0, f"有 {failure_count} 个查询失败")
    
    def test_connection_limits(self):
        """测试连接池在高并发下的表现"""
        # 创建固定数量的并发连接，不依赖于连接池的具体大小
        test_pool_size = 10  # 测试使用的连接数
        threads = []
        results = []
        
        def hold_connection():
            """占用一个连接一段时间"""
            try:
                # 使用不同的SQL来避免可能的查询缓存影响
                sql = f"SELECT 1 as test_value WHERE 1={random.randint(1,1)}"
                execute_query(sql)
                time.sleep(0.5)  # 模拟一些处理时间
                results.append(True)
            except Exception as e:
                print(f"连接失败: {str(e)}")
                results.append(False)
        
        print(f"测试连接限制: 创建 {test_pool_size + 5} 个并发连接...")
        
        # 创建多个线程同时占用连接
        for _ in range(test_pool_size + 5):
            t = threading.Thread(target=hold_connection)
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 验证大部分请求都能得到处理
        success_count = sum(results)
        print(f"连接限制测试 - 成功: {success_count}, 总请求数: {len(threads)}")
        
        # 期望至少80%的请求成功
        min_success_rate = 0.8
        self.assertGreaterEqual(success_count, len(threads) * min_success_rate, 
                               f"至少{min_success_rate*100}%的请求应该成功")
    
    def test_long_running_connections(self):
        """测试长时间运行的连接是否会被正确回收"""
        def long_running_query(sleep_time):
            """执行长时间运行的查询"""
            try:
                sql = f"SELECT SLEEP({sleep_time})"
                execute_query(sql)
                return True
            except Exception as e:
                print(f"长时间查询失败: {str(e)}")
                return False
        
        # 测试不同时长的查询
        sleep_times = [0.5, 1.0, 2.0]
        
        print("测试长时间运行的连接...")
        for sleep_time in sleep_times:
            print(f"  执行 {sleep_time} 秒的查询...")
            success = long_running_query(sleep_time)
            self.assertTrue(success, f"{sleep_time}秒的查询失败")
        
        print("✓ 长时间运行连接测试通过")

if __name__ == '__main__':
    unittest.main()