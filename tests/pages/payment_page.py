# tests/pages/payment_page.py — 支付沙箱与结果页 Page Object（自定义）
import logging  # 标准库

from tests.pages.base_page import BasePage  # 自定义调用
from tests.utils.config import Config  # 自定义调用
from tests.utils.wait_helper import WaitHelper  # 自定义调用

logger = logging.getLogger(__name__)  # 标准库


class PaymentPage(BasePage):  # 自定义：支付相关页面

    def confirm_payment_success(self):  # 自定义：沙箱点击支付成功
        logger.info("沙箱确认支付成功")  # 自定义
        self.wait.until_url_contains("/payment/")  # 自定义：确保在沙箱页
        by, loc = WaitHelper.by_testid("pay-confirm-btn")  # 自定义
        self.wait.until_clickable(by, loc, timeout=Config.PAYMENT_WAIT).click()  # 框架调用 click
        success_by, success_loc = WaitHelper.by_testid("payment-success-msg")  # 自定义
        self.wait.until_visible(success_by, success_loc, timeout=Config.PAYMENT_WAIT)  # 自定义：等成功页

    def cancel_payment(self):  # 自定义：沙箱取消支付
        logger.info("沙箱取消支付")  # 自定义
        by, loc = WaitHelper.by_testid("pay-cancel-btn")  # 自定义
        self.wait.until_clickable(by, loc).click()  # 框架调用 click
        fail_by, fail_loc = WaitHelper.by_testid("payment-fail-msg")  # 自定义
        self.wait.until_visible(fail_by, fail_loc, timeout=Config.PAYMENT_WAIT)  # 自定义：等失败页

    def get_success_message(self):  # 自定义：成功页文案
        return self.get_text("payment-success-msg")  # 自定义调用

    def get_fail_message(self):  # 自定义：失败页文案
        return self.get_text("payment-fail-msg")  # 自定义调用
