import pymysql
import hashlib
import csv
import io
from datetime import datetime
from flask import make_response

class AdminModel:
    @staticmethod
    def get_db_connection():
        """获取数据库连接"""
        return pymysql.connect(
            host='localhost',
            user='root',
            password='123456',  # 使用与create_database.py相同的密码
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    
    @staticmethod
    def get_students(page=1, per_page=10, search='', sort_by='card_no', sort_order='asc'):
        """获取学生列表，支持分页、搜索和排序"""
        connection = None
        try:
            connection = AdminModel.get_db_connection()
            with connection.cursor() as cursor:
                # 字段映射：前端使用的字段名 -> 数据库字段名
                field_mapping = {
                    'CardNo': 'card_no',
                    'Name': None,  # 数据库中可能没有name字段
                    'Gender': 'sex',
                    'Major': 'major',
                    'Grade': None,  # 数据库中可能没有grade字段
                    'card_no': 'card_no',
                    'sex': 'sex',
                    'major': 'major',
                    'access_card_no': 'access_card_no'
                }
                
                # 转换排序字段
                db_sort_by = field_mapping.get(sort_by, 'card_no')
                
                # 构建基础查询
                base_query = """SELECT * FROM students WHERE 1=1"""
                count_query = """SELECT COUNT(*) as total FROM students WHERE 1=1"""
                params = []
                
                # 添加搜索条件
                if search:
                    search_condition = """ AND (card_no LIKE %s OR major LIKE %s)"""
                    search_param = f"%{search}%"
                    base_query += search_condition
                    count_query += search_condition
                    params.extend([search_param, search_param])
                
                # 添加排序
                valid_sort_fields = ['card_no', 'sex', 'major', 'access_card_no', 'created_at']
                if db_sort_by in valid_sort_fields:
                    base_query += f" ORDER BY {db_sort_by} {sort_order.upper()}"
                
                # 添加分页
                offset = (page - 1) * per_page
                base_query += " LIMIT %s OFFSET %s"
                params.extend([per_page, offset])
                
                # 执行查询
                cursor.execute(count_query, params[:-2])  # 移除分页参数
                total = cursor.fetchone()['total']
                
                cursor.execute(base_query, params)
                students = cursor.fetchall()
                
                # 转换学生数据，适配前端期望的字段名格式
                formatted_students = []
                for student in students:
                    formatted_student = {
                        'CardNo': student.get('card_no', ''),
                        'Name': f"学生{student.get('card_no', '')[-4:]}",  # 生成默认名字
                        'Gender': student.get('sex', ''),
                        'Major': student.get('major', ''),
                        'Grade': student.get('card_no', '')[:4] if student.get('card_no', '') else '',  # 从学号提取年级
                        'AccessCardNo': student.get('access_card_no', ''),
                        'CreatedAt': student.get('created_at', '')
                    }
                    formatted_students.append(formatted_student)
                
                return {
                    'students': formatted_students,
                    'total': total
                }
        except Exception as e:
            print(f"获取学生列表错误: {str(e)}")
            raise
        finally:
                if connection:
                    connection.close()


class ConsumptionModel:
    @staticmethod
    def get_db_connection():
        """获取数据库连接"""
        return pymysql.connect(
            host='localhost',
            user='root',
            password='123456',  # 使用与create_database.py相同的密码
            database='student_analytics',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    
    @staticmethod
    def get_consumption_records(page=1, per_page=10, card_no='', start_date='', end_date=''):
        """获取消费记录列表"""
        connection = None
        try:
            connection = ConsumptionModel.get_db_connection()
            with connection.cursor() as cursor:
                # 基础查询 - 直接查询消费记录表，不关联学生表
                base_query = """
                SELECT cr.card_no, cr.peo_no, cr.date_time, cr.money, cr.dept 
                FROM consumption_records cr
                WHERE 1=1
                """
                count_query = """
                SELECT COUNT(*) as total 
                FROM consumption_records cr
                WHERE 1=1
                """
                params = []
                
                # 添加筛选条件
                if card_no:
                    condition = """ AND cr.card_no = %s"""
                    base_query += condition
                    count_query += condition
                    params.append(card_no)
                
                if start_date:
                    condition = """ AND DATE(cr.date_time) >= %s"""
                    base_query += condition
                    count_query += condition
                    params.append(start_date)
                
                if end_date:
                    condition = """ AND DATE(cr.date_time) <= %s"""
                    base_query += condition
                    count_query += condition
                    params.append(end_date)
                
                # 添加排序
                base_query += " ORDER BY cr.date_time DESC"
                
                # 添加分页
                offset = (page - 1) * per_page
                base_query += " LIMIT %s OFFSET %s"
                params.extend([per_page, offset])
                
                # 执行查询获取总数
                cursor.execute(count_query, params[:-2])  # 移除分页参数
                total = cursor.fetchone()['total']
                
                # 执行查询获取数据
                cursor.execute(base_query, params)
                records = cursor.fetchall()
                
                # 格式化数据为前端期望的格式
                formatted_records = []
                for record in records:
                    # 确保money字段是数字类型，处理可能的非数字值
                    money_value = record.get('money', 0)
                    try:
                        # 尝试将money转换为浮点数
                        money_value = float(money_value)
                    except (ValueError, TypeError):
                        # 如果转换失败，设置为0
                        money_value = 0
                        
                    formatted_record = {
                        'card_no': record.get('card_no', ''),
                        'peo_no': record.get('peo_no', ''),
                        'date_time': record.get('date_time', ''),
                        'money': money_value,
                        'dept': record.get('dept', '')
                    }
                    formatted_records.append(formatted_record)
                
                return {
                    'records': formatted_records,
                    'total_count': total
                }
        except Exception as e:
            print(f"获取消费记录错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def get_all_card_numbers():
        """获取所有校园卡号"""
        connection = None
        try:
            connection = ConsumptionModel.get_db_connection()
            with connection.cursor() as cursor:
                query = """SELECT DISTINCT card_no FROM consumption_records WHERE card_no != 'card_no' ORDER BY card_no"""
                cursor.execute(query)
                results = cursor.fetchall()
                return [result['card_no'] for result in results]
        except Exception as e:
            print(f"获取校园卡号列表错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def export_consumption_records(card_no='', start_date='', end_date=''):
        """导出消费记录数据为CSV格式"""
        connection = None
        try:
            connection = ConsumptionModel.get_db_connection()
            with connection.cursor() as cursor:
                # 构建查询
                query = """
                SELECT cr.card_no, s.peo_no, cr.date_time, cr.money, cr.dept 
                FROM consumption_records cr
                LEFT JOIN students s ON cr.card_no = s.card_no
                WHERE 1=1
                """
                params = []
                
                # 添加筛选条件
                if card_no:
                    query += """ AND cr.card_no = %s"""
                    params.append(card_no)
                
                if start_date:
                    query += """ AND DATE(cr.date_time) >= %s"""
                    params.append(start_date)
                
                if end_date:
                    query += """ AND DATE(cr.date_time) <= %s"""
                    params.append(end_date)
                
                # 添加排序
                query += " ORDER BY cr.date_time DESC"
                
                # 执行查询
                cursor.execute(query, params)
                records = cursor.fetchall()
                
                # 创建CSV文件
                output = io.StringIO()
                writer = csv.writer(output)
                
                # 写入表头
                writer.writerow(['校园卡号', '校园卡编号', '消费时间', '消费金额', '消费地点'])
                
                # 写入数据
                for record in records:
                    writer.writerow([
                        record.get('card_no', ''),
                        record.get('peo_no', ''),
                        record.get('date_time', ''),
                        record.get('money', 0),
                        record.get('dept', '')
                    ])
                
                # 创建响应
                output.seek(0)
                response = make_response(output.getvalue())
                response.headers['Content-Disposition'] = 'attachment; filename=consumption_records.csv'
                response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'  # 使用UTF-8 BOM以支持Excel
                
                return response
        except Exception as e:
            print(f"导出消费记录错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()()
    
    @staticmethod
    def get_student_by_card_no(card_no):
        """根据学号获取单个学生信息"""
        connection = None
        try:
            connection = AdminModel.get_db_connection()
            with connection.cursor() as cursor:
                query = """SELECT * FROM students WHERE card_no = %s"""
                cursor.execute(query, (card_no,))
                student = cursor.fetchone()
                
                if student:
                    # 格式化为前端期望的字段名格式
                    return {
                        'CardNo': student.get('card_no', ''),
                        'Name': f"学生{student.get('card_no', '')[-4:]}",  # 生成默认名字
                        'Gender': student.get('sex', ''),
                        'Major': student.get('major', ''),
                        'Grade': student.get('card_no', '')[:4] if student.get('card_no', '') else '',  # 从学号提取年级
                        'AccessCardNo': student.get('access_card_no', ''),
                        'CreatedAt': student.get('created_at', '')
                    }
                return None
        except Exception as e:
            print(f"获取学生信息错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def add_student(student_data):
        """添加学生"""
        connection = None
        try:
            connection = AdminModel.get_db_connection()
            
            # 学生密码不再需要（系统不再支持学生登录）
            card_no = student_data.get('card_no', '') or student_data.get('CardNo', '')
            
            with connection.cursor() as cursor:
                # 检查学生是否已存在
                check_query = """SELECT * FROM students WHERE card_no = %s"""
                cursor.execute(check_query, (card_no,))
                if cursor.fetchone():
                    return False
                
                # 插入学生数据（使用实际的表结构字段）
                insert_query = """
                    INSERT INTO students 
                    (card_no, sex, major, access_card_no, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                """
                cursor.execute(insert_query, (
                    card_no,
                    student_data.get('sex', '') or student_data.get('Gender', '') or student_data.get('Sex', ''),
                    student_data.get('major', '') or student_data.get('Major', ''),
                    student_data.get('access_card_no', '') or student_data.get('AccessCardNo', '')
                ))
                
                connection.commit()
                return True
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"添加学生错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def update_student(card_no, update_data):
        """更新学生信息"""
        connection = None
        try:
            connection = AdminModel.get_db_connection()
            
            # 构建更新字段
            update_fields = []
            params = []
            
            # 映射字段名
            field_mapping = {
                'sex': 'sex',
                'gender': 'sex',
                'Gender': 'sex',
                'Sex': 'sex',
                'major': 'major',
                'Major': 'major',
                'access_card_no': 'access_card_no',
                'AccessCardNo': 'access_card_no'
            }
            
            for field, db_field in field_mapping.items():
                if field in update_data:
                    update_fields.append(f"{db_field} = %s")
                    params.append(update_data[field])
            
            # 添加更新时间
            update_fields.append("updated_at = NOW()")
            params.append(card_no)
            
            if not update_fields:
                return True  # 没有更新字段，视为成功
            
            with connection.cursor() as cursor:
                update_query = f"""
                    UPDATE students 
                    SET {', '.join(update_fields)}
                    WHERE card_no = %s
                """
                
                affected_rows = cursor.execute(update_query, params)
                connection.commit()
                
                return affected_rows > 0
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"更新学生信息错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def delete_student(card_no):
        """删除学生"""
        connection = None
        try:
            connection = AdminModel.get_db_connection()
            with connection.cursor() as cursor:
                # 删除学生数据
                delete_query = """DELETE FROM students WHERE card_no = %s"""
                affected_rows = cursor.execute(delete_query, (card_no,))
                connection.commit()
                
                return affected_rows > 0
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"删除学生错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def batch_delete_students(card_numbers):
        """批量删除学生"""
        connection = None
        try:
            connection = AdminModel.get_db_connection()
            with connection.cursor() as cursor:
                # 构建批量删除查询
                placeholders = ','.join(['%s'] * len(card_numbers))
                delete_query = f"""DELETE FROM students WHERE card_no IN ({placeholders})"""
                
                affected_rows = cursor.execute(delete_query, card_numbers)
                connection.commit()
                
                return True, affected_rows
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"批量删除学生错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def reset_student_password(card_no):
        """重置学生密码（重置为学号后6位的MD5）"""
        connection = None
        try:
            connection = AdminModel.get_db_connection()
            
            # 计算新密码
            password_suffix = card_no[-6:] if len(card_no) >= 6 else card_no
            password_md5 = hashlib.md5(password_suffix.encode()).hexdigest()
            
            with connection.cursor() as cursor:
                # 更新密码
                update_query = """
                    UPDATE students 
                    SET password = %s, updated_at = NOW() 
                    WHERE card_no = %s
                """
                affected_rows = cursor.execute(update_query, (password_md5, card_no))
                connection.commit()
                
                return affected_rows > 0
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"重置学生密码错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def import_students_from_csv(file):
        """从CSV文件导入学生数据"""
        success_count = 0
        failed_count = 0
        failed_records = []
        
        # 读取CSV文件
        csv_data = file.read().decode('utf-8-sig')  # 使用utf-8-sig处理BOM
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        connection = None
        try:
            connection = AdminModel.get_db_connection()
            
            for row in csv_reader:
                try:
                    # 验证必需字段
                    if not row.get('CardNo'):
                        failed_count += 1
                        failed_records.append({
                            'record': row,
                            'error': '缺少学号'
                        })
                        continue
                    
                    # 计算密码
                    card_no = row.get('CardNo', '')
                    password_suffix = card_no[-6:] if len(card_no) >= 6 else card_no
                    password_md5 = hashlib.md5(password_suffix.encode()).hexdigest()
                    
                    with connection.cursor() as cursor:
                        # 尝试插入，如果存在则更新
                        insert_query = """
                            INSERT INTO students 
                            (card_no, sex, major, access_card_no, password, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                            ON DUPLICATE KEY UPDATE 
                                sex = VALUES(sex),
                                major = VALUES(major),
                                access_card_no = VALUES(access_card_no),
                                updated_at = NOW()
                        """
                        
                        cursor.execute(insert_query, (
                            card_no,
                            row.get('Sex', ''),
                    row.get('Major', ''),
                    row.get('AccessCardNo', ''),
                    password_md5
                ))
                        
                    success_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    failed_records.append({
                        'record': row,
                        'error': str(e)
                    })
            
            connection.commit()
            
            return {
                'success_count': success_count,
                'failed_count': failed_count,
                'failed_records': failed_records
            }
            
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"导入学生数据错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def export_students_to_csv(search=''):
        """导出学生数据为CSV文件"""
        connection = None
        try:
            connection = AdminModel.get_db_connection()
            
            # 构建查询
            query = """SELECT card_no, sex, major, access_card_no, created_at, updated_at FROM students"""
            params = []
            
            if search:
                query += " WHERE card_no LIKE %s OR major LIKE %s"
                search_param = f"%{search}%"
                params.extend([search_param, search_param])
            
            query += " ORDER BY card_no"
            
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                students = cursor.fetchall()
                
                # 创建CSV数据
                output = io.StringIO()
                fieldnames = ['学号', '性别', '专业', '门禁卡号', '创建时间', '更新时间']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for student in students:
                    writer.writerow({
                    '学号': student['card_no'],
                    '性别': student['sex'],
                    '专业': student['major'],
                    '门禁卡号': student['access_card_no'],
                    '创建时间': student['created_at'],
                    '更新时间': student['updated_at']
                })
                
                # 生成响应内容
                csv_content = output.getvalue()
                output.close()
                
                # 这里只返回CSV内容，由控制器处理响应头
                return csv_content
                
        except Exception as e:
            print(f"导出学生数据错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()