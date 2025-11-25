from flask import Blueprint, request, jsonify, session, redirect, url_for
from .models import verify_admin

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """管理员登录接口"""
    try:
        data = request.get_json()
        
        if not data:
            # 如果不是JSON请求，尝试从表单获取数据
            username = request.form.get('username')
            password = request.form.get('password')
        else:
            username = data.get('username')
            password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        # 只支持管理员登录
        admin = verify_admin(username, password)
        if admin:
            session['user_id'] = admin['id']
            session['username'] = admin['username']
            session['user_type'] = 'admin'
            return jsonify({'success': True, 'message': '管理员登录成功', 'user_type': 'admin'})
        else:
            return jsonify({'success': False, 'message': '管理员账号或密码错误'}), 401
    except Exception as e:
        # 添加详细错误日志以便诊断
        import traceback
        print(f"登录过程中的详细错误:")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出接口"""
    try:
        # 清除会话
        session.clear()
        return jsonify({'success': True, 'message': '登出成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': '登出失败'}), 500

@auth_bp.route('/check_login', methods=['GET'])
def check_login():
    """检查用户是否已登录"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user_id': session['user_id'],
            'username': session['username'],
            'user_type': session['user_type']
        })
    else:
        return jsonify({'logged_in': False})

def login_required(f):
    """登录装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function