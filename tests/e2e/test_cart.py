# tests/e2e/test_cart.py — 购物车 UI 自动化用例（pytest + Selenium）
import logging  # 标准库

import pytest  # 框架：pytest 测试运行器

from tests.pages.product_page import ProductPage  # 自定义调用：商品页 PO
from tests.pages.cart_page import CartPage  # 自定义调用：购物车 PO
from tests.utils.config import Config  # 自定义调用：DEFAULT_SKU

logger = logging.getLogger(__name__)  # 标准库：模块 logger


@pytest.mark.ui  # 框架 marker：UI 层
@pytest.mark.cart  # 框架：自定义 marker 分组
@pytest.mark.flaky(reruns=2, reruns_delay=1)  # 框架+插件：UI 重试机制（Skill 强制）
class TestCart:  # 自定义：购物车测试类

    def test_cart_add_item_shows_badge_count_one(self, driver, log_test_name):  # 框架：test 方法，注入 fixture
        """CART-001: 加购后角标为 1"""  # 自定义：用例文档
        product = ProductPage(driver)  # 自定义：实例化 ProductPage
        product.open_product(Config.DEFAULT_SKU)  # 自定义调用：打开默认 SKU
        product.add_to_cart(quantity=1)  # 自定义调用：加购 1 件
        assert product.get_badge_count() == "1"  # 框架 assert：角标断言
        logger.info("CART-001 通过：角标为 1")  # 自定义日志

    def test_cart_add_same_sku_increases_badge(self, driver, log_test_name):  # 框架
        """CART-002: 同 SKU 重复加购角标累加"""  # 自定义
        product = ProductPage(driver)  # 自定义
        product.open_product(Config.DEFAULT_SKU)  # 自定义
        product.add_to_cart(quantity=1)  # 自定义：第一次
        product.add_to_cart(quantity=1)  # 自定义：第二次
        assert product.get_badge_count() == "2"  # 框架 assert
        logger.info("CART-002 通过：角标为 2")  # 自定义

    def test_cart_update_quantity_on_cart_page(self, driver, log_test_name):  # 框架
        """CART-003: 购物车页修改数量"""  # 自定义
        sku = Config.DEFAULT_SKU  # 自定义
        product = ProductPage(driver)  # 自定义
        cart = CartPage(driver)  # 自定义
        product.open_product(sku)  # 自定义
        product.add_to_cart(quantity=1)  # 自定义
        cart.open_cart()  # 自定义
        cart.update_quantity(sku, 3)  # 自定义：改为 3
        assert cart.get_item_quantity(sku) == "3"  # 框架 assert
        logger.info("CART-003 通过：数量为 3")  # 自定义

    def test_cart_delete_item_shows_empty(self, driver, log_test_name):  # 框架
        """CART-004: 删除商品后购物车为空"""  # 自定义
        sku = Config.DEFAULT_SKU  # 自定义
        product = ProductPage(driver)  # 自定义
        cart = CartPage(driver)  # 自定义
        product.open_product(sku)  # 自定义
        product.add_to_cart(quantity=1)  # 自定义
        cart.open_cart()  # 自定义
        cart.delete_item(sku)  # 自定义
        assert cart.is_empty() is True  # 框架 assert
        logger.info("CART-004 通过：购物车为空")  # 自定义
