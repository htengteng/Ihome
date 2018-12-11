import os
import re

from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from flask import g
from sqlalchemy import desc

from App.models import User, db, HouseImage, House, Area
from utils import status_code
from utils.settings import UPLOAD_DIR
from utils.user_is_login import is_login
from fdfs_client.client import Fdfs_client

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/create_db/')
# @is_login
def create_database():
    db.create_all()
    return '创建成功'


@user_blueprint.route('/register/', methods=['GET', "POST"])
def register():
    """用户注册"""
    if request.method == "GET":
        return render_template('register.html')
    print("输出数据")
    print(request.json)
    print(request.data)
    print(request.form)
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    # 1.验证数据的完整性
    if not all([mobile, password, password2]):
        return jsonify(status_code.USER_REGISTER_DATA_NOT_NULL)
    # 2.验证手机号码的正确性
    if not re.match(r'^1[34578][0-9]{9}$', mobile):
        return jsonify(status_code.USER_REGISTER_MOBILE_ERROR)

    # 3.验证密码
    if password != password2:
        return jsonify(status_code.USER_REGISTER_PASSWORD_IS_NOT_VALID)

    user = User.query.filter(User.phone == mobile).first()
    if user:
        return jsonify(status_code.USER_REGISTER_MOBILE_EXSTIS)
    else:
        user = User()
        user.phone = mobile
        user.name = mobile
        user.password = password
        user.add_update()
        return jsonify(status_code.SUCCESS)


@user_blueprint.route('/login/', methods=['GET'])
def login():
    return render_template('login.html')


@user_blueprint.route('/login/', methods=['POST'])
def user_login():
    """用户登录"""
    mobile = request.form.get('mobile')
    password = request.form.get('password')

    # 1.验证数据完整性
    if not all([mobile, password]):
        return jsonify(status_code.USER_REGISTER_DATA_NOT_NULL)
    # 2.验证手机正确性
    if not re.match(r'^1[34578][0-9]{9}$', mobile):
        return jsonify(status_code.USER_REGISTER_MOBILE_ERROR)
    # 3. 验证用户是否存在

    user = User.query.filter(User.phone == mobile).first()
    if user:
        if not user.check_pwd(password):
            return jsonify(status_code.USER_LOGIN_PASSWORD_IS_NOT_VALID)
        # 4.验证用户成功
        session['user_id'] = user.id
        print("你好")
        return jsonify(status_code.SUCCESS)
    else:
        print("出现错误")
        return jsonify(status_code.USER_LOGIN_USER_NOT_EXSITS)


@user_blueprint.route('/logout/', methods=['GET'])
def logout():
    session.clear()
    return jsonify(code=status_code.ok)


@user_blueprint.route('/my/', methods=['GET'])
@is_login
def my():
    return render_template('my.html')


@user_blueprint.route('/search/', methods=['GET'])
@is_login
def search():
    house_lists = House.query.filter(House.is_delected==False).order_by(desc("update_time")).all()
    house_area = Area.query.all()
    area_list = []
    for area in house_area:
        area_list.append(area.to_dict())
    house_list_all = []
    for house_list in house_lists:
        house_list_all.append(house_list.to_full_dict())

    print(house_list_all)
    data = {
        "house_list" : house_list_all,
        "area_list" : area_list,
    }
    return render_template('search.html',data = data)


@user_blueprint.route('/profile/', methods=['GET'])
@is_login
def profile():
    user = g.user
    user_name = user.name
    image_url = user.avatar
    return render_template('profile.html', data={'name':user_name,'avatar':image_url})


@user_blueprint.route('/profile/', methods=['PATCH'])
@is_login
def user_profile():
    # 获取文件
    file_content = request.files.get('avatar').read()
    print(file_content)
    # print(type(file), file)
    try:
        client = Fdfs_client('utils/fastdfs/client.conf')
    except Exception  as e:
        print("出现错误%s" % e)
    ret = client.upload_by_buffer(file_content)
    ret_name = ret['Remote file_id']
    # 获取登录用户的信息
    user = User.query.get(session['user_id'])
    # 获取用户的头像地址
    avatar_path = "http://192.168.28.144:8888/"+ret_name
    # 更新头像信息
    user.avatar = avatar_path
    try:
        user.add_update()
    except Exception as e:
        # 如果服务器取不到数据就报数据库错误额异常
        return jsonify(status_code.DATABASE_ERROR)
    return jsonify(code=status_code.ok, image_url="http://192.168.28.144:8888/"+ret_name)


@user_blueprint.route('/profile/name/', methods=['PATCH'])
@is_login
def user_profile_name():
    # 获取修改的用户名
    name = request.form.get('name')
    users = User.query.filter_by(name=name).all()
    if users:
        # 过滤用户名是否存在
        return jsonify(status_code.USER_CHANGE_PORFILE_NAME_IS_INVALID)
    else:
        user = User.query.get(session.get('user_id'))
        user.name = name
        try:
            user.add_update()
        except:
            # 如果出现异常回滚
            db.session.rollback()
            return jsonify(status_code.DATABASE_ERROR)
        return jsonify(code=status_code.ok, name=name)


@user_blueprint.route('/userinfo/')
@is_login
def user_info():
    user = User.query.get(session.get('user_id'))
    return jsonify(code=status_code.ok, data=user.to_basic_dict())


@user_blueprint.route('/auth/', methods=['GET'])
@is_login
def auth():
    return render_template('auth.html')


@user_blueprint.route('/auth/', methods=['PATCH'])
@is_login
def user_auth():
    real_name = request.form.get('real_name')
    id_card = request.form.get('id_card')

    # 判断实名信息是否为空
    if not all([real_name, id_card]):
        return jsonify(status_code.USER_AUTH_DATA_IS_NOT_NULL)
    # 匹配身份证号码
    if not re.match(r'^[1-9]\d{17}$', id_card):
        return jsonify(status_code.USER_AUTH_ID_CARD_IS_NOT_VALID)

    # 获取用户信息并且向数据库中添加值
    user = User.query.get(session['user_id'])
    user.id_name = real_name
    user.id_card = id_card
    try:
        user.add_update()
    except:
        db.session.rollback()
        return jsonify(status_code.DATABASE_ERROR)
    return jsonify(code=status_code.ok)


@user_blueprint.route('/authinfo/', methods=['GET'])
def auth_info():
    user = User.query.get(session['user_id'])
    return jsonify(code=status_code.ok, data=user.to_auth_dict())
