# demo_shop/common.py — 电商业务共享逻辑（UI 与 API 共用，自定义模块）
PRODUCTS = {  # 自定义：内存商品表 SKU -> 商品 dict
    "sku-001": {"sku_id": "sku-001", "name": "测试商品A", "price": 99.00, "stock": 100},  # 自定义
    "sku-002": {"sku_id": "sku-002", "name": "测试商品B", "price": 199.00, "stock": 5},  # 自定义
}

TEST_USERS = {  # 自定义：测试账号邮箱 -> 密码
    "test@demo.com": "123456",  # 自定义：默认 E2E/API 账号
}


def get_cart(session):  # 自定义：从 Flask session 读购物车
    if "cart" not in session:  # 自定义：无 cart 键则初始化
        session["cart"] = {}  # 自定义：空 dict
    return session["cart"]  # 自定义返回


def cart_total(cart):  # 自定义：计算购物车商品小计
    total = 0.0  # 自定义累加器
    for sku_id, qty in cart.items():  # 自定义遍历
        product = PRODUCTS.get(sku_id)  # 自定义查商品
        if product:  # 自定义有效 SKU
            total += product["price"] * qty  # 自定义金额累加
    return round(total, 2)  # 自定义返回两位小数


def shipping_fee(cart_total_amount):  # 自定义：运费规则
    return 0.0 if cart_total_amount >= 200 else 10.0  # 自定义：满 200 包邮


def find_order(session, order_id):  # 自定义：按 order_id 查订单
    for order in session.get("orders", []):  # 自定义遍历 orders 列表
        if order["order_id"] == order_id:  # 自定义匹配
            return order  # 自定义返回
    return None  # 自定义未找到


def build_cart_items(cart):  # 自定义：组装 API/UI 共用购物车行
    items = []  # 自定义列表
    for sku_id, qty in cart.items():  # 自定义
        product = PRODUCTS.get(sku_id)  # 自定义
        if product:  # 自定义
            items.append(  # 自定义 append 行 dict
                {
                    "sku_id": sku_id,  # 自定义字段
                    "name": product["name"],  # 自定义
                    "price": product["price"],  # 自定义：UI 模板兼容字段
                    "unit_price": product["price"],  # 自定义：API 字段
                    "quantity": qty,  # 自定义
                    "line_total": round(product["price"] * qty, 2),  # 自定义小计
                }
            )
    return items  # 自定义返回


def api_response(code=0, message="success", data=None, http_status=200):  # 自定义：统一 API 响应构造
    from flask import jsonify  # 框架调用：延迟导入 jsonify，来源 flask

    body = {"code": code, "message": message, "data": data if data is not None else {}}  # 自定义响应体
    return jsonify(body), http_status  # 框架调用：返回 JSON 响应元组
