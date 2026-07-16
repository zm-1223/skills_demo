# tests/e2e/conftest.py — UI fixture：WebDriver、失败截图、Allure 附件（自定义 + pytest/selenium/allure）
import logging  # 标准库：日志
from pathlib import Path  # 标准库：截图路径

import allure  # 第三方：Allure 报告附件 API，来源 allure-pytest 依赖包
import pytest  # 框架：pytest fixture 与 hook
from selenium import webdriver  # 框架：Selenium WebDriver
from selenium.webdriver.chrome.options import Options  # 框架：Chrome 配置
from selenium.webdriver.chrome.service import Service  # 框架：Chrome 驱动服务
from webdriver_manager.chrome import ChromeDriverManager  # 第三方：自动管理 chromedriver

from tests.utils.config import Config  # 自定义：HEADLESS 等环境配置
from tests.utils.wait_helper import WaitHelper  # 自定义：隐性/显式等待封装

logger = logging.getLogger(__name__)  # 标准库：模块 logger


@pytest.fixture  # 框架装饰器：每个 UI 用例注入独立 driver
def driver(request):  # 自定义：WebDriver 生命周期 fixture
    logger.info("启动 Chrome WebDriver")  # 自定义：步骤日志
    options = Options()  # 框架调用：创建 ChromeOptions，来源 selenium
    if Config.HEADLESS:  # 自定义：读取无头配置
        options.add_argument("--headless=new")  # 框架调用：Chrome 无头参数
    options.add_argument("--window-size=1280,800")  # 框架调用：窗口尺寸
    options.add_argument("--disable-gpu")  # 框架调用：禁用 GPU（CI 常用）
    service = Service(ChromeDriverManager().install())  # 第三方调用：安装/缓存 chromedriver
    browser = webdriver.Chrome(service=service, options=options)  # 框架调用：启动 Chrome
    browser.maximize_window()  # 框架调用：最大化窗口
    WaitHelper.setup_implicit_wait(browser)  # 自定义调用：设置隐性等待
    request.node._driver = browser  # 自定义：挂到 node 供截图 hook 读取
    yield browser  # 框架语法：交给测试用例使用
    logger.info("关闭 WebDriver")  # 自定义
    browser.quit()  # 框架调用：关闭浏览器


@pytest.hookimpl(tryfirst=True, hookwrapper=True)  # 框架 hook：生成用例阶段 report
def pytest_runtest_makereport(item, call):  # 自定义：记录 setup/call/teardown 结果
    outcome = yield  # 框架 hookwrapper 固定写法
    report = outcome.get_result()  # 框架：取 TestReport
    setattr(item, f"rep_{report.when}", report)  # 自定义：供 screenshot fixture 使用


@pytest.fixture(autouse=True)  # 框架：每个 UI 用例自动执行
def screenshot_on_failure(request):  # 自定义：失败截图并 attach 到 Allure
    yield  # 框架：先执行用例
    rep = getattr(request.node, "rep_call", None)  # 自定义：取 call 阶段结果
    if rep is not None and rep.failed:  # 自定义：仅失败时
        browser = getattr(request.node, "_driver", None)  # 自定义：取 WebDriver
        if browser is not None:  # 自定义：UI 用例才有 driver
            path = Path("reports/screenshots") / f"{request.node.name}.png"  # 自定义：截图路径
            path.parent.mkdir(parents=True, exist_ok=True)  # 标准库：确保目录存在
            browser.save_screenshot(str(path))  # 框架调用：WebDriver 截图
            logger.error("UI 用例失败，截图: %s", path)  # 自定义 ERROR 日志
            allure.attach.file(  # 第三方调用：附加文件到 Allure 报告
                str(path),  # 自定义：文件路径
                name="失败截图",  # 自定义：附件名称
                attachment_type=allure.attachment_type.PNG,  # 第三方：PNG 类型枚举
            )


@pytest.fixture  # 框架 fixture
def log_test_name(request):  # 自定义：用例边界日志
    logger.info("===== UI 用例开始: %s =====", request.node.name)  # 自定义
    yield  # 框架
    logger.info("===== UI 用例结束: %s =====", request.node.name)  # 自定义
