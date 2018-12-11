import os
from _operator import and_
from datetime import datetime
from fdfs_client.client import Fdfs_client
from flask import Blueprint, render_template, request, session, jsonify
# from sqlalchemy import all_
from App.models import Area, Facility, House, HouseImage
from utils import status_code
from utils.settings import UPLOAD_DIR
from utils.user_is_login import is_login
from App.models import db

house_blueprint = Blueprint('house', __name__)

def select_sk(sk,houses):
    if sk == "new":
        houses = houses.order_by(db.desc("update_time")).all()
    elif sk == "price-des":
        houses = houses.order_by(db.desc("price")).all()
    elif sk == "price-inc":
        houses = houses.order_by(db.asc("price")).all()
    else:
        houses = houses.order_by(db.desc("capacity")).all()
    return houses

# 查询符合条件的房间3
@house_blueprint.route('/search_house/', methods=['GET'])
def delect_house():
    json_data = request.args
    print(json_data)
    aid = json_data.get('aid',None)
    end = json_data.get('ed',None)
    start = json_data.get('sd',None)
    sk = json_data.get('sk', None)
    houses = None
    print(sk)

    try:
        filters = [House.is_delected == False]
        if end and start:
            begin_date = datetime.strptime(end, '%Y-%m-%d')
            end_date = datetime.strptime(start, '%Y-%m-%d')
            time = int(str(begin_date - end_date)[0])
            filters.append(House.min_days <= time)
            filters.append(time <= House.max_days)
            print(filters)
            print("你好呀")
            houses = House.query.filter(*filters)
            if aid:
                filters.append(House.area_id == int(aid))
                print(filters)
                houses = House.query.filter(*filters)
            if houses:
                houses = select_sk(sk,houses)
            else:
                houses = None
        else:
            houses = House.query.filter(House.is_delected == False)
            if aid:
                houses = House.query.filter(House.is_delected == False,House.area_id == int(aid))
            if houses:
                houses = select_sk(sk, houses)
            else:
                houses = None
    except Exception as e :
        print(e)
    print(houses)
    house_list_all = []
    for house_list in houses:
        house_list_all.append(house_list.to_full_dict())
    data = house_list_all
    print(data)
    return jsonify(code=status_code.ok, data=data)


@house_blueprint.route('/myhouse/', methods=['GET'])
@is_login
def my_house():
    return render_template('myhouse.html')


@house_blueprint.route('/newhouse/', methods=['GET'])
@is_login
def new_house():
    return render_template('newhouse.html')


@house_blueprint.route('/house_info/', methods=['GET'])
@is_login
def house_info():
    areas = Area.query.all()
    facilitys = Facility.query.all()

    areas_list = [area.to_dict() for area in areas]
    facilitys_list = [facility.to_dict() for facility in facilitys]
    return jsonify(code=status_code.ok, areas_list=areas_list, facilitys_list=facilitys_list)


@house_blueprint.route('/newhouseinfo/', methods=['POST'])
@is_login
def new_house_info():
    # 获取前端提交过来的参数
    params = request.form.to_dict()
    # 获取配置设备信息
    facility_ids = request.form.getlist('facility')
    # 创建House对象
    house = House()
    house.user_id = session['user_id']
    house.title = params.get('title')
    house.area_id = params.get('area_id')
    house.price = params.get('price')
    house.address = params.get('address')
    house.room_count = params.get('room_count')
    house.acreage = params.get('acreage')
    house.unit = params.get('unit')
    house.capacity = params.get('capacity')
    house.beds = params.get('beds')
    house.deposit = params.get('deposit')
    house.min_days = params.get('min_days')
    house.max_days = params.get('max_days')

    # 房屋和设施中间表添加信息
    if facility_ids:
        facility_list = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        house.facilities = facility_list
    try:
        house.add_update()
    except:
        db.session.rollback()
        return jsonify(status_code.DATABASE_ERROR)
    return jsonify(code=status_code.ok, house_id=house.id)


@house_blueprint.route('/housing/', methods=['GET'])
@is_login
def my_housing():
    """我的房源信息"""
    houses = None
    try:
        houses = House.query.filter(and_(House.user_id == session['user_id'], House.is_delected == False)).all()
    except Exception as e:
        print(e)
    print(houses)
    house_list = [house.to_dict() for house in houses]
    return jsonify(code=status_code.ok, house_list=house_list)


@house_blueprint.route('/houseimg/', methods=['POST'])
@is_login
def house_image():
    house_id = request.form.get('house_id')
    house_image = request.files.get('house_image').read()

    try:
        client = Fdfs_client('utils/fastdfs/client.conf')
    except Exception  as e:
        print("出现错误%s" % e)
    ret = client.upload_by_buffer(house_image)
    ret_name = ret['Remote file_id']

    # 保存房屋的首图
    house = House.query.get(house_id)
    if not house.index_image_url:
        house.index_image_url = "http://192.168.28.144:8888/" + ret_name

    # 保存房屋图片信息
    h_image = HouseImage()
    h_image.url = "http://192.168.28.144:8888/" + ret_name
    h_image.house_id = house_id
    try:
        h_image.add_update()
    except:
        db.session.rollback()
        return jsonify(status_code.DATABASE_ERROR)
    return jsonify(code=status_code.ok, image_url="http://192.168.28.144:8888/" + ret_name)


@house_blueprint.route('/detail/', methods=['GET'])
def detail():
    """房间详情页"""
    return render_template('detail.html')


@house_blueprint.route('/detail/<int:id>/', methods=['GET'])
@is_login
def house_detail(id):
    """房间详情页接口"""
    house = House.query.get(id)
    house_info = house.to_full_dict()
    # return render_template('detail.html',house = house)
    return jsonify(code=status_code.ok, house_info=house_info)


@house_blueprint.route('/booking/', methods=['GET'])
@is_login
def booking():
    return render_template('booking.html')


@house_blueprint.route('/delected/', methods=['GET'])
@is_login
def deleted_house():
    id = request.args.get('house_id')
    print(id)
    house = House.query.get(id)
    house.is_delected = False
    db.session.commit()
    return render_template('myhouse.html')
