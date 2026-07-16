# demo_shop/api_routes.py — REST API 蓝图（自定义，框架 Flask Blueprint）
from flask import Blueprint, request, session  # 框架调用：Blueprint 与请求/session，来源 flask

from demo_shop.common import (  # 自定义导入：共享业务逻辑
    PRODUCTS,  # 自定义：商品表
    TEST_USERS,  # 自定义：账号
    get_cart,  # 自定义：读购物车
    cart_total,  # 自定义：购物车金额
    shipping_fee,  # 自定义：运费
    find_order,  # 自定义：查订单
    build_cart_items,  # 自定义：购物车行
    api_response,  # 自定义：统一响应
)

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")  # 框架调用：创建 API 蓝图，前缀 /api/v1


@api_bp.route("/auth/login", methods=["POST"])  # 框架装饰器：登录接口
def api_login():  # 自定义视图：JSON 登录，写入 session
    payload = request.get_json(silent=True) or {}  # 框架调用：解析 JSON body
    email = payload.get("email", "")  # 自定义：邮箱
    password = payload.get("password", "")  # 自定义：密码
    if TEST_USERS.get(email) != password:  # 自定义：校验
        return api_response(code=1001, message="账号或密码错误", http_status=401)  # 自定义错误响应
    session["user"] = email  # 框架调用：写登录态
    session.modified = True  # 框架调用
    return api_response(data={"email": email})  # 自定义成功


@api_bp.route("/products", methods=["GET"])  # 框架装饰器：商品列表
def api_products():  # 自定义视图
    return api_response(data={"items": list(PRODUCTS.values())})  # 自定义返回全部商品


@api_bp.route("/products/<sku_id>", methods=["GET"])  # 框架装饰器：商品详情
def api_product_detail(sku_id):  # 自定义视图
    product = PRODUCTS.get(sku_id)  # 自定义查商品
    if not product:  # 自定义不存在
        return api_response(code=1002, message="商品不存在", http_status=404)  # 自定义 404
    return api_response(data=product)  # 自定义成功


@api_bp.route("/cart", methods=["GET"])  # 框架装饰器：查询购物车
def api_get_cart():  # 自定义视图
    cart = get_cart(session)  # 自定义调用：读 session 购物车
    items = build_cart_items(cart)  # 自定义调用：组装行
    total = cart_total(cart)  # 自定义调用：小计
    return api_response(data={"items": items, "cart_total": total, "item_count": sum(cart.values())})  # 自定义


@api_bp.route("/cart/items", methods=["POST"])  # 框架装饰器：加购
def api_add_cart_item():  # 自定义视图
    payload = request.get_json(silent=True) or {}  # 框架调用
    sku_id = payload.get("sku_id")  # 自定义
    quantity = int(payload.get("quantity", 1))  # 自定义
    product = PRODUCTS.get(sku_id)  # 自定义
    if not product:  # 自定义
        return api_response(code=1002, message="商品不存在", http_status=400)  # 自定义
    cart = get_cart(session)  # 自定义调用
    current = cart.get(sku_id, 0)  # 自定义当前数量
    if current + quantity > product["stock"]:  # 自定义库存校验
        return api_response(code=1003, message="库存不足", http_status=400)  # 自定义
    cart[sku_id] = current + quantity  # 自定义合并数量
    session["cart"] = cart  # 框架调用
    session.modified = True  # 框架调用
    return api_response(data={"sku_id": sku_id, "quantity": cart[sku_id]})  # 自定义


@api_bp.route("/cart/items/<sku_id>", methods=["PUT"])  # 框架装饰器：更新数量
def api_update_cart_item(sku_id):  # 自定义视图
    payload = request.get_json(silent=True) or {}  # 框架调用
    quantity = int(payload.get("quantity", 0))  # 自定义
    cart = get_cart(session)  # 自定义调用
    if quantity <= 0:  # 自定义：删除
        cart.pop(sku_id, None)  # 自定义 dict 删除
    else:  # 自定义：更新
        product = PRODUCTS.get(sku_id)  # 自定义
        if not product:  # 自定义
            return api_response(code=1002, message="商品不存在", http_status=400)  # 自定义
        if quantity > product["stock"]:  # 自定义超库存
            return api_response(code=1003, message="库存不足", http_status=400)  # 自定义
        cart[sku_id] = quantity  # 自定义写数量
    session["cart"] = cart  # 框架调用
    session.modified = True  # 框架调用
    return api_response(data={"sku_id": sku_id, "quantity": cart.get(sku_id, 0)})  # 自定义


@api_bp.route("/cart/items/<sku_id>", methods=["DELETE"])  # 框架装饰器：删除条目
def api_delete_cart_item(sku_id):  # 自定义视图
    cart = get_cart(session)  # 自定义调用
    cart.pop(sku_id, None)  # 自定义删除
    session["cart"] = cart  # 框架调用
    session.modified = True  # 框架调用
    return api_response(data={"sku_id": sku_id})  # 自定义


@api_bp.route("/cart/clear", methods=["POST"])  # 框架装饰器：清空购物车
def api_clear_cart():  # 自定义视图
    session["cart"] = {}  # 框架调用
    session.modified = True  # 框架调用
    return api_response(data={"cleared": True})  # 自定义


@api_bp.route("/orders/checkout", methods=["POST"])  # 框架装饰器：下单
def api_checkout():  # 自定义视图：创建待支付订单
    cart = get_cart(session)  # 自定义调用
    if not cart:  # 自定义空车
        return api_response(code=1004, message="购物车为空", http_status=400)  # 自定义
    subtotal = cart_total(cart)  # 自定义小计
    shipping = shipping_fee(subtotal)  # 自定义运费
    payable = round(subtotal + shipping, 2)  # 自定义应付
    order_id = f"ORD-{len(session.get('orders', [])) + 1:04d}"  # 自定义订单号
    order = {  # 自定义订单 dict
        "order_id": order_id,  # 自定义
        "status": "PENDING_PAYMENT",  # 自定义状态
        "subtotal": subtotal,  # 自定义
        "shipping": shipping,  # 自定义
        "total": payable,  # 自定义
        "payment_ids": [],  # 自定义：已处理 payment_id，用于幂等
    }
    orders = session.get("orders", [])  # 框架调用
    orders.append(order)  # 自定义追加
    session["orders"] = orders  # 框架调用
    session["current_order"] = order_id  # 框架调用
    session.modified = True  # 框架调用
    return api_response(data=order)  # 自定义返回订单


@api_bp.route("/orders/<order_id>", methods=["GET"])  # 框架装饰器：查订单
def api_get_order(order_id):  # 自定义视图
    order = find_order(session, order_id)  # 自定义调用
    if not order:  # 自定义
        return api_response(code=1005, message="订单不存在", http_status=404)  # 自定义
    return api_response(data=order)  # 自定义


@api_bp.route("/payment/confirm", methods=["POST"])  # 框架装饰器：支付沙箱确认（真实 API，非 mock）
def api_payment_confirm():  # 自定义视图：模拟支付网关回调/确认
    payload = request.get_json(silent=True) or {}  # 框架调用
    order_id = payload.get("order_id")  # 自定义
    action = payload.get("action", "success")  # 自定义 success / cancel
    payment_id = payload.get("payment_id") or f"PAY-{order_id}"  # 自定义支付流水号
    order = find_order(session, order_id)  # 自定义调用
    if not order:  # 自定义
        return api_response(code=1005, message="订单不存在", http_status=404)  # 自定义
    if payment_id in order.get("payment_ids", []):  # 自定义：幂等，同一 payment_id 重复通知
        return api_response(data=order, message="already processed")  # 自定义：已处理仍返回成功
    order.setdefault("payment_ids", []).append(payment_id)  # 自定义：记录 payment_id
    if action == "success":  # 自定义支付成功
        order["status"] = "PAID"  # 自定义更新状态
        session["cart"] = {}  # 框架调用：支付成功清空购物车
    session.modified = True  # 框架调用
    return api_response(data=order)  # 自定义返回最新订单
