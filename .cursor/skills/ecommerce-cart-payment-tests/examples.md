# 示例索引（UI + 接口双层）

设计新用例时先对照 [SKILL.md](SKILL.md) **测试范围矩阵**，再查下表已实现用例。

## 工程结构

```
demo_shop/
  common.py           # UI/API 共享逻辑
  api_routes.py       # REST /api/v1/*
  app.py              # UI 路由 + 注册蓝图

tests/
  conftest.py         # 全局日志
  clients/shop_api_client.py
  api/
    conftest.py       # api_client fixture
    test_cart_api.py
    test_order_payment_api.py
  e2e/
    conftest.py       # driver、失败截图
    test_cart.py
    test_checkout_payment.py
  pages/              # POM Page Object（UI 强制）
  utils/              # config、wait、popup
```

## POM 示例

```python
# tests/pages/cart_page.py — Page 封装操作
class CartPage(BasePage):
    PATH = "/cart"
    def go_checkout(self):
        by, loc = WaitHelper.by_testid("checkout-btn")
        self.wait.until_clickable(by, loc).click()
        self.wait.until_url_contains("/checkout")

# tests/e2e/test_cart.py — test 只编排 + 断言
def test_xxx(self, driver, log_test_name):
    cart = CartPage(driver)
    cart.open_cart()
    cart.go_checkout()
    assert "/checkout" in driver.current_url
```

完整 POM 规则见 [SKILL.md](SKILL.md) **POM 设计模式** 章节。

## 用例对照表

| ID | 层 | 文件 | 说明 |
|----|-----|------|------|
| API-CART-001~005 | API | test_cart_api.py | 加购/合并/库存/删除/改数量 |
| API-CHK-001~002 | API | test_order_payment_api.py | 下单/空车 |
| API-PAY-001~003 | API | test_order_payment_api.py | 成功/取消/幂等 |
| API-AUTH-001~002 | API | test_order_payment_api.py | 登录 |
| CART-001~004 | UI | test_cart.py | 购物车页面 |
| CHK/PAY/AUTH | UI | test_checkout_payment.py | 结算支付登录 |

## 运行命令

```bash
python run_server.py          # 先启动服务

pytest                        # 全部
pytest -m api                 # 仅接口（无需浏览器）
pytest -m ui                  # 仅 UI
pytest -m "api and payment"   # API 支付
pytest tests/api/test_cart_api.py -v
```

## API 示例

```python
def test_api_add_item_returns_quantity_one(self, api_client, log_api_test):
    data = ShopApiClient.assert_ok(api_client.add_cart_item("sku-001", 1))
    assert data["quantity"] == 1
    cart = ShopApiClient.assert_ok(api_client.get_cart())
    assert cart["item_count"] == 1
```

## UI 示例

```python
@pytest.mark.ui
def test_cart_add_item_shows_badge_count_one(self, driver, log_test_name):
    product = ProductPage(driver)
    product.open_product(Config.DEFAULT_SKU)
    product.add_to_cart(quantity=1)
    assert product.get_badge_count() == "1"
```

## 同一场景双层设计示例

**场景：加购后下单并支付成功**

1. **API 路径（快速回归）**：`add_cart_item` → `checkout` → `payment_confirm` → 断言 `status==PAID`
2. **UI 路径（冒烟）**：商品页加购 → 购物车 → 结算 → 沙箱页点成功 → 断言成功文案

两层互补，不互相替代。

## 扩展指南

| 需求 | 操作 |
|------|------|
| 新 API | `api_routes.py` 加路由 + `ShopApiClient` 加方法 + `tests/api/` 加用例 |
| 新 UI 页 | **先** `tests/pages/xxx_page.py`（POM）→ **再** `tests/e2e/` 加用例 |
| 新 marker | `pytest.ini` 注册 |
