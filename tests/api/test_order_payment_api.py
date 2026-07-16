# tests/api/test_order_payment_api.py — 结算/支付/登录接口测试（pytest + requests）
import logging  # 标准库

import pytest  # 框架

from tests.clients.shop_api_client import ShopApiClient  # 自定义
from tests.utils.config import Config  # 自定义

logger = logging.getLogger(__name__)  # 标准库


@pytest.mark.api  # 框架 marker
@pytest.mark.checkout  # 框架 marker
class TestCheckoutApi:  # 自定义

    def test_api_checkout_creates_pending_order(self, api_client, log_api_test):  # 框架
        """API-CHK-001: 下单后 status=PENDING_PAYMENT"""  # 自定义
        ShopApiClient.assert_ok(api_client.add_cart_item(Config.DEFAULT_SKU, 1))  # 自定义加购
        order = ShopApiClient.assert_ok(api_client.checkout())  # 自定义下单
        assert order["status"] == "PENDING_PAYMENT"  # 框架 assert
        assert order["total"] == 109.0  # 框架 assert：99 + 10 运费
        assert order["order_id"].startswith("ORD-")  # 框架 assert
        logger.info("API-CHK-001 通过 order=%s", order["order_id"])  # 自定义

    def test_api_checkout_empty_cart_fails(self, api_client, log_api_test):  # 框架
        """API-CHK-002: 空车下单失败"""  # 自定义
        resp = api_client.checkout()  # 自定义
        body = resp.json()  # 第三方
        assert resp.status_code == 400  # 框架 assert
        assert body["code"] == 1004  # 框架 assert
        logger.info("API-CHK-002 通过")  # 自定义


@pytest.mark.api  # 框架 marker
@pytest.mark.payment  # 框架 marker
class TestPaymentApi:  # 自定义

    def _create_pending_order(self, client):  # 自定义 helper：创建待支付订单
        ShopApiClient.assert_ok(client.add_cart_item(Config.DEFAULT_SKU, 1))  # 自定义
        return ShopApiClient.assert_ok(client.checkout())  # 自定义返回 order data

    def test_api_payment_success_updates_status(self, api_client, log_api_test):  # 框架
        """API-PAY-001: 支付成功订单变 PAID"""  # 自定义
        order = self._create_pending_order(api_client)  # 自定义 helper
        paid = ShopApiClient.assert_ok(  # 自定义
            api_client.payment_confirm(order["order_id"], action="success")  # 自定义沙箱确认
        )
        assert paid["status"] == "PAID"  # 框架 assert
        cart = ShopApiClient.assert_ok(api_client.get_cart())  # 自定义：支付后清空车
        assert cart["item_count"] == 0  # 框架 assert
        logger.info("API-PAY-001 通过")  # 自定义

    def test_api_payment_cancel_keeps_pending(self, api_client, log_api_test):  # 框架
        """API-PAY-002: 取消支付保持待支付"""  # 自定义
        order = self._create_pending_order(api_client)  # 自定义
        result = ShopApiClient.assert_ok(  # 自定义
            api_client.payment_confirm(order["order_id"], action="cancel")  # 自定义
        )
        assert result["status"] == "PENDING_PAYMENT"  # 框架 assert
        logger.info("API-PAY-002 通过")  # 自定义

    def test_api_payment_idempotent(self, api_client, log_api_test):  # 框架
        """API-PAY-003: 重复 payment_id 幂等"""  # 自定义
        order = self._create_pending_order(api_client)  # 自定义
        pid = "PAY-IDEMPOTENT-001"  # 自定义固定 payment_id
        ShopApiClient.assert_ok(api_client.payment_confirm(order["order_id"], payment_id=pid))  # 自定义第一次
        second = ShopApiClient.assert_ok(api_client.payment_confirm(order["order_id"], payment_id=pid))  # 自定义重复
        assert second["status"] == "PAID"  # 框架 assert
        logger.info("API-PAY-003 通过")  # 自定义


@pytest.mark.api  # 框架 marker
@pytest.mark.login  # 框架 marker
class TestAuthApi:  # 自定义

    def test_api_login_success(self, api_client, log_api_test):  # 框架
        """API-AUTH-001: 登录成功"""  # 自定义
        data = ShopApiClient.assert_ok(api_client.login())  # 自定义
        assert data["email"] == Config.TEST_USER  # 框架 assert
        logger.info("API-AUTH-001 通过")  # 自定义

    def test_api_login_wrong_password(self, api_client, log_api_test):  # 框架
        """API-AUTH-002: 密码错误"""  # 自定义
        resp = api_client.login(password="wrong")  # 自定义
        body = resp.json()  # 第三方
        assert resp.status_code == 401  # 框架 assert
        assert body["code"] == 1001  # 框架 assert
        logger.info("API-AUTH-002 通过")  # 自定义
