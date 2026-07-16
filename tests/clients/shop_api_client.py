# tests/clients/shop_api_client.py — 商城 REST API 客户端（自定义，基于 requests）
import logging  # 标准库

import requests  # 第三方：HTTP 客户端，来源 requests 包

from tests.utils.config import Config  # 自定义调用：BASE_URL 等

logger = logging.getLogger(__name__)  # 标准库：模块 logger


class ShopApiClient:  # 自定义：封装 /api/v1 接口调用
    """真实环境 API 客户端；使用 Session 保持 cookie 与 UI 测试隔离。"""  # 自定义文档

    def __init__(self, base_url=None):  # 自定义构造
        self.base_url = (base_url or Config.BASE_URL).rstrip("/")  # 自定义：根 URL
        self.api_prefix = f"{self.base_url}/api/v1"  # 自定义：API 前缀
        self.session = requests.Session()  # 第三方：可复用 cookie 的 Session

    def _url(self, path):  # 自定义：拼完整 URL
        return f"{self.api_prefix}{path}"  # 自定义返回

    def _request(self, method, path, **kwargs):  # 自定义：统一请求与日志
        url = self._url(path)  # 自定义
        logger.info("API %s %s body=%s", method, url, kwargs.get("json"))  # 自定义日志
        resp = self.session.request(method, url, timeout=kwargs.pop("timeout", 30), **kwargs)  # 第三方：发请求
        logger.info("API 响应 status=%s body=%s", resp.status_code, resp.text[:500])  # 自定义：截断日志
        return resp  # 自定义返回 Response

    def login(self, email=None, password=None):  # 自定义：POST /auth/login
        payload = {"email": email or Config.TEST_USER, "password": password or Config.TEST_PASSWORD}  # 自定义
        return self._request("POST", "/auth/login", json=payload)  # 自定义调用 _request

    def list_products(self):  # 自定义：GET /products
        return self._request("GET", "/products")  # 自定义

    def get_product(self, sku_id):  # 自定义：GET /products/{sku}
        return self._request("GET", f"/products/{sku_id}")  # 自定义

    def get_cart(self):  # 自定义：GET /cart
        return self._request("GET", "/cart")  # 自定义

    def add_cart_item(self, sku_id, quantity=1):  # 自定义：POST /cart/items
        return self._request("POST", "/cart/items", json={"sku_id": sku_id, "quantity": quantity})  # 自定义

    def update_cart_item(self, sku_id, quantity):  # 自定义：PUT /cart/items/{sku}
        return self._request("PUT", f"/cart/items/{sku_id}", json={"quantity": quantity})  # 自定义

    def delete_cart_item(self, sku_id):  # 自定义：DELETE /cart/items/{sku}
        return self._request("DELETE", f"/cart/items/{sku_id}")  # 自定义

    def clear_cart(self):  # 自定义：POST /cart/clear
        return self._request("POST", "/cart/clear")  # 自定义

    def checkout(self):  # 自定义：POST /orders/checkout
        return self._request("POST", "/orders/checkout")  # 自定义

    def get_order(self, order_id):  # 自定义：GET /orders/{id}
        return self._request("GET", f"/orders/{order_id}")  # 自定义

    def payment_confirm(self, order_id, action="success", payment_id=None):  # 自定义：POST /payment/confirm
        payload = {"order_id": order_id, "action": action}  # 自定义 body
        if payment_id:  # 自定义：可选指定 payment_id 测幂等
            payload["payment_id"] = payment_id  # 自定义
        return self._request("POST", "/payment/confirm", json=payload)  # 自定义

    @staticmethod  # 自定义：解析 JSON 并断言业务 code
    def parse_json(resp):  # 自定义：辅助解析
        return resp.json()  # 第三方：Response.json()

    @staticmethod  # 自定义
    def assert_ok(resp, expected_code=0):  # 自定义：HTTP + 业务码断言 helper
        body = resp.json()  # 第三方
        assert resp.status_code == 200, body  # 框架 assert
        assert body["code"] == expected_code, body  # 框架 assert
        return body["data"]  # 自定义返回 data 字段
