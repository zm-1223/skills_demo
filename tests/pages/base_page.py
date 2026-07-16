# tests/pages/base_page.py — Page Object 基类（自定义，基于 Selenium WebDriver）
import logging  # 标准库

from tests.utils.wait_helper import WaitHelper  # 自定义调用：等待工具
from tests.utils.config import Config  # 自定义调用：BASE_URL

logger = logging.getLogger(__name__)  # 标准库


class BasePage:  # 自定义：所有 Page 的父类
    """封装 driver、wait 与通用导航。"""  # 自定义文档

    def __init__(self, driver):  # 自定义构造
        self.driver = driver  # 自定义：WebDriver 实例
        self.wait = WaitHelper(driver)  # 自定义调用：创建 WaitHelper
        self.base_url = Config.BASE_URL  # 自定义：根 URL

    def open(self, path=""):  # 自定义：打开相对路径
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"  # 自定义拼接
        logger.info("打开页面: %s", url)  # 自定义日志
        self.driver.get(url)  # 框架调用：WebDriver.get 导航

    def get_text(self, test_id, timeout=None):  # 自定义：读 data-testid 元素文本
        by, loc = WaitHelper.by_testid(test_id)  # 自定义调用
        el = self.wait.until_visible(by, loc, timeout=timeout)  # 自定义调用
        return el.text  # 框架属性：WebElement.text

    def is_present(self, test_id, timeout=2):  # 自定义：判断元素是否出现（短超时）
        by, loc = WaitHelper.by_testid(test_id)  # 自定义
        try:  # 自定义
            self.wait.until_visible(by, loc, timeout=timeout)  # 自定义
            return True  # 自定义
        except Exception:  # 自定义：任何失败视为不存在
            return False  # 自定义
