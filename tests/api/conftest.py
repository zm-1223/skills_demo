# tests/api/conftest.py — API fixture：token 复用、Allure 附件（框架 pytest + 自定义 client）
import logging  # 标准库

import allure  # 第三方：Allure 附件，来源 allure-pytest
import pytest  # 框架：pytest fixture

from tests.clients.shop_api_client import ShopApiClient  # 自定义调用：API 客户端

logger = logging.getLogger(__name__)  # 标准库


@pytest.fixture(scope="session")  # 框架：整个 pytest 会话只登录一次
def auth_token():  # 自定义：session 级 token（Flask session cookie + 逻辑 token）
    """登录一次，供后续用例复用 token/session，禁止每条用例重复 login。"""  # 自定义文档
    client = ShopApiClient()  # 自定义：独立 client 用于登录
    resp = client.login()  # 自定义：POST /auth/login
    assert resp.status_code == 200, resp.text  # 框架 assert
    body = resp.json()  # 第三方
    assert body["code"] == 0, body  # 框架 assert
    logger.info("Session 级 auth_token 已获取: %s", body["data"]["email"])  # 自定义
    return client  # 自定义：返回已登录 client（cookie 在 session 中）


@pytest.fixture  # 框架装饰器：每个用例独立 Session，但不重复登录
def api_client():  # 自定义：无登录态 API 客户端（购物车等用例）
    client = ShopApiClient()  # 自定义实例化
    client.clear_cart()  # 自定义：清理购物车，保证隔离
    yield client  # 框架 yield
    client.clear_cart()  # 自定义 teardown


@pytest.fixture  # 框架装饰器
def auth_api_client(auth_token):  # 自定义：复用 session token 的已登录 client
    client = ShopApiClient()  # 自定义：新 client 实例
    client.reuse_auth_from(auth_token)  # 自定义：复制 cookie/token，不再次 login
    client.clear_cart()  # 自定义：用例级仍清购物车
    yield client  # 框架
    client.clear_cart()  # 自定义 teardown


@pytest.fixture  # 框架装饰器
def log_api_test(request):  # 自定义：API 用例边界日志
    logger.info("===== API 用例开始: %s =====", request.node.name)  # 自定义
    yield  # 框架
    logger.info("===== API 用例结束: %s =====", request.node.name)  # 自定义


@pytest.hookimpl(hookwrapper=True, tryfirst=True)  # 框架 hook：API 失败时附加响应到 Allure
def pytest_runtest_makereport(item, call):  # 自定义
    outcome = yield  # 框架 hookwrapper
    report = outcome.get_result()  # 框架
    if report.when == "call" and report.failed:  # 自定义：call 阶段失败
        api_client = item.funcargs.get("api_client") or item.funcargs.get("auth_api_client")  # 自定义
        if api_client is not None and getattr(api_client, "last_response", None):  # 自定义
            resp = api_client.last_response  # 自定义
            body = f"status={resp.status_code}\nurl={resp.url}\n\n{resp.text}"  # 自定义摘要
            allure.attach(body, name="last_api_response", attachment_type=allure.attachment_type.TEXT)  # 第三方
