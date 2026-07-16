# tests/api/test_cart_api.py — 购物车接口测试（pytest + requests）
import logging  # 标准库

import pytest  # 框架

from tests.clients.shop_api_client import ShopApiClient  # 自定义
from tests.utils.config import Config  # 自定义

logger = logging.getLogger(__name__)  # 标准库


@pytest.mark.api  # 框架 marker：接口层
@pytest.mark.cart  # 框架 marker：购物车模块
class TestCartApi:  # 自定义测试类

    def test_api_add_item_returns_quantity_one(self, api_client, log_api_test):  # 框架
        """API-CART-001: 加购后 GET cart 数量为 1"""  # 自定义
        sku = Config.DEFAULT_SKU  # 自定义
        data = ShopApiClient.assert_ok(api_client.add_cart_item(sku, 1))  # 自定义调用
        assert data["quantity"] == 1  # 框架 assert
        cart = ShopApiClient.assert_ok(api_client.get_cart())  # 自定义
        assert cart["item_count"] == 1  # 框架 assert
        assert cart["items"][0]["sku_id"] == sku  # 框架 assert
        logger.info("API-CART-001 通过")  # 自定义

    def test_api_add_same_sku_merges_quantity(self, api_client, log_api_test):  # 框架
        """API-CART-002: 重复加购合并数量"""  # 自定义
        sku = Config.DEFAULT_SKU  # 自定义
        ShopApiClient.assert_ok(api_client.add_cart_item(sku, 1))  # 自定义
        ShopApiClient.assert_ok(api_client.add_cart_item(sku, 2))  # 自定义
        cart = ShopApiClient.assert_ok(api_client.get_cart())  # 自定义
        assert cart["items"][0]["quantity"] == 3  # 框架 assert
        logger.info("API-CART-002 通过")  # 自定义

    def test_api_add_over_stock_returns_error(self, api_client, log_api_test):  # 框架
        """API-CART-003: 超库存返回 code 1003"""  # 自定义
        resp = api_client.add_cart_item("sku-002", 999)  # 自定义：sku-002 库存仅 5
        body = resp.json()  # 第三方
        assert resp.status_code == 400  # 框架 assert HTTP
        assert body["code"] == 1003  # 框架 assert 业务码
        logger.info("API-CART-003 通过")  # 自定义

    def test_api_delete_item_empties_cart(self, api_client, log_api_test):  # 框架
        """API-CART-004: 删除后购物车为空"""  # 自定义
        sku = Config.DEFAULT_SKU  # 自定义
        ShopApiClient.assert_ok(api_client.add_cart_item(sku, 1))  # 自定义
        ShopApiClient.assert_ok(api_client.delete_cart_item(sku))  # 自定义
        cart = ShopApiClient.assert_ok(api_client.get_cart())  # 自定义
        assert cart["items"] == []  # 框架 assert
        assert cart["item_count"] == 0  # 框架 assert
        logger.info("API-CART-004 通过")  # 自定义

    def test_api_update_quantity(self, api_client, log_api_test):  # 框架
        """API-CART-005: PUT 更新数量"""  # 自定义
        sku = Config.DEFAULT_SKU  # 自定义
        ShopApiClient.assert_ok(api_client.add_cart_item(sku, 1))  # 自定义
        ShopApiClient.assert_ok(api_client.update_cart_item(sku, 4))  # 自定义
        cart = ShopApiClient.assert_ok(api_client.get_cart())  # 自定义
        assert cart["items"][0]["quantity"] == 4  # 框架 assert
        logger.info("API-CART-005 通过")  # 自定义
