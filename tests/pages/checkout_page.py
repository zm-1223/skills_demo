# tests/pages/checkout_page.py — 结算页 Page Object（自定义）
import logging  # 标准库

from tests.pages.base_page import BasePage  # 自定义调用
from tests.utils.config import Config  # 自定义调用
from tests.utils.wait_helper import WaitHelper  # 自定义调用
from tests.utils.popup_helper import PopupHelper  # 自定义调用

logger = logging.getLogger(__name__)  # 标准库


class CheckoutPage(BasePage):  # 自定义：结算页

    def open_checkout(self, price_change=False):  # 自定义：打开结算页
        url = Config.checkout_url(price_change=price_change)  # 自定义调用
        logger.info("打开结算页: %s", url)  # 自定义
        self.driver.get(url)  # 框架调用 get
        self.wait.until_url_contains("/checkout")  # 自定义

    def get_payable_text(self):  # 自定义：应付总额文案
        return self.get_text("checkout-payable")  # 自定义调用

    def submit_order(self, handle_price_change=True):  # 自定义：提交订单
        logger.info("提交订单")  # 自定义
        by, loc = WaitHelper.by_testid("submit-order-btn")  # 自定义
        self.wait.until_clickable(by, loc).click()  # 框架调用 click
        if handle_price_change:  # 自定义：提交后按需处理价格弹窗
            PopupHelper(self.driver).confirm_price_change_if_present()  # 自定义调用
        self.wait.until_url_contains("/payment/", timeout=Config.PAYMENT_WAIT)  # 自定义：等跳转支付沙箱
