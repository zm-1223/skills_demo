# tests/utils/wait_helper.py — Selenium 显式/隐性等待封装（自定义模块，依赖 selenium 框架）
import logging  # 标准库：记录等待日志，来源 Python 内置

from selenium.webdriver.support.ui import WebDriverWait  # 框架调用：显式等待类，来源 selenium
from selenium.webdriver.support import expected_conditions as EC  # 框架调用：预期条件集合，来源 selenium
from selenium.webdriver.common.by import By  # 框架调用：定位策略常量，来源 selenium
from selenium.common.exceptions import TimeoutException  # 框架调用：超时异常，来源 selenium

from tests.utils.config import Config  # 自定义调用：读取 EXPLICIT_WAIT 等配置

logger = logging.getLogger(__name__)  # 标准库：本模块 logger，供步骤日志输出


class WaitHelper:  # 自定义类：封装 WebDriverWait 常用操作
    """显式等待工具；禁止在业务 Page 中直接使用 time.sleep。"""  # 自定义文档

    def __init__(self, driver, timeout=None):  # 自定义构造：绑定 driver
        self.driver = driver  # 自定义：保存 WebDriver 实例引用
        self.timeout = timeout or Config.EXPLICIT_WAIT  # 自定义：默认超时来自 Config

    def until_visible(self, by, locator, timeout=None):  # 自定义：等元素可见
        wait_sec = timeout or self.timeout  # 自定义：本次等待秒数
        logger.info("显式等待可见: %s=%s timeout=%s", by, locator, wait_sec)  # 自定义：写 INFO 日志
        return WebDriverWait(self.driver, wait_sec).until(  # 框架调用：WebDriverWait.until
            EC.visibility_of_element_located((by, locator))  # 框架调用：可见条件
        )

    def until_clickable(self, by, locator, timeout=None):  # 自定义：等元素可点击
        wait_sec = timeout or self.timeout  # 自定义
        logger.info("显式等待可点击: %s=%s timeout=%s", by, locator, wait_sec)  # 自定义
        return WebDriverWait(self.driver, wait_sec).until(  # 框架调用
            EC.element_to_be_clickable((by, locator))  # 框架调用
        )

    def until_url_contains(self, text, timeout=None):  # 自定义：等 URL 包含片段
        wait_sec = timeout or self.timeout  # 自定义
        logger.info("显式等待 URL 包含: %s timeout=%s", text, wait_sec)  # 自定义
        return WebDriverWait(self.driver, wait_sec).until(  # 框架调用
            EC.url_contains(text)  # 框架调用
        )

    def until_invisible(self, by, locator, timeout=None):  # 自定义：等元素消失
        wait_sec = timeout or self.timeout  # 自定义
        logger.info("显式等待消失: %s=%s timeout=%s", by, locator, wait_sec)  # 自定义
        return WebDriverWait(self.driver, wait_sec).until(  # 框架调用
            EC.invisibility_of_element_located((by, locator))  # 框架调用
        )

    @staticmethod  # 自定义：静态方法，设置隐性等待
    def setup_implicit_wait(driver):  # 自定义：在 fixture 中调用一次
        driver.implicitly_wait(Config.IMPLICIT_WAIT)  # 框架调用：WebDriver.implicitly_wait 隐性兜底
        logger.info("已设置隐性等待 %s 秒", Config.IMPLICIT_WAIT)  # 自定义日志

    @staticmethod  # 自定义
    def by_testid(test_id):  # 自定义：统一 data-testid CSS 选择器
        return By.CSS_SELECTOR, f'[data-testid="{test_id}"]'  # 自定义：返回 (By, locator) 元组
