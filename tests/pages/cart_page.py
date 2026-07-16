# tests/pages/cart_page.py — 购物车页 Page Object（自定义）
import logging  # 标准库

from tests.pages.base_page import BasePage  # 自定义调用
from tests.utils.wait_helper import WaitHelper  # 自定义调用

logger = logging.getLogger(__name__)  # 标准库


class CartPage(BasePage):  # 自定义：购物车页
    PATH = "/cart"  # 自定义路径

    def open_cart(self):  # 自定义：进入购物车
        self.open(self.PATH)  # 自定义调用 BasePage.open
        self.wait.until_url_contains("/cart")  # 自定义：显式等 URL

    def get_cart_total_text(self):  # 自定义：读合计文案
        return self.get_text("cart-total")  # 自定义调用

    def get_item_quantity(self, sku_id):  # 自定义：读某 SKU 数量输入框 value
        by, loc = WaitHelper.by_testid(f"cart-item-qty-{sku_id}")  # 自定义
        el = self.wait.until_visible(by, loc)  # 自定义调用
        return el.get_attribute("value")  # 框架调用：WebElement.get_attribute

    def update_quantity(self, sku_id, quantity):  # 自定义：改数量并提交
        logger.info("更新购物车 SKU=%s quantity=%s", sku_id, quantity)  # 自定义
        by, loc = WaitHelper.by_testid(f"cart-item-qty-{sku_id}")  # 自定义
        el = self.wait.until_visible(by, loc)  # 自定义
        el.clear()  # 框架调用
        el.send_keys(str(quantity))  # 框架调用
        upd_by, upd_loc = WaitHelper.by_testid(f"cart-item-update-{sku_id}")  # 自定义
        self.wait.until_clickable(upd_by, upd_loc).click()  # 框架调用 click

    def delete_item(self, sku_id):  # 自定义：删除商品
        logger.info("删除购物车 SKU=%s", sku_id)  # 自定义
        del_by, del_loc = WaitHelper.by_testid(f"cart-item-delete-{sku_id}")  # 自定义
        self.wait.until_clickable(del_by, del_loc).click()  # 框架调用 click

    def go_checkout(self):  # 自定义：点击去结算
        logger.info("点击去结算")  # 自定义
        by, loc = WaitHelper.by_testid("checkout-btn")  # 自定义
        self.wait.until_clickable(by, loc).click()  # 框架调用 click
        self.wait.until_url_contains("/checkout")  # 自定义

    def is_empty(self):  # 自定义：是否空购物车
        return self.is_present("empty-cart-msg")  # 自定义调用 BasePage.is_present
