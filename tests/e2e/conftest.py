# tests/e2e/conftest.py — UI 测试 fixture：WebDriver、失败截图（日志在 tests/conftest.py）
import logging  # 标准库
from pathlib import Path  # 标准库

import pytest  # 框架：pytest
from selenium import webdriver  # 框架：Selenium WebDriver
from selenium.webdriver.chrome.options import Options  # 框架：Chrome 选项
from selenium.webdriver.chrome.service import Service  # 框架：Chrome Service
from webdriver_manager.chrome import ChromeDriverManager  # 第三方：chromedriver 管理

from tests.utils.config import Config  # 自定义：HEADLESS 等
from tests.utils.wait_helper import WaitHelper  # 自定义：隐性等待

logger = logging.getLogger(__name__)  # 标准库


@pytest.fixture  # 框架：每用例一个浏览器
def driver(request):  # 自定义：WebDriver 生命周期
    logger.info("启动 Chrome WebDriver")  # 自定义
    options = Options()  # 框架调用
    if Config.HEADLESS:  # 自定义
        options.add_argument("--headless=new")  # 框架调用
    options.add_argument("--window-size=1280,800")  # 框架调用
    options.add_argument("--disable-gpu")  # 框架调用
    service = Service(ChromeDriverManager().install())  # 第三方
    browser = webdriver.Chrome(service=service, options=options)  # 框架调用
    browser.maximize_window()  # 框架调用
    WaitHelper.setup_implicit_wait(browser)  # 自定义调用
    request.node._driver = browser  # 自定义：供截图 hook
    yield browser  # 框架
    logger.info("关闭 WebDriver")  # 自定义
    browser.quit()  # 框架调用


@pytest.hookimpl(tryfirst=True, hookwrapper=True)  # 框架 hook
def pytest_runtest_makereport(item, call):  # 自定义：记录用例结果阶段
    outcome = yield  # 框架 hookwrapper
    report = outcome.get_result()  # 框架
    setattr(item, f"rep_{report.when}", report)  # 自定义


@pytest.fixture(autouse=True)  # 框架：UI 用例自动失败截图
def screenshot_on_failure(request):  # 自定义
    yield  # 框架
    rep = getattr(request.node, "rep_call", None)  # 自定义
    if rep is not None and rep.failed:  # 自定义：仅失败
        browser = getattr(request.node, "_driver", None)  # 自定义
        if browser is not None:  # 自定义：仅 UI 有用例有 driver
            path = Path("reports/screenshots") / f"{request.node.name}.png"  # 自定义
            browser.save_screenshot(str(path))  # 框架调用
            logger.error("UI 用例失败，截图: %s", path)  # 自定义


@pytest.fixture  # 框架
def log_test_name(request):  # 自定义：UI 用例边界日志
    logger.info("===== UI 用例开始: %s =====", request.node.name)  # 自定义
    yield  # 框架
    logger.info("===== UI 用例结束: %s =====", request.node.name)  # 自定义
