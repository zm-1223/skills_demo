---
name: ecommerce-cart-payment-tests
description: >-
  电商购物车、结算、支付的 UI + 接口双层自动化测试（pytest + Selenium + requests）。
  含可运行 demo_shop、REST API、E2E 与 API 用例，POM、重试机制、等待策略、日志、HTML 报告与失败截图。
  Use when the user mentions e-commerce cart, checkout, payment, pytest, selenium, POM, retry, flaky,
  购物车, 结算, 支付, UI自动化, 接口测试, E2E.
---

# 电商购物车与支付自动化（UI + 接口）

## 双层测试策略

| 层级 | 工具 | 目录 | 职责 |
|------|------|------|------|
| **接口** | pytest + requests | `tests/api/` | 业务逻辑、契约、幂等、边界、快速回归 |
| **UI** | pytest + Selenium | `tests/e2e/` | 用户路径、页面展示、弹窗、沙箱支付页 |

**本 Skill 范围外（不做）：** 性能测试、压力测试、负载测试、benchmark、并发压测——仅做 **功能** 层面的 UI + 接口测试。

原则：**接口覆盖核心逻辑，UI 覆盖关键路径**；同一业务场景可分别有 API-* 与 UI-* 用例 ID。

## 测试范围矩阵

设计用例前先对照本矩阵，确保 **必测场景** 有覆盖；**常见边界** 优先 API，关键路径补 UI。

| 模块 | 必测场景 | 常见边界 | API | UI |
|------|----------|----------|-----|-----|
| 购物车 | 加购、同 SKU 合并、改数量、删商品、清空、查询 | 库存不足、下架、限购、失效 SKU | ✓ 必做 | ✓ 主路径 |
| 结算 | 金额/运费计算、优惠券/积分、提交订单、生成 orderNo | 券过期、门槛不满足、地址不可达、价格变动 | ✓ 必做 | ✓ 展示+弹窗 |
| 支付 | 发起支付、成功、失败/取消、超时、重复点击 | 幂等回调、回调乱序、沙箱跳转失败 | ✓ 必做 | ✓ 沙箱页 |
| 订单 | 状态流转、订单详情、取消/关单规则 | 支付中取消、待支付超时、重复支付 | ✓ 必做 | ✓ 结果页 |
| 登录 | 正确/错误凭证、登录态保持 | 未登录访问结算、session 过期 | ✓ 必做 | ✓ 可选 |

**分层原则：**

- **API**：金额计算、库存校验、状态机、错误码、幂等——全部在接口层断言
- **UI**：页面跳转、角标/toast、弹窗交互、沙箱支付页操作——不重复验证复杂计算逻辑

## 购物车测试清单

```
- [ ] 空购物车（API: item_count=0 / UI: 空车文案）
- [ ] 单 SKU 加购 quantity=1
- [ ] 同 SKU 重复加购（数量合并）
- [ ] 修改数量（合法 / 超库存 / 低于最小起购）
- [ ] 删除单个商品
- [ ] 批量删除 / 清空购物车
- [ ] 下架或失效 SKU（API: code 错误 / UI: 不可结算提示）
- [ ] 登录前后游客购物车合并（按业务规则）
- [ ] 购物车金额汇总（API: cart_total / UI: 合计文案）
```

## 结算测试清单

```
- [ ] 默认地址与运费（API: shipping 字段 / UI: 运费展示）
- [ ] 切换地址导致运费变化
- [ ] 可用优惠券抵扣
- [ ] 不可用优惠券（过期、未达门槛、品类限制）
- [ ] 积分抵扣上限
- [ ] 结算页价格与购物车一致
- [ ] 提交订单后 status=PENDING_PAYMENT（API）/ 跳转支付页（UI）
- [ ] 价格变动确认弹窗（UI 按需局部等待）
```

## 支付测试清单

```
- [ ] 创建/绑定支付单（orderNo、金额一致）
- [ ] 支付成功 → 订单 PAID（API）/ 成功页文案（UI）
- [ ] 支付失败或取消 → 保持待支付 + 可重试
- [ ] 重复 payment_id 回调幂等（API 必做）
- [ ] 支付超时 / 用户取消
- [ ] 跳转真实沙箱页并完成操作（UI）
- [ ] 0 元单 / 纯积分单（若业务支持）
```

## 订单测试清单

```
- [ ] 下单生成唯一 orderNo
- [ ] 状态：PENDING_PAYMENT → PAID → （发货 → 完成）
- [ ] 取消/关单后不可重复支付（按业务规则）
- [ ] GET 订单详情字段完整（API）
- [ ] 订单页/成功页状态展示（UI）
```

## 可运行工程

```
skills_demo/
├── demo_shop/
│   ├── app.py              # UI 路由
│   ├── api_routes.py       # REST /api/v1/*
│   └── common.py           # UI/API 共享业务
├── tests/
│   ├── conftest.py         # 全局日志
│   ├── api/                # 接口测试
│   ├── e2e/                # UI 测试
│   ├── clients/            # ShopApiClient
│   ├── pages/              # Page Object
│   └── utils/
├── pytest.ini
├── requirements.txt
└── run_server.py
```

## 运行步骤

**终端 1 — 启动站点（UI + API 共用）：**

```bash
pip install -r requirements.txt
python run_server.py
```

**终端 2 — 运行测试：**

```bash
pytest                  # UI + API 全部
pytest -m api           # 仅接口
pytest -m ui            # 仅 UI
pytest -m "api and cart"  # 接口购物车
pytest tests/api/       # 指定目录
pytest tests/e2e/       # 指定目录
```

**产出物：**

| 产出 | 路径 | 适用 |
|------|------|------|
| HTML 报告 | `reports/report.html` | UI + API |
| 日志 | `logs/test_*.log` | UI + API |
| 失败截图 | `reports/screenshots/` | 仅 UI 失败 |

## REST API 清单（demo_shop）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 登录，session cookie |
| GET | `/api/v1/products` | 商品列表 |
| GET | `/api/v1/products/{sku}` | 商品详情 |
| GET | `/api/v1/cart` | 查询购物车 |
| POST | `/api/v1/cart/items` | 加购 `{"sku_id","quantity"}` |
| PUT | `/api/v1/cart/items/{sku}` | 改数量 |
| DELETE | `/api/v1/cart/items/{sku}` | 删除 |
| POST | `/api/v1/cart/clear` | 清空 |
| POST | `/api/v1/orders/checkout` | 下单 |
| GET | `/api/v1/orders/{id}` | 查订单 |
| POST | `/api/v1/payment/confirm` | 支付沙箱确认（真实 API） |

响应格式：`{"code": 0, "message": "success", "data": {...}}`

## Agent 工作流程

1. **复用本仓库结构** — `tests/api/` + `tests/e2e/` + `tests/clients/`
2. **先判断层级** — 逻辑/契约 → API；页面/交互 → UI；关键场景 → 两层各一条
3. **真实环境** — 连 demo_shop 或测试/预发 URL；禁止 mock 接口
4. **接口** — `ShopApiClient` + session 隔离 + 断言 HTTP + `code` + `data`
5. **UI** — **POM 强制** + 显式/隐性等待 + 按需弹窗 + 失败截图 + 偶发 flaky 时用例级重试

## 接口测试规范

### 命名

`test_api_<模块>_<场景>_<预期>`

### 断言顺序

1. HTTP status
2. 业务 `body["code"]`
3. `body["data"]` 字段值

### Client 用法

```python
data = ShopApiClient.assert_ok(api_client.add_cart_item("sku-001", 1))
cart = ShopApiClient.assert_ok(api_client.get_cart())
assert cart["item_count"] == 1
```

### 隔离

- 每用例独立 `requests.Session`（`api_client` fixture）
- `setup/teardown` 调用 `clear_cart()`

### 文件布局

- 购物车 API → `tests/api/test_cart_api.py`
- 结算/支付/登录 API → `tests/api/test_order_payment_api.py`
- Client → `tests/clients/shop_api_client.py`

## POM 设计模式（UI 强制）

所有 UI/E2E 测试 **必须** 采用 **Page Object Model（POM）**：页面元素与操作封装在 Page 类，测试用例只编排业务流程与断言。

### 目录与继承

```
tests/pages/
├── base_page.py       # 基类：driver、wait、open、通用定位
├── product_page.py    # 一页面/File
├── cart_page.py
├── checkout_page.py
├── payment_page.py
└── login_page.py
```

- 每个 Page **继承** `BasePage`
- **一个页面（或紧密相关的一组视图）对应一个 Page 类、一个 `.py` 文件**
- 类名：`XxxPage`；文件名：`xxx_page.py`（小写蛇形）

### 职责划分

| 层级 | 目录 | 职责 | 禁止 |
|------|------|------|------|
| **Page** | `tests/pages/` | 定位器、页面操作、显式等待、步骤日志 | 业务断言、跨页面流程编排 |
| **Test** | `tests/e2e/` | 调用 Page 方法、组织场景、assert 结果 | 直接 `driver.find_element`、硬编码 locator |
| **Helper** | `tests/utils/` | 跨页通用能力（WaitHelper、PopupHelper） | 页面特有业务操作 |
| **Client** | `tests/clients/` | API 封装（接口层，非 POM） | UI 定位与操作 |

### Page 类编写规则

1. **定位器内聚**：所有 `data-testid` / CSS / XPath 只在 Page 内出现，不泄露到 `test_*.py`
2. **方法语义化**：方法名用业务动词，如 `add_to_cart()`、`go_checkout()`，不用 `click_btn_1()`
3. **操作自带等待**：点击/输入前在 Page 方法内做显式等待（通过 `self.wait`），测试层不再重复等待
4. **弹窗在步骤后处理**：在触发弹窗的 Page 方法末尾调用 `PopupHelper`（按需局部），不在 test 或 conftest 全局处理
5. **返回值**：需要断言时返回文本/状态（如 `get_badge_count()`），由 **test 层 assert**
6. **日志**：每个公开操作方法写 `logger.info`，便于与 `logs/` 对照
7. **PATH 常量**：固定路由可定义 `PATH = "/cart"`，用 `self.open(self.PATH)` 导航

### 测试层编写规则

```python
# ✅ 正确：test 只编排 Page + 断言
def test_cart_add_item_shows_badge_count_one(self, driver, log_test_name):
    product = ProductPage(driver)
    product.open_product(Config.DEFAULT_SKU)
    product.add_to_cart(quantity=1)
    assert product.get_badge_count() == "1"

# ❌ 错误：locator 与 WebDriver 操作写在 test 里
def test_bad(self, driver):
    driver.find_element(By.CSS_SELECTOR, "[data-testid='add-to-cart-btn']").click()
```

- 一个 test 方法 = 一个业务场景；可组合多个 Page，但 **不跨 3 个以上页面仍不写 Page 方法**
- 需要登录前置时，用 `LoginPage(driver).login(...)` 或 fixture 封装，不在 test 内填表

### 本仓库 Page 映射

| Page 类 | 文件 | 对应页面 |
|---------|------|----------|
| `ProductPage` | `product_page.py` | 商品详情 |
| `CartPage` | `cart_page.py` | 购物车 |
| `CheckoutPage` | `checkout_page.py` | 结算 |
| `PaymentPage` | `payment_page.py` | 支付沙箱 / 成功 / 失败 |
| `LoginPage` | `login_page.py` | 登录 |

新增页面时：**先建 Page → 再写 test**，顺序不可颠倒。

### POM 反模式

- 在 `tests/e2e/test_*.py` 中出现 `By.`、`find_element`、`WebDriverWait`
- 同一 locator 在多个 Page/test 重复定义
- Page 方法内写 `assert`（除「等待即断言」的显式等待外）
- 一个 Page 类超过 ~150 行不拆分（按 Tab/区域拆 `CheckoutPage`、`PaymentPage`）
- 用 Page 类做 API 请求（API 用 `ShopApiClient`）

## UI 测试规范

### 命名

`test_<模块>_<场景>_<预期>`

### 等待（强制）

- 禁止 `time.sleep()`
- 隐性：`driver.implicitly_wait(5)` 在 fixture 设一次
- 显式：`WebDriverWait` + `EC` 在 `WaitHelper`/Page 内

### 弹窗（按需局部）

- 商品页：`PopupHelper.dismiss_cookie_if_present()`
- 提交订单后：`confirm_price_change_if_present()`
- **禁止** conftest 全局扫弹窗

### 文件布局

- UI 购物车 → `tests/e2e/test_cart.py`（只调 `ProductPage` / `CartPage`）
- UI 结算/支付 → `tests/e2e/test_checkout_payment.py`（只调各 Page）
- Page → `tests/pages/`（见 **POM 设计模式**）

## 重试机制

用于缓解 **环境偶发不稳定**（浏览器渲染、网络抖动、第三方支付页加载慢），**不能**用来掩盖业务缺陷或稳定失败的断言。

### 适用 / 不适用

| 适用 | 不适用 |
|------|--------|
| UI 元素偶发未就绪（已用显式等待仍偶发） | API 返回固定 4xx/5xx 或业务 code 错误 |
| 沙箱支付页偶发加载超时 | 断言逻辑写错、测试数据错误 |
| 本地/CI 环境 flaky | 每次必现的失败 |

**顺序：** 先加强 **显式等待 / POM 稳定性** → 仍 flaky 再加 **用例级重试** → 禁止一上来全局盲目重试。

### 工具与配置

默认使用 **pytest-rerunfailures**：

```bash
# UI 偶发失败时（最多跑 3 次：1 + 2 次重试）
pytest -m ui --reruns 2 --reruns-delay 1

# 仅重试指定用例
pytest tests/e2e/test_cart.py::TestCart::test_cart_add_item_shows_badge_count_one --reruns 2
```

| 配置 | 推荐值 | 说明 |
|------|--------|------|
| `--reruns` | `2` | 失败后最多再跑 2 次 |
| `--reruns-delay` | `1`（秒） | 重试间隔，禁止用 sleep 代替业务等待 |
| 作用范围 | **仅 UI** 或标记 `flaky` 的用例 | API 默认不重试 |

环境变量（可选）：`PYTEST_RERUNS=2`、`PYTEST_RERUNS_DELAY=1`

### 用例标记

对确认偶发的 UI 用例打 `@pytest.mark.flaky`：

```python
import pytest

@pytest.mark.ui
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_full_checkout_payment_success(self, driver, log_test_name):
    ...
```

- **API 用例**：不加 `flaky`；连接类错误可在 `ShopApiClient` 内做 **最多 1 次** 请求重试，且只针对 `ConnectionError` / `Timeout`
- 在 `pytest.ini` 注册 `flaky` marker，避免警告

### 日志与报告

- 重试发生时必须在日志中可见（pytest-rerunfailures 会输出 `RERUN`）
- HTML 报告保留 **最终** 结果；若最终通过但曾失败，在 PR/说明中标注为 flaky 并建 issue 修根因
- 失败截图：以 **最后一次失败** 为准（已有 `screenshot_on_failure`）

### 重试反模式

- 全局 `--reruns 5` 刷绿 CI
- 对 API 业务错误（库存不足、code≠0）重试
- 用重试替代显式等待或修复 locator
- 不记录 flaky 用例、不跟进根因

## 用例 ID 对照

| 模块 | API ID | UI ID |
|------|--------|-------|
| 加购 | API-CART-001 | CART-001 |
| 重复加购 | API-CART-002 | CART-002 |
| 超库存 | API-CART-003 | — |
| 删除 | API-CART-004 | CART-004 |
| 下单 | API-CHK-001 | CHK-001 |
| 支付成功 | API-PAY-001 | PAY-001 |
| 支付取消 | API-PAY-002 | PAY-002 |
| 支付幂等 | API-PAY-003 | — |
| 登录 | API-AUTH-001 | AUTH-001 |

## 配置项

| 变量 | 默认 | 说明 |
|------|------|------|
| BASE_URL | http://127.0.0.1:5000 | 站点根 URL |
| API_PREFIX | /api/v1 | API 前缀 |
| TEST_USER | test@demo.com | 账号 |
| TEST_PASSWORD | 123456 | 密码 |
| DEFAULT_SKU | sku-001 | 默认商品 |
| HEADLESS | false | UI 无头模式 |
| PYTEST_RERUNS | 0 | UI 重试次数（命令行 `--reruns` 优先） |
| PYTEST_RERUNS_DELAY | 1 | 重试间隔秒数 |

## 对接真实项目

1. 改 `BASE_URL` / `API_PREFIX`
2. 扩展 `ShopApiClient` 方法对齐真实 API
3. 改 Page 内 `data-testid`
4. 保留：全局日志、pytest-html、UI 失败截图、API session 隔离

## 反模式

- 仅 UI 测复杂金额/状态机（应 API 断言）
- mock/stub 接口或支付
- API 与 UI 共用同一 session 导致串扰
- UI 使用 sleep；API 无业务 code 断言
- UI 失败无截图；无日志文件
- **违反 POM**：test 中直接操作 WebDriver / 写 locator
- **滥用重试**：掩盖稳定失败、对 API 业务错误重试
- **性能测试**：本 Skill 不包含压测/负载/benchmark（见范围外说明）

## 附加资源

- [test-case-template.md](test-case-template.md)
- [examples.md](examples.md)
