# 示例

## 示例 1：用例清单（文档输出）

用户请求：「帮我列购物车 UI 测试用例」

| ID | 优先级 | 模块 | 标题 | 类型 |
|----|--------|------|------|------|
| CART-001 | P0 | 购物车 | 加购后角标显示 1 | UI |
| CART-002 | P0 | 购物车 | 同 SKU 再次加购角标累加 | UI |
| CART-003 | P1 | 购物车 | 超库存时页面提示不可结算 | UI |
| CHK-001 | P0 | 结算 | 结算页金额与购物车一致 | UI |
| PAY-001 | P0 | 支付 | 沙箱支付成功后展示成功页 | E2E |

---

## 示例 2：Playwright E2E + 显式等待 + 按需弹窗

```python
import logging
import re

import pytest
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


class ProductPage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str):
        logger.info("Open product page: %s", url)
        self.page.goto(url)
        self.dismiss_cookie_bar_if_present()

    def dismiss_cookie_bar_if_present(self):
        bar = self.page.locator("[data-testid='cookie-consent']")
        try:
            bar.wait_for(state="visible", timeout=2000)
            self.page.get_by_test_id("cookie-accept-btn").click()
            bar.wait_for(state="hidden")
            logger.info("Cookie bar dismissed")
        except Exception:
            logger.info("No cookie bar")

    def add_to_cart(self):
        self.page.get_by_test_id("add-to-cart-btn").click()
        expect(self.page.get_by_test_id("cart-badge-count")).to_have_text("1")


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page

    def submit_order(self):
        self.page.get_by_test_id("submit-order-btn").click()
        self.confirm_price_change_if_present()

    def confirm_price_change_if_present(self):
        dialog = self.page.locator("[data-testid='price-change-dialog']")
        try:
            dialog.wait_for(state="visible", timeout=3000)
            self.page.get_by_test_id("confirm-price-change-btn").click()
            dialog.wait_for(state="hidden")
            logger.warning("Price change dialog confirmed")
        except Exception:
            logger.info("No price change dialog")


def test_checkout_happy_path(page: Page, base_url: str, product_url: str):
    product = ProductPage(page)
    checkout = CheckoutPage(page)

    product.open(product_url)
    product.add_to_cart()

    page.get_by_test_id("checkout-btn").click()
    expect(page).to_have_url(re.compile(r"/checkout"))

    checkout.submit_order()

    # 真实沙箱：等跳转回站点的成功态，不用 sleep
    expect(page.get_by_test_id("payment-success-msg")).to_be_visible(timeout=60_000)
    logger.info("Payment success verified on UI")
```

---

## 示例 3：conftest — 日志 + 失败截图 + 隐性超时

```python
import logging
from datetime import datetime
from pathlib import Path

import pytest


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
    logging.info("Log file: %s", log_file)


@pytest.fixture
def page(page):
    page.set_default_timeout(10_000)
    page.set_default_navigation_timeout(30_000)
    yield page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            out = Path("reports/screenshots")
            out.mkdir(parents=True, exist_ok=True)
            path = out / f"{item.name}.png"
            page.screenshot(path=path, full_page=True)
            logging.error("Failure screenshot: %s", path)
```

---

## 示例 4：Selenium 显式等待（无 sleep）

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def click_checkout(driver):
    driver.implicitly_wait(5)  # 隐性兜底，仅初始化一次
    btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='checkout-btn']"))
    )
    btn.click()
    WebDriverWait(driver, 15).until(EC.url_contains("/checkout"))
```

---

## 示例 5：生成报告命令

```bash
pytest tests/e2e/ -v --html=reports/report.html --self-contained-html
pytest tests/e2e/ -v --alluredir=reports/allure-results
```

---

## 示例 6：用户对话 → Agent 行为

| 用户说 | Agent 应做 |
|--------|------------|
| 「写购物车测试用例」 | 输出 UI 用例清单，标注弹窗点与等待策略 |
| 「实现支付 E2E」 | 真实环境 + 沙箱支付 + 显式等待 + conftest 日志截图报告 |
| 「老失败在弹窗」 | 在对应 Page 步骤后加局部弹窗 helper，禁止全局扫描 |
| 「加测试报告」 | pytest-html 或 allure 配置 + 失败截图 hook |
