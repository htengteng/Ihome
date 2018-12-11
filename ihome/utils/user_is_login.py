from flask import current_app
from flask import g
from flask import session, redirect, url_for
import functools
from functools import wraps

from App.models import User


def is_login(func):
    """
    装饰器用于登录验证
    session['user_id']
    """
    @functools.wraps(func)
    def check_login(*args, **kwargs):
        # 验证登录
        # 获取是否有user_id
        user_session = session.get('user_id')
        user = None
        # 如果有
        if user_session:
            try:
                user = User.query.get(user_session)
            except Exception as e:
                current_app.logger.error(e)
            g.user = user
            return func(*args, **kwargs)
        # 如果验证失败
        else:
            return redirect(url_for('user.login'))
    return check_login
#
# def user_login_data(f):
#     # 使用 functools.wraps 去装饰内层函数，可以保持当前装饰器去装饰的函数的 __name__ 的值不变
#     @functools.wraps(f)
#     def wrapper(*args, **kwargs):
#         user_id = session.get("user_id", None)
#         user = None
#         if user_id:
#             # 尝试查询用户的模型
#             try:
#                 user = User.query.get(user_id)
#             except Exception as e:
#                 current_app.logger.error(e)
#         # 把查询出来的数据赋值给g变量
#         g.user = user
#         return f(*args, **kwargs)
#     return wrapper