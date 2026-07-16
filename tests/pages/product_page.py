# tests/pages/product_page.py — 商品详情页 Page Object（自定义）
import logging  # 标准库

from tests.pages.base_page import BasePage  # 自定义调用
from tests.utils.config import Config  # 自定义调用
from tests.utils.wait_helper import WaitHelper  # 自定义调用
from tests.utils.popup_helper import PopupHelper  # 自定义调用：按需 cookie 弹窗

logger = logging.getLogger(__name__)  # 标准库


class ProductPage(BasePage):  # 自定义：商品页

    def open_product(self, sku_id=None):  # 自定义：打开指定 SKU 商品页
        url = Config.product_url(sku_id)  # 自定义调用：拼 URL
        logger.info("打开商品页: %s", url)  # 自定义
        self.driver.get(url)  # 框架调用：WebDriver.get
        PopupHelper(self.driver).dismiss_cookie_if_present()  # 自定义调用：仅在本页按需关 cookie

    def add_to_cart(self, quantity=1):  # 自定义：加购
        logger.info("加购数量: %s", quantity)  # 自定义
        qty_by, qty_loc = WaitHelper.by_testid("product-qty-input")  # 自定义
        btn_by, btn_loc = WaitHelper.by_testid("add-to-cart-btn")  # 自定义
        qty_el = self.wait.until_visible(qty_by, qty_loc)  # 自定义调用
        qty_el.clear()  # 框架调用
        qty_el.send_keys(str(quantity))  # 框架调用
        self.wait.until_clickable(btn_by, btn_loc).click()  # 框架调用 click
        toast_by, toast_loc = WaitHelper.by_testid("add-success-toast")  # 自定义：成功 toast
        self.wait.until_visible(toast_by, toast_loc)  # 自定义：显式等 toast，不用 sleep
        badge_by, badge_loc = WaitHelper.by_testid("cart-badge-count")  # 自定义：角标
        self.wait.until_visible(badge_by, badge_loc)  # 自定义

    def get_badge_count(self):  # 自定义：读购物车角标
        return self.get_text("cart-badge-count")  # 自定义调用 BasePage.get_text
