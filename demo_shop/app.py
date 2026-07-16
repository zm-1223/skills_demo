# demo_shop/app.py — Flask 演示电商站点（UI 路由 + API 蓝图注册）
from flask import Flask, render_template, request, redirect, url_for, session  # 框架调用：Flask 核心，来源 flask

from demo_shop.common import (  # 自定义导入：UI/API 共享业务
    PRODUCTS,  # 自定义：商品表
    TEST_USERS,  # 自定义：测试账号
    get_cart,  # 自定义：读购物车（原 _get_cart）
    cart_total,  # 自定义：购物车金额（原 _cart_total）
    shipping_fee,  # 自定义：运费
    find_order,  # 自定义：查订单（原 _find_order）
    build_cart_items,  # 自定义：购物车行
)
from demo_shop.api_routes import api_bp  # 自定义导入：REST API 蓝图

app = Flask(__name__)  # 框架调用：创建 Flask 应用
app.secret_key = "demo-shop-secret-key-for-session"  # 自定义：session 密钥
app.register_blueprint(api_bp)  # 框架调用：注册 /api/v1/* 蓝图


@app.route("/")  # 框架装饰器：首页商品列表
def index():  # 自定义 UI 视图
    return render_template("index.html", products=PRODUCTS.values())  # 框架调用：渲染模板


@app.route("/login", methods=["GET", "POST"])  # 框架装饰器：登录页
def login():  # 自定义 UI 登录
    if request.method == "POST":  # 框架调用
        email = request.form.get("email", "")  # 框架调用
        password = request.form.get("password", "")  # 框架调用
        if TEST_USERS.get(email) == password:  # 自定义校验
            session["user"] = email  # 框架调用
            return redirect(url_for("index"))  # 框架调用
        return render_template("login.html", error="账号或密码错误")  # 框架调用
    return render_template("login.html", error=None)  # 框架调用


@app.route("/product/<sku_id>")  # 框架装饰器：商品详情页
def product_detail(sku_id):  # 自定义 UI 视图
    product = PRODUCTS.get(sku_id)  # 自定义查商品
    if not product:  # 自定义
        return "商品不存在", 404  # 自定义 404
    return render_template("product.html", product=product)  # 框架调用


@app.route("/cart/add", methods=["POST"])  # 框架装饰器：UI 表单加购
def cart_add():  # 自定义 UI 加购（与 API 共用 session 购物车）
    sku_id = request.form.get("sku_id")  # 框架调用
    quantity = int(request.form.get("quantity", 1))  # 自定义
    product = PRODUCTS.get(sku_id)  # 自定义
    if not product:  # 自定义
        return "商品不存在", 400  # 自定义
    cart = get_cart(session)  # 自定义调用
    current = cart.get(sku_id, 0)  # 自定义
    if current + quantity > product["stock"]:  # 自定义库存
        return "库存不足", 400  # 自定义
    cart[sku_id] = current + quantity  # 自定义
    session["cart"] = cart  # 框架调用
    session.modified = True  # 框架调用
    return redirect(url_for("product_detail", sku_id=sku_id, added=1))  # 框架调用


@app.route("/cart")  # 框架装饰器：购物车页
def cart_view():  # 自定义 UI 视图
    cart = get_cart(session)  # 自定义调用
    items = build_cart_items(cart)  # 自定义调用：与 API 一致的数据结构
    return render_template("cart.html", items=items, cart_total=cart_total(cart))  # 框架调用


@app.route("/cart/update", methods=["POST"])  # 框架装饰器：UI 更新数量
def cart_update():  # 自定义 UI 视图
    sku_id = request.form.get("sku_id")  # 框架调用
    quantity = int(request.form.get("quantity", 0))  # 自定义
    cart = get_cart(session)  # 自定义调用
    if quantity <= 0:  # 自定义删除
        cart.pop(sku_id, None)  # 自定义
    else:  # 自定义更新
        product = PRODUCTS.get(sku_id)  # 自定义
        if product and quantity <= product["stock"]:  # 自定义
            cart[sku_id] = quantity  # 自定义
    session["cart"] = cart  # 框架调用
    session.modified = True  # 框架调用
    return redirect(url_for("cart_view"))  # 框架调用


@app.route("/checkout", methods=["GET", "POST"])  # 框架装饰器：结算页
def checkout():  # 自定义 UI 结算
    cart = get_cart(session)  # 自定义调用
    if not cart:  # 自定义
        return redirect(url_for("cart_view"))  # 框架调用
    items = build_cart_items(cart)  # 自定义调用
    subtotal = cart_total(cart)  # 自定义调用
    shipping = shipping_fee(subtotal)  # 自定义调用
    payable = round(subtotal + shipping, 2)  # 自定义应付
    if request.method == "POST":  # 自定义提交订单
        need_price_confirm = request.args.get("price_change") == "1"  # 自定义弹窗场景
        if need_price_confirm and request.form.get("confirm_price_change") != "1":  # 自定义
            return render_template(  # 框架调用
                "checkout.html",
                items=items,
                cart_total=subtotal,
                shipping=shipping,
                payable=payable,
                show_price_change_dialog=True,
                price_change_mode=True,
            )
        order_id = f"ORD-{len(session.get('orders', [])) + 1:04d}"  # 自定义订单号
        orders = session.get("orders", [])  # 框架调用
        orders.append(  # 自定义追加订单
            {
                "order_id": order_id,
                "total": payable,
                "status": "PENDING_PAYMENT",
                "subtotal": subtotal,
                "shipping": shipping,
                "payment_ids": [],
            }
        )
        session["orders"] = orders  # 框架调用
        session["current_order"] = order_id  # 框架调用
        session.modified = True  # 框架调用
        return redirect(url_for("payment_sandbox", order_id=order_id))  # 框架调用
    return render_template(  # 框架调用 GET
        "checkout.html",
        items=items,
        cart_total=subtotal,
        shipping=shipping,
        payable=payable,
        show_price_change_dialog=False,
        price_change_mode=False,
    )


@app.route("/cookie/accept", methods=["POST"])  # 框架装饰器
def accept_cookie():  # 自定义
    session["cookie_accepted"] = True  # 框架调用
    session.modified = True  # 框架调用
    return redirect(request.referrer or url_for("index"))  # 框架调用


@app.route("/payment/<order_id>")  # 框架装饰器：UI 支付沙箱页
def payment_sandbox(order_id):  # 自定义
    order = find_order(session, order_id)  # 自定义调用
    if not order:  # 自定义
        return "订单不存在", 404  # 自定义
    return render_template("payment_sandbox.html", order_id=order_id, amount=order["total"])  # 框架调用


@app.route("/payment/confirm/<order_id>", methods=["POST"])  # 框架装饰器：UI 沙箱确认
def payment_confirm(order_id):  # 自定义 UI 支付（与 API 逻辑对齐）
    action = request.form.get("action")  # 框架调用
    order = find_order(session, order_id)  # 自定义调用
    if not order:  # 自定义
        return "订单不存在", 404  # 自定义
    if action == "success":  # 自定义
        order["status"] = "PAID"  # 自定义
        session["cart"] = {}  # 框架调用
    session.modified = True  # 框架调用
    if action == "success":  # 自定义
        return redirect(url_for("payment_success", order_id=order_id))  # 框架调用
    return redirect(url_for("payment_fail", order_id=order_id))  # 框架调用


@app.route("/payment/success/<order_id>")  # 框架装饰器
def payment_success(order_id):  # 自定义
    return render_template("payment_success.html", order_id=order_id)  # 框架调用


@app.route("/payment/fail/<order_id>")  # 框架装饰器
def payment_fail(order_id):  # 自定义
    return render_template("payment_fail.html", order_id=order_id)  # 框架调用


@app.context_processor  # 框架装饰器：模板全局变量
def inject_cart_count():  # 自定义
    cart = session.get("cart", {})  # 框架调用
    return {"cart_count": sum(cart.values())}  # 自定义角标


if __name__ == "__main__":  # 自定义入口
    app.run(host="127.0.0.1", port=5000, debug=True)  # 框架调用
