from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from auth.auth_controller import admin_required
from admin.models import ConsumptionModel

consumption_bp = Blueprint('consumption', __name__, url_prefix='/admin/consumption')

# 消费记录页面
@consumption_bp.route('/')
@admin_required
def consumption_management():
    return render_template('admin_consumption.html')

# 获取消费记录列表
@consumption_bp.route('/list', methods=['GET'])
@admin_required
def get_consumption_records():
    try:
        # 从请求参数中获取分页和筛选信息
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        card_no = request.args.get('card_no', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # 调用模型获取消费记录列表
        result = ConsumptionModel.get_consumption_records(page, per_page, card_no, start_date, end_date)
        
        # 计算总页数
        total_pages = (result['total_count'] + per_page - 1) // per_page
        
        return jsonify({
            'success': True,
            'data': result['records'],
            'total_count': result['total_count'],
            'page': page,
            'total_pages': total_pages
        })
    except Exception as e:
        print(f"获取消费记录列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取消费记录列表失败，请稍后重试'
        })

# 获取所有校园卡号（用于下拉框）
@consumption_bp.route('/card-numbers', methods=['GET'])
@admin_required
def get_card_numbers():
    try:
        card_numbers = ConsumptionModel.get_all_card_numbers()
        return jsonify({
            'success': True,
            'card_numbers': card_numbers
        })
    except Exception as e:
        print(f"获取校园卡号列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取校园卡号列表失败，请稍后重试'
        })

# 导出消费记录数据
@consumption_bp.route('/export', methods=['GET'])
@admin_required
def export_consumption_records():
    try:
        card_no = request.args.get('card_no', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        # 调用模型导出数据
        csv_data = ConsumptionModel.export_consumption_records(card_no=card_no, start_date=start_date, end_date=end_date)
        
        # 返回CSV数据
        return csv_data
    except Exception as e:
        print(f"导出消费记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '导出消费记录失败，请稍后重试'
        })