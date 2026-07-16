# tests/utils/popup_helper.py — 按需局部弹窗处理（自定义模块，非全局扫描）
import logging  # 标准库：日志

from selenium.common.exceptions import TimeoutException  # 框架调用：短超时捕获，来源 selenium

from tests.utils.wait_helper import WaitHelper  # 自定义调用：复用显式等待

logger = logging.getLogger(__name__)  # 标准库：模块 logger


class PopupHelper:  # 自定义类：步骤级弹窗处理
    """仅在对应操作后调用；禁止在 conftest 全局自动关闭所有弹窗。"""  # 自定义文档

    def __init__(self, driver):  # 自定义构造
        self.driver = driver  # 自定义：WebDriver
        self.wait = WaitHelper(driver)  # 自定义调用：内部 WaitHelper

    def dismiss_cookie_if_present(self, short_timeout=2):  # 自定义：商品页 cookie 条
        by, loc = WaitHelper.by_testid("cookie-consent")  # 自定义调用：定位 cookie 遮罩
        try:  # 自定义：短超时，未出现不算失败
            self.wait.until_visible(by, loc, timeout=short_timeout)  # 自定义调用：显式等待出现
            logger.warning("检测到 Cookie 弹窗，尝试关闭")  # 自定义：WARNING 级别
            btn_by, btn_loc = WaitHelper.by_testid("cookie-accept-btn")  # 自定义：同意按钮
            self.wait.until_clickable(btn_by, btn_loc, timeout=short_timeout).click()  # 框架调用：element.click
            self.wait.until_invisible(by, loc, timeout=short_timeout)  # 自定义：等遮罩消失
            logger.info("Cookie 弹窗已关闭")  # 自定义
        except TimeoutException:  # 框架异常：未出现弹窗
            logger.info("未出现 Cookie 弹窗，跳过")  # 自定义

    def confirm_price_change_if_present(self, short_timeout=3):  # 自定义：结算后价格变动框
        by, loc = WaitHelper.by_testid("price-change-dialog")  # 自定义
        try:  # 自定义
            self.wait.until_visible(by, loc, timeout=short_timeout)  # 自定义调用
            logger.warning("检测到价格变动弹窗")  # 自定义
            btn_by, btn_loc = WaitHelper.by_testid("confirm-price-change-btn")  # 自定义
            self.wait.until_clickable(btn_by, btn_loc, timeout=short_timeout).click()  # 框架调用 click
            self.wait.until_invisible(by, loc, timeout=short_timeout)  # 自定义
            logger.info("价格变动弹窗已确认")  # 自定义
            return True  # 自定义：表示曾出现并已处理
        except TimeoutException:  # 框架异常
            logger.info("未出现价格变动弹窗，跳过")  # 自定义
            return False  # 自定义：未出现
