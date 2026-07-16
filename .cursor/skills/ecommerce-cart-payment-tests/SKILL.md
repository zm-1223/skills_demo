---
name: ecommerce-cart-payment-tests
description: >-
  设计与编写电商平台购物车、结算、支付流程的 UI/E2E 自动化测试用例与脚本。
  使用真实测试环境，含等待策略、弹窗处理、日志与报告。
  Use when the user mentions e-commerce cart, checkout, payment, order,
  购物车, 结算, 支付, 下单, UI自动化, E2E, or automated testing for shopping flows.
---

# 电商购物车与支付 UI 自动化测试

## 快速开始

接到任务后按顺序执行：

1. **确认测试类型**：仅 **UI/E2E**（本 Skill 不包含 API 层测试）
2. **确认真实环境**：使用项目指定的测试/预发环境 URL、测试账号、支付沙箱（真实网关测试通道，非 mock）
3. **读取项目约定**：检查 Playwright / Selenium、pytest、conftest、Page Object、现有报告与日志配置
4. **输出测试资产**：用例清单 → E2E 脚本 → 等待/弹窗工具 → 日志与报告 hook → conftest 配置

## 测试范围矩阵

| 模块 | 必测场景 | 常见边界 |
|------|----------|----------|
| 购物车 | 加购、改数量、删商品、清空、合并游客车 | 库存不足、下架、限购、失效 SKU |
| 结算 | 地址/运费/优惠券/积分/税费展示与计算 | 券过期、门槛不满足、地址不可达、价格变动 |
| 支付 | 发起支付、成功、失败、取消、超时 | 重复点击、支付页跳转、真实沙箱扣款 |
| 订单 | 支付后状态展示、订单详情、取消规则 | 支付中取消、待支付关单提示 |

## 用例设计规范

### 命名

```
test_<模块>_<场景>_<预期结果>
```

示例：`test_cart_add_item_shows_badge_count_one`

### 结构（AAA）

- **Arrange**：打开页面、登录、准备测试商品 URL
- **Act**：UI 操作（点击、输入、选择）
- **Assert**：页面元素可见性、文案、URL、订单页状态（通过 UI 观测）

### 优先级

- **P0**：主路径（加购 → 结算 → 真实支付沙箱成功 → 订单完成页）
- **P1**：常见异常（库存不足提示、支付失败、券不可用）
- **P2**：边界（限购、0 元单、游客与登录合并）

### 每条用例必须包含

| 字段 | 说明 |
|------|------|
| ID | 如 `CART-001` |
| 标题 | 一句话描述 |
| 前置条件 | 登录态、商品可购、测试环境可用 |
| 步骤 | 可执行的 UI 操作序列 |
| 预期结果 | 页面可见断言点 |
| 测试数据 | 商品链接、数量、测试账号、支付沙箱账号 |
| 弹窗点 | 哪些步骤可能触发弹窗及处理方式 |
| 清理 | 是否取消订单 / 退出登录 |

完整模板见 [test-case-template.md](test-case-template.md)。

## 购物车测试清单

```
- [ ] 空购物车展示
- [ ] 单 SKU 加购（数量=1）
- [ ] 同 SKU 重复加购（角标/数量合并）
- [ ] 修改数量（合法 / 超库存 / 低于最小起购）
- [ ] 删除单个商品
- [ ] 批量删除 / 清空购物车
- [ ] 下架或失效 SKU 的页面提示
- [ ] 登录前后游客购物车合并（以业务规则为准）
- [ ] 购物车金额汇总展示正确
```

## 结算测试清单

```
- [ ] 默认地址与运费展示
- [ ] 切换地址导致运费变化
- [ ] 可用优惠券抵扣展示
- [ ] 不可用优惠券的错误提示
- [ ] 积分抵扣上限提示
- [ ] 结算页价格与购物车一致
- [ ] 提交订单后跳转支付页或订单详情
```

## 支付测试清单

```
- [ ] 跳转真实支付沙箱页面（微信/支付宝/银联等测试通道）
- [ ] 支付成功后回到站点并展示成功态
- [ ] 支付失败 / 取消后页面提示与可重试
- [ ] 支付超时或关单提示
- [ ] 0 元单 / 纯积分单（若支持）
- [ ] 重复点击支付按钮的防重复表现
```

## 等待策略（核心）

**禁止使用 `time.sleep()` / 固定硬等待**，除非对接第三方页面且无 DOM 信号且已注明原因。

### 优先级

1. **显式等待（首选）**：等具体条件成立
2. **隐性等待（全局默认超时）**：作为兜底，不替代显式等待
3. **禁止**：用 sleep 代替断言、全局轮询所有弹窗

### Playwright

```python
# 隐性：全局默认超时（conftest 或 fixture 设置一次）
page.set_default_timeout(10_000)
page.set_default_navigation_timeout(30_000)

# 显式：等元素可交互 / 断言
page.get_by_test_id("cart-badge-count").wait_for(state="visible")
expect(page.get_by_test_id("checkout-btn")).to_be_enabled()
expect(page).to_have_url(re.compile(r"/order/confirm"))
```

### Selenium

```python
# 隐性：driver 级兜底（仅 setup 设置一次，不宜过大）
driver.implicitly_wait(5)

# 显式：WebDriverWait + expected_conditions
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='checkout-btn']"))
)
```

### 异步页面（支付回调、跳转）

- 用 **显式等待** 等待目标 URL、成功文案或订单状态元素
- 可配置 `timeout`（如支付页 60s），仍不用 sleep 轮询

```python
# Playwright 示例：等支付结果页
expect(page.get_by_text("支付成功")).to_be_visible(timeout=60_000)
```

## 弹窗等待机制（按需局部处理）

**禁止**在每条用例开头或全局 fixture 中扫描/关闭所有弹窗。

仅在 **必要操作或目标页面** 按需等待和处理：

| 触发时机 | 处理方式 |
|----------|----------|
| 进入商品页 | 仅处理 cookie/地区选择条（若挡住加购按钮） |
| 点击加购后 | 等「加入成功」toast 或规格弹窗关闭 |
| 进入结算页 | 等地址确认弹窗、运费变更提示 |
| 提交订单后 | 等库存/价格变动确认框 |
| 跳转支付前 | 等支付方式选择弹层 |

### 封装模式（Page Object 内）

```python
class CheckoutPage:
    def dismiss_price_change_dialog_if_present(self, page, timeout=3000):
        """仅在提交订单后调用，不全局检测"""
        dialog = page.locator("[data-testid='price-change-dialog']")
        try:
            dialog.wait_for(state="visible", timeout=timeout)
            page.get_by_test_id("confirm-price-change-btn").click()
            dialog.wait_for(state="hidden")
        except TimeoutError:
            pass  # 未出现则继续，不算失败
```

原则：

- 弹窗 helper **挂在对应 Page / 步骤后** 调用，不在 `conftest` 全局自动执行
- 用 **短超时** 的显式等待判断「是否出现」，出现才操作
- 记录日志：弹窗出现 / 已关闭 / 未出现

## 真实环境测试

- 使用 **测试/预发环境** 真实 URL（`BASE_URL` 来自 env 或配置文件）
- 使用 **真实测试账号** 登录，不 stub 登录态
- 支付走 **官方沙箱或测试商户号**（真实跳转支付页，非 mock 回调接口）
- 所需 env 示例：`BASE_URL`、`TEST_USER`、`TEST_PASSWORD`、`PAYMENT_SANDBOX_MODE`
- **禁止**：WireMock、responses、本地 stub 伪造支付结果；**禁止** mock 页面接口

## 日志（必须自动生成）

每个测试 run 自动输出结构化日志，便于 CI 与本地排查。

### 要求

- 使用 Python `logging`，禁止仅用 `print`
- 日志文件：`logs/test_{yyyyMMdd_HHmmss}.log`（或项目既有目录）
- 每条用例开始/结束、关键步骤、弹窗处理、失败堆栈均写日志
- 级别：INFO（步骤）、WARNING（弹窗/重试）、ERROR（失败）

### conftest 参考（pytest）

```python
import logging
from datetime import datetime
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"test_{datetime.now():%Y%m%d_%H%M%S}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logging.info("Test session started, log file: %s", log_file)
```

用例内：`logger = logging.getLogger(__name__)`，关键步骤 `logger.info(...)`。

## 报告与失败截图（必须自动生成）

### 测试报告

- 默认 **pytest-html** 或 **allure-pytest**（优先复用项目已有方案）
- 报告输出目录：`reports/`（如 `reports/report.html` 或 `reports/allure-results/`）
- 报告含：用例名、通过/失败、耗时、错误信息、日志链接

### 失败截图

在 `conftest.py` 用 hook **仅失败时** 截图，不每步都截：

```python
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")  # Playwright
        if page:
            screenshot_dir = Path("reports/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            path = screenshot_dir / f"{item.name}_{call.when}.png"
            page.screenshot(path=path, full_page=True)
            logging.error("Screenshot saved: %s", path)
            # allure: allure.attach.file(path, name="failure", attachment_type=allure.attachment_type.PNG)
```

Selenium 失败时对 `driver.save_screenshot(...)` 同理。

### 生成命令（写入变更说明，不自动执行）

```bash
pytest tests/e2e/ --html=reports/report.html --self-contained-html
# 或
pytest tests/e2e/ --alluredir=reports/allure-results
```

## 自动化实现原则

### 技术栈

| 职责 | 工具 |
|------|------|
| E2E | Playwright（首选）或 Selenium |
| 运行器 | pytest |
| 报告 | pytest-html / allure-pytest |
| 日志 | logging + 文件输出 |

### 数据与隔离

- 每用例独立浏览器 context 或清理 cookies（按项目 fixture）
- 测试账号、商品 URL 从 env / yaml 读取，不硬编码生产数据
- 支付使用沙箱测试号，避免真实资金

### UI 断言

- 金额：比对页面展示文本或 `data-amount` 属性，用 Decimal 解析
- 顺序：元素可见 → 文案/属性 → URL → 下游页面元素

### 项目适配

编写代码前必须：

1. 搜索 `tests/e2e/`、`conftest.py`、`*Page*.py`
2. 复用已有 base_url、login fixture、报告与日志配置
3. 不新增 API 测试文件

## 输出格式

### 1. 用例清单

```markdown
| ID | 优先级 | 模块 | 标题 | 类型 |
|----|--------|------|------|------|
| CART-001 | P0 | 购物车 | 加购后角标为 1 | UI |
```

### 2. E2E 代码

- 一个场景一个 test 函数
- Page Object 封装页面操作与 **按需弹窗** 处理
- 显式等待 + 日志，无 sleep
- conftest 含：日志、失败截图、报告配置

### 3. 变更说明

列出新增文件、env 变量、报告/日志/截图路径、运行命令（**不要自动执行测试**，除非用户明确要求）。

## 决策树

**仅要测试用例文档？** → 输出 UI 用例清单 + 步骤，不写代码

**要可运行自动化？** → E2E 脚本 + conftest（日志/截图/报告）+ Page Object

**支付页为第三方？** → 显式等待 URL/成功元素，使用官方沙箱账号，长 timeout，仍不用 mock

**偶发失败？** → 优先加强显式等待与弹窗局部处理；retry 仅标记 flaky，不掩盖 bug

## 反模式（避免）

- `time.sleep()` 固定等待
- 全局自动关闭所有弹窗
- mock / stub 支付或接口
- 编写 API 层测试（与本 Skill 范围冲突）
- 仅在 stdout 打印、无日志文件
- 失败无截图
- 多条 UI 断言堆在一个巨型 test 中

## 附加资源

- 用例字段模板：[test-case-template.md](test-case-template.md)
- 完整示例：[examples.md](examples.md)
