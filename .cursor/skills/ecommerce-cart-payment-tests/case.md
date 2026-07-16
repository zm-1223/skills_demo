# 测试用例范围、数量、前置与数据

> 本文件为 **用例清单唯一来源**；新增/变更用例时同步更新此处与自动化代码。  
> 设计前对照 [SKILL.md](SKILL.md) **测试范围矩阵**。

## 数量汇总

| 层级 | 模块 | 用例数 | 已实现 |
|------|------|--------|--------|
| API | 购物车 | 5 | 5 |
| API | 结算 | 2 | 2 |
| API | 支付 | 3 | 3 |
| API | 登录 | 2 | 2 |
| **API 小计** | | **12** | **12** |
| UI | 购物车 | 4 | 4 |
| UI | 结算 | 2 | 2 |
| UI | 支付 | 2 | 2 |
| UI | 登录 | 1 | 1 |
| **UI 小计** | | **9** | **9** |
| **合计** | | **21** | **21** |

| 优先级 | API | UI | 合计 |
|--------|-----|-----|------|
| P0 | 8 | 6 | 14 |
| P1 | 4 | 3 | 7 |
| P2 | 0 | 0 | 0 |

---

## 全局前置条件

| 项 | 要求 |
|----|------|
| 环境 | `demo_shop` 已启动：`python run_server.py` |
| Base URL | `http://127.0.0.1:5000`（见 `.env` / `Config.BASE_URL`） |
| API 前缀 | `/api/v1` |
| 浏览器 | Chrome + ChromeDriver（UI 用例，`webdriver-manager` 自动管理） |
| Allure CLI | 生成 HTML 需安装（`scoop install allure`） |

## 全局测试数据

| 字段 | 值 | 说明 |
|------|-----|------|
| TEST_USER | `test@demo.com` | API/UI 登录账号 |
| TEST_PASSWORD | `123456` | 登录密码 |
| DEFAULT_SKU | `sku-001` | 默认加购商品（库存 100，单价 99.00） |
| LOW_STOCK_SKU | `sku-002` | 库存边界商品（库存 5，单价 199.00） |
| 运费规则 | 满 200 包邮，否则 10 元 | 结算断言用 |
| 期望应付（DEFAULT_SKU×1） | 109.00 | 99 + 10 运费 |

## Token / 登录态

| 项 | 规则 |
|----|------|
| API | **session 级复用**：`auth_token` fixture 登录一次，后续 `auth_api_client` 复制 session cookie，**禁止每用例重复 login** |
| UI | 需登录场景用 `LoginPage.login()` 或前置 fixture；与 API token 独立（浏览器 cookie） |

---

## API 用例明细

### 购物车（5）

| ID | 优先级 | 标题 | 前置 | 专用数据 | 文件 |
|----|--------|------|------|----------|------|
| API-CART-001 | P0 | 加购后 cart 数量为 1 | 空购物车 | sku-001, qty=1 | test_cart_api.py |
| API-CART-002 | P0 | 重复加购合并数量 | 空购物车 | sku-001, 1+2=3 | test_cart_api.py |
| API-CART-003 | P1 | 超库存返回 code 1003 | 空购物车 | sku-002, qty=999 | test_cart_api.py |
| API-CART-004 | P0 | 删除后购物车为空 | 已加购 1 件 | sku-001 | test_cart_api.py |
| API-CART-005 | P1 | PUT 更新数量 | 已加购 1 件 | sku-001, qty→4 | test_cart_api.py |

### 结算（2）

| ID | 优先级 | 标题 | 前置 | 专用数据 | 文件 |
|----|--------|------|------|----------|------|
| API-CHK-001 | P0 | 下单 status=PENDING_PAYMENT | 已加购 sku-001×1 | total=109.00 | test_order_payment_api.py |
| API-CHK-002 | P1 | 空车下单 code 1004 | 空购物车 | — | test_order_payment_api.py |

### 支付（3）

| ID | 优先级 | 标题 | 前置 | 专用数据 | 文件 |
|----|--------|------|------|----------|------|
| API-PAY-001 | P0 | 支付成功 → PAID | 待支付订单 | action=success | test_order_payment_api.py |
| API-PAY-002 | P1 | 取消支付保持待支付 | 待支付订单 | action=cancel | test_order_payment_api.py |
| API-PAY-003 | P1 | payment_id 幂等 | 待支付订单 | payment_id 固定 | test_order_payment_api.py |

### 登录（2）

| ID | 优先级 | 标题 | 前置 | 专用数据 | 文件 |
|----|--------|------|------|----------|------|
| API-AUTH-001 | P0 | 登录成功 | 新 session（不复用 token） | 正确账号密码 | test_order_payment_api.py |
| API-AUTH-002 | P1 | 密码错误 401 | 新 session | 错误密码 | test_order_payment_api.py |

---

## UI 用例明细

> UI 用例类统一标记 `@pytest.mark.flaky(reruns=2, reruns_delay=1)` 作为重试机制。

### 购物车（4）

| ID | 优先级 | 标题 | 前置 | 专用数据 | Page |
|----|--------|------|------|----------|------|
| CART-001 | P0 | 加购后角标为 1 | 打开商品页，关 cookie | sku-001, qty=1 | ProductPage |
| CART-002 | P0 | 重复加购角标累加 | 同上 | 加购两次 | ProductPage |
| CART-003 | P1 | 购物车页改数量 | 已加购 1 件 | qty→3 | CartPage |
| CART-004 | P0 | 删除后空车 | 已加购 1 件 | sku-001 | CartPage |

### 结算（2）

| ID | 优先级 | 标题 | 前置 | 专用数据 | Page |
|----|--------|------|------|----------|------|
| CHK-001 | P0 | 结算应付含运费 | 已加购 sku-001×1 | 109.00 | CheckoutPage |
| CHK-002 | P1 | 价格变动弹窗后支付 | 已加购，`?price_change=1` | — | CheckoutPage |

### 支付（2）

| ID | 优先级 | 标题 | 前置 | 专用数据 | Page |
|----|--------|------|------|----------|------|
| PAY-001 | P0 | 全流程支付成功 | 已提交订单 | 沙箱点成功 | PaymentPage |
| PAY-002 | P1 | 取消支付失败页 | 已提交订单 | 沙箱点取消 | PaymentPage |

### 登录（1）

| ID | 优先级 | 标题 | 前置 | 专用数据 | Page |
|----|--------|------|------|----------|------|
| AUTH-001 | P0 | 登录成功 | 未登录 | test@demo.com | LoginPage |

---

## 扩展用例时

1. 在本文件增加行并更新 **数量汇总**
2. 在 `tests/api/` 或 `tests/e2e/` 实现
3. 更新 [SKILL.md](SKILL.md) **用例 ID 对照**（若需要）
