# tests/api/conftest.py — API 测试 fixture（框架 pytest + 自定义 client）
import logging  # 标准库

import pytest  # 框架：pytest fixture

from tests.clients.shop_api_client import ShopApiClient  # 自定义调用：API 客户端

logger = logging.getLogger(__name__)  # 标准库


@pytest.fixture  # 框架装饰器：每个用例独立 Session
def api_client():  # 自定义：无登录态 API 客户端
    client = ShopApiClient()  # 自定义实例化
    client.clear_cart()  # 自定义调用：清理购物车，保证用例隔离
    yield client  # 框架 yield 给用例
    client.clear_cart()  # 自定义 teardown 清理


@pytest.fixture  # 框架装饰器
def auth_api_client(api_client):  # 自定义：已登录 API 客户端
    resp = api_client.login()  # 自定义调用登录
    assert resp.status_code == 200, resp.text  # 框架 assert
    body = resp.json()  # 第三方
    assert body["code"] == 0, body  # 框架 assert
    logger.info("API 登录成功: %s", body["data"]["email"])  # 自定义
    yield api_client  # 框架


@pytest.fixture  # 框架装饰器
def log_api_test(request):  # 自定义：API 用例边界日志
    logger.info("===== API 用例开始: %s =====", request.node.name)  # 自定义
    yield  # 框架
    logger.info("===== API 用例结束: %s =====", request.node.name)  # 自定义
