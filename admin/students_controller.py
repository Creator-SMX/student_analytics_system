from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from admin.models import AdminModel
from auth.auth_controller import admin_required
import json

students_bp = Blueprint('students', __name__, url_prefix='/admin/students')

# 学生管理页面
@students_bp.route('/')
@admin_required
def students_management():
    return render_template('admin_students.html')

# 获取学生列表
@students_bp.route('/list', methods=['GET'])
@admin_required
def get_students():
    try:
        # 从请求参数中获取分页信息
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        # 将前端可能使用的CardNo转换为card_no
        sort_by = request.args.get('sort_by', 'card_no')
        if sort_by == 'CardNo':
            sort_by = 'card_no'
        sort_order = request.args.get('sort_order', 'asc')
        
        # 调用模型获取学生列表
        result = AdminModel.get_students(page, per_page, search, sort_by, sort_order)
        
        return jsonify({
            'success': True,
            'data': result['students'],
            'total': result['total'],
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        print(f"获取学生列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取学生列表失败，请稍后重试'
        })

# 获取单个学生信息
@students_bp.route('/<string:card_no>', methods=['GET'])
@admin_required
def get_student(card_no):
    try:
        student = AdminModel.get_student_by_card_no(card_no)
        if student:
            return jsonify({
                'success': True,
                'data': student
            })
        else:
            return jsonify({
                'success': False,
                'message': '学生不存在'
            })
    except Exception as e:
        print(f"获取学生信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取学生信息失败，请稍后重试'
        })

# 添加学生
@students_bp.route('/', methods=['POST'])
@admin_required
def add_student():
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['card_no', 'sex', 'major']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'{field} 是必填字段'
                })
        
        # 调用模型添加学生
        success = AdminModel.add_student(data)
        
        if success:
            return jsonify({
                'success': True,
                'message': '学生添加成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '学生添加失败，学号可能已存在'
            })
    except Exception as e:
        print(f"添加学生失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'添加学生失败: {str(e)}'
        })

# 更新学生信息
@students_bp.route('/<string:card_no>', methods=['PUT'])
@admin_required
def update_student(card_no):
    try:
        data = request.get_json()
        
        # 确保学号不被修改
        if 'card_no' in data and data['card_no'] != card_no:
            return jsonify({
                'success': False,
                'message': '学号不能修改'
            })
        
        # 调用模型更新学生信息
        success = AdminModel.update_student(card_no, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': '学生信息更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '学生不存在或更新失败'
            })
    except Exception as e:
        print(f"更新学生信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新学生信息失败: {str(e)}'
        })

# 删除学生
@students_bp.route('/<string:card_no>', methods=['DELETE'])
@admin_required
def delete_student(card_no):
    try:
        # 调用模型删除学生
        success = AdminModel.delete_student(card_no)
        
        if success:
            return jsonify({
                'success': True,
                'message': '学生删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '学生不存在或删除失败'
            })
    except Exception as e:
        print(f"删除学生失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除学生失败: {str(e)}'
        })

# 批量删除学生
@students_bp.route('/batch-delete', methods=['POST'])
@admin_required
def batch_delete_students():
    try:
        data = request.get_json()
        card_numbers = data.get('card_numbers', [])
        
        if not card_numbers:
            return jsonify({
                'success': False,
                'message': '请选择要删除的学生'
            })
        
        # 调用模型批量删除学生
        success, deleted_count = AdminModel.batch_delete_students(card_numbers)
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 名学生',
            'deleted_count': deleted_count
        })
    except Exception as e:
        print(f"批量删除学生失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'批量删除学生失败: {str(e)}'
        })

# 学生密码相关功能已移除，系统不再支持学生登录功能

# 导入学生数据（CSV）
@students_bp.route('/import', methods=['POST'])
@admin_required
def import_students():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '请选择要上传的CSV文件'
            })
        
        file = request.files['file']
        
        # 检查文件类型
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'message': '请上传CSV格式的文件'
            })
        
        # 调用模型导入学生数据
        result = AdminModel.import_students_from_csv(file)
        
        return jsonify({
            'success': True,
            'message': f'学生数据导入成功，成功导入 {result["success_count"]} 条，失败 {result["failed_count"]} 条',
            'import_result': result
        })
    except Exception as e:
        print(f"导入学生数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'导入学生数据失败: {str(e)}'
        })

# 导出学生数据
@students_bp.route('/export', methods=['GET'])
@admin_required
def export_students():
    try:
        search = request.args.get('search', '')
        
        # 调用模型导出学生数据
        csv_data = AdminModel.export_students_to_csv(search)
        
        # 设置响应头，返回CSV文件
        return csv_data
    except Exception as e:
        print(f"导出学生数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '导出学生数据失败，请稍后重试'
        })