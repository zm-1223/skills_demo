# 示例

## 示例 1：用例清单（文档输出）

用户请求：「帮我列购物车 API 测试用例」

| ID | 优先级 | 模块 | 标题 | 类型 |
|----|--------|------|------|------|
| CART-001 | P0 | 购物车 | 加购单个 SKU 后购物车数量为 1 | API |
| CART-002 | P0 | 购物车 | 同 SKU 再次加购合并数量 | API |
| CART-003 | P1 | 购物车 | 加购数量超过库存返回明确错误 | API |
| CART-004 | P1 | 购物车 | 删除商品后购物车为空 | API |
| CHK-001 | P0 | 结算 | 无券结算金额等于商品小计加固运费 | API |
| PAY-001 | P0 | 支付 | 模拟支付成功回调后订单变为已支付 | API |

---

## 示例 2：pytest API 自动化（参考结构）

适配项目时替换 URL、字段名与 auth 方式。

```python
import pytest


@pytest.mark.parametrize("quantity", [1, 2])
def test_cart_add_item(api_client, product_in_stock, quantity):
    sku_id = product_in_stock["skuId"]

    resp = api_client.post("/api/cart/items", json={"skuId": sku_id, "quantity": quantity})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0

    cart = api_client.get("/api/cart").json()["data"]
    item = next(i for i in cart["items"] if i["skuId"] == sku_id)
    assert item["quantity"] == quantity


def test_checkout_creates_pending_order(api_client, cart_with_one_item, default_address):
    resp = api_client.post(
        "/api/orders/checkout",
        json={"addressId": default_address["id"], "couponId": None},
    )
    assert resp.status_code == 200
    order = resp.json()["data"]
    assert order["status"] == "PENDING_PAYMENT"
    assert order["totalAmount"] == cart_with_one_item["expectedTotal"]


def test_payment_notify_idempotent(api_client, pending_order, payment_sandbox):
    payment_id = payment_sandbox.create_payment(pending_order["orderNo"])

    for _ in range(2):
        notify_resp = api_client.post(
            "/api/payment/notify",
            json=payment_sandbox.build_success_payload(payment_id),
        )
        assert notify_resp.status_code == 200

    order = api_client.get(f"/api/orders/{pending_order['orderNo']}").json()["data"]
    assert order["status"] == "PAID"
```

---

## 示例 3：Playwright E2E 冒烟（参考结构）

```python
def test_guest_checkout_happy_path(page, base_url, test_product_url):
    page.goto(test_product_url)
    page.get_by_test_id("add-to-cart-btn").click()
    page.get_by_test_id("cart-badge-count").wait_for()
    assert page.get_by_test_id("cart-badge-count").inner_text() == "1"

    page.get_by_test_id("checkout-btn").click()
    page.get_by_test_id("submit-order-btn").click()

    page.get_by_test_id("pay-confirm-btn").click()
    page.get_by_text("支付成功").wait_for(timeout=15000)
```

---

## 示例 4：支付 mock 回调

当无法调用真实网关时，直接 POST 回调接口：

```python
def simulate_payment_success(api_client, order_no, amount_cents):
    payload = {
        "orderNo": order_no,
        "paymentId": f"test_pay_{order_no}",
        "amount": amount_cents,
        "status": "SUCCESS",
        "sign": "mock_sign_in_test_env",
    }
    return api_client.post("/api/payment/notify", json=payload)
```

---

## 示例 5：用户对话 → Agent 行为

| 用户说 | Agent 应做 |
|--------|------------|
| 「写购物车测试用例」 | 输出用例清单表格，覆盖加购/改数量/删/库存边界 |
| 「实现支付自动化」 | 查项目框架 → API 测试 + mock 回调 → 说明 env 变量 |
| 「E2E 从加购到支付」 | 1 条 P0 冒烟 + 依赖 testid；复杂断言放 API 层 |
| 「并发加购怎么测」 | 用例 + threading/async 示例 + 断言最终库存与数量 |
