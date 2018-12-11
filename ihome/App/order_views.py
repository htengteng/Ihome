import os
from datetime import datetime

from alipay import AliPay
from flask import Blueprint, session, render_template, request, jsonify
from flask import g

from utils import status_code
from utils.user_is_login import is_login
from App.models import Order, House, User
from utils.app import db
order_blueprint = Blueprint('order', __name__)


@order_blueprint.route('/update_comment/', methods=['POST'])
@is_login
def update_comment():
    order_id = request.form.get('order_id')
    comment = request.form.get('comment')
    order = Order.query.filter(Order.id == order_id).first()
    order.comment = comment
    order.status = 'COMPLETE'
    order.add_update()

    return jsonify(status_code.SUCCESS)


@order_blueprint.route('/update_order/', methods=['POST'])
@is_login
def update_order():
    order_id = request.form.get("order_id")
    action = request.form.get("action")
    order = Order.query.filter(Order.id == order_id).first()
    if action == "accept":
        order.status = "WAIT_COMMENT"
    else:
        order.status = "REJECTED"
    order.add_update()

    return jsonify(status_code.SUCCESS)


@order_blueprint.route('/solve_order/', methods=['GET', 'POST'])
@is_login
def solve_order():
    user = g.user
    houses = House.query.filter(House.user_id == user.id).all()
    print(houses)
    house_id_list = []
    for house in houses:
        house_id_list.append(house.id)
    print(house_id_list)
    orders = []
    for house_id in house_id_list:
        orders.append(Order.query.filter(Order.house_id == house_id).all())
    order_list = []
    user_id_list = []
    for orders_list in orders:
        for order in orders_list:
            order_list.append(order.to_dict())
            user_id_list.append(order.to_dict()['user_id'])
    i = 0
    for user_id in user_id_list:
        user = User.query.filter(User.id == user_id).first()
        order_list[i]['user_name'] = user.name
        i = i + 1

    print(order_list)
    data = {
        "orders": order_list
    }
    # print(data)
    return render_template('lorders.html', data=data)


@order_blueprint.route('/my_order/', methods=['GET', 'POST'])
@is_login
def my_order():
    user = g.user
    orders = Order.query.filter(Order.user_id == user.id,Order.is_delected == False).order_by(db.desc('update_time')).all()
    order_list = []
    order_house_id = []
    for order in orders:
        order_list.append(order.to_dict())
        order_house_id.append(order.to_dict()['house_id'])
    i = 0
    for house_id in order_house_id:
        house = House.query.filter(House.id == house_id).first()
        user_name = house.to_full_dict()['user_name']
        order_list[i]['user_name'] = user_name
        i = i + 1
    print(order_list)
    data = {
        "orders": order_list
    }
    # print("哈哈哈")
    return render_template("orders.html", data=data)


@order_blueprint.route('/create_order', methods=['POST', 'GET'])
@is_login
def create_order():
    if request.method == "POST":
        house_id = request.form.get('house_id')
        # 对前端传过来的时间值进行处理成可以做加法运算的
        print(request.form.get('begin_date'))
        begin_date = datetime.strptime(request.form.get('begin_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        print(begin_date, end_date)
        user_id = session['user_id']

        # 验证是否有填写时间
        if not all([begin_date, end_date]):
            return jsonify(status_code.ORDER_BEGIN_END_DATA_NOT_NULL)
        # 验证初始时间是否大于结束时间
        if begin_date > end_date:
            return jsonify(status_code.ORDER_BEGIN_DATA_GT_END_DATA_ERROE)
        # 获取房屋信息
        try:
            house = House.query.get(house_id)
        except:
            return jsonify(code=status_code.DATABASE_ERROR)
        # 创建订单对象
        order = Order()
        order.house_id = house_id
        order.end_date = end_date
        order.begin_date = begin_date
        order.user_id = user_id
        order.days = (end_date - begin_date).days + 1
        order.house_price = house.price
        order.amount = order.days * order.house_price

        order.add_update()
        data = {
            "order_id": order.id,
            "order_amount": order.amount
        }
        print(data)
        return jsonify(code=status_code.ok, data=data)
    else:
        id = request.args.get('id')
        amount = request.args.get('amount')
        print(id, amount)
        return render_template('order_success.html', data={'id': id, 'amount': amount})


@order_blueprint.route('/payment', methods=['POST', 'GET'])
@is_login
def pay_order():
    id = request.args.get('id')
    amount = request.args.get('amount')
    print(id, amount)
    # 请求支付宝链接
    # 构造支付宝支付链接地址
    alipay_client = AliPay(
        appid="2016092000554429",
        app_notify_url=None,  # 默认回调url
        # app_private_key_path= "/utils/keys/app_private_key.pem",
        # alipay_public_key_path="/utils/keys/alipay_public_key.pem",  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "keys/app_private_key.pem"),
        alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回
        sign_type="RSA2",  # RS 或者 RSA2
        debug=False  # 默认False
    )

    order_string = alipay_client.api_alipay_trade_page_pay(
        out_trade_no=id,
        total_amount=str(amount),
        subject="美多商城%s" % id,
        return_url="http://127.0.0.1:5000/order/pay_success",
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    print(order_string)
    # 拼接支付宝链接网址
    alipay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
    print(alipay_url)
    return jsonify(code=status_code.ok, imageurl=alipay_url)


# 支付成功的界面
@order_blueprint.route('/pay_success', methods=['POST', 'GET'])
@is_login
def pay_success():
    if request.method == 'GET':
        print("get请求")
        return render_template('pay_success.html')
    else:
        sign = request.args.get('sign')
        alipay_req_dcit = {
            'sign_type': request.args.get('sign_type'),
            'app_id': request.args.get('app_id'),
            'method': request.args.get('method'),
            'seller_id': request.args.get('seller_id'),
            'timestamp': request.args.get('timestamp'),
            'version':request.args.get('version'),
            'trade_no':request.args.get('trade_no'),
            'auth_app_id':request.args.get('auth_app_id'),
            'total_amount':request.args.get('total_amount'),
            'out_trade_no':request.args.get("out_trade_no"),
            'charset':request.args.get('charset')
        }
        print(alipay_req_dcit)
        alipay_client = AliPay(
            appid="2016092000554429",
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=False  # 默认False
        )

        # result的结果是true或者false
        result = alipay_client.verify(alipay_req_dcit, sign)
        print(result)
        if result:
            order_id = alipay_req_dcit['out_trade_no']
            trade_id = alipay_req_dcit['trade_no']
            order = Order.query.get(order_id)
            print(order)
            print(trade_id)
            order.trade_id = trade_id
            try:
                db.session.commit()
            except Exception as e:
                print(e)
            return jsonify(code=status_code.ok, trade_id=trade_id)
        else:
            return jsonify(code=status_code.DATABASE_ERROR)
