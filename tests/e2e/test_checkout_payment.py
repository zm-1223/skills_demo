# tests/e2e/test_checkout_payment.py — 结算与支付 E2E 用例（pytest + Selenium）
import logging  # 标准库

import pytest  # 框架：pytest

from tests.pages.product_page import ProductPage  # 自定义调用
from tests.pages.cart_page import CartPage  # 自定义调用
from tests.pages.checkout_page import CheckoutPage  # 自定义调用
from tests.pages.payment_page import PaymentPage  # 自定义调用
from tests.pages.login_page import LoginPage  # 自定义调用
from tests.utils.config import Config  # 自定义调用

logger = logging.getLogger(__name__)  # 标准库


@pytest.mark.ui  # 框架 marker：UI 层
@pytest.mark.checkout  # 框架 marker
class TestCheckout:  # 自定义：结算相关

    def test_checkout_payable_matches_cart_total_with_shipping(self, driver, log_test_name):  # 框架
        """CHK-001: 结算页应付含运费"""  # 自定义：99 商品 + 10 运费 = 109
        product = ProductPage(driver)  # 自定义
        cart = CartPage(driver)  # 自定义
        checkout = CheckoutPage(driver)  # 自定义
        product.open_product(Config.DEFAULT_SKU)  # 自定义
        product.add_to_cart(1)  # 自定义
        cart.open_cart()  # 自定义
        cart.go_checkout()  # 自定义
        payable = checkout.get_payable_text()  # 自定义
        assert "109.00" in payable  # 框架 assert：99+10 运费
        logger.info("CHK-001 通过：应付 %s", payable)  # 自定义


@pytest.mark.ui  # 框架 marker：UI 层
@pytest.mark.payment  # 框架 marker
class TestPaymentFlow:  # 自定义：支付全流程

    def test_full_checkout_payment_success(self, driver, log_test_name):  # 框架
        """PAY-001: 加购→结算→沙箱支付成功"""  # 自定义 P0 主路径
        product = ProductPage(driver)  # 自定义
        cart = CartPage(driver)  # 自定义
        checkout = CheckoutPage(driver)  # 自定义
        payment = PaymentPage(driver)  # 自定义
        product.open_product(Config.DEFAULT_SKU)  # 自定义
        product.add_to_cart(1)  # 自定义
        cart.open_cart()  # 自定义
        cart.go_checkout()  # 自定义
        checkout.submit_order(handle_price_change=True)  # 自定义：提交并按需处理弹窗
        payment.confirm_payment_success()  # 自定义：沙箱点成功
        assert payment.get_success_message() == "支付成功"  # 框架 assert
        logger.info("PAY-001 通过：支付成功")  # 自定义

    def test_payment_cancel_shows_fail_message(self, driver, log_test_name):  # 框架
        """PAY-002: 取消支付展示失败页"""  # 自定义
        product = ProductPage(driver)  # 自定义
        cart = CartPage(driver)  # 自定义
        checkout = CheckoutPage(driver)  # 自定义
        payment = PaymentPage(driver)  # 自定义
        product.open_product(Config.DEFAULT_SKU)  # 自定义
        product.add_to_cart(1)  # 自定义
        cart.open_cart()  # 自定义
        cart.go_checkout()  # 自定义
        checkout.submit_order()  # 自定义
        payment.cancel_payment()  # 自定义
        assert "支付已取消" in payment.get_fail_message()  # 框架 assert
        logger.info("PAY-002 通过：取消支付")  # 自定义

    def test_checkout_price_change_dialog_confirm(self, driver, log_test_name):  # 框架
        """CHK-002: 价格变动弹窗确认后继续支付"""  # 自定义
        product = ProductPage(driver)  # 自定义
        cart = CartPage(driver)  # 自定义
        checkout = CheckoutPage(driver)  # 自定义
        payment = PaymentPage(driver)  # 自定义
        product.open_product(Config.DEFAULT_SKU)  # 自定义
        product.add_to_cart(1)  # 自定义
        cart.open_cart()  # 自定义
        cart.go_checkout()  # 自定义
        driver.get(Config.checkout_url(price_change=True))  # 框架调用：带 price_change 参数进结算
        checkout.submit_order(handle_price_change=True)  # 自定义：触发并确认弹窗
        payment.confirm_payment_success()  # 自定义
        assert payment.get_success_message() == "支付成功"  # 框架 assert
        logger.info("CHK-002 通过：价格变动弹窗流程")  # 自定义


@pytest.mark.ui  # 框架 marker：UI 层
@pytest.mark.login  # 框架 marker
class TestLogin:  # 自定义：登录

    def test_login_success(self, driver, log_test_name):  # 框架
        """AUTH-001: 测试账号登录成功"""  # 自定义
        login = LoginPage(driver)  # 自定义
        login.open_login()  # 自定义
        login.login(Config.TEST_USER, Config.TEST_PASSWORD)  # 自定义
        assert "/login" not in driver.current_url  # 框架 assert：已离开登录页
        logger.info("AUTH-001 通过：登录成功")  # 自定义
