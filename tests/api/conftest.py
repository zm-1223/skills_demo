# tests/api/conftest.py — API 测试 fixture + Allure 失败附件（框架 pytest + 自定义 client）
import logging  # 标准库

import allure  # 第三方：Allure 附件，来源 allure-pytest
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


@pytest.hookimpl(hookwrapper=True, tryfirst=True)  # 框架 hook：API 失败时附加响应到 Allure
def pytest_runtest_makereport(item, call):  # 自定义：与 e2e conftest 同名 hook，pytest 会合并调用
    outcome = yield  # 框架 hookwrapper
    report = outcome.get_result()  # 框架
    if report.when == "call" and report.failed:  # 自定义：call 阶段失败
        api_client = item.funcargs.get("api_client") or item.funcargs.get("auth_api_client")  # 自定义
        if api_client is not None and getattr(api_client, "last_response", None):  # 自定义：有最近响应
            resp = api_client.last_response  # 自定义
            body = f"status={resp.status_code}\nurl={resp.url}\n\n{resp.text}"  # 自定义摘要
            allure.attach(body, name="last_api_response", attachment_type=allure.attachment_type.TEXT)  # 第三方
