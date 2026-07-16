# tests/utils/config.py — 读取 E2E 测试环境配置（自定义模块）
import os  # 标准库：读取环境变量，来源 Python 内置


class Config:  # 自定义类：集中管理测试配置项
    """测试配置；优先从环境变量读取，便于 CI 与本地切换。"""  # 自定义：类文档

    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")  # 自定义：被测站点根 URL，默认本地 demo_shop
    TEST_USER = os.getenv("TEST_USER", "test@demo.com")  # 自定义：登录邮箱
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "123456")  # 自定义：登录密码
    DEFAULT_SKU = os.getenv("DEFAULT_SKU", "sku-001")  # 自定义：默认加购 SKU
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "5"))  # 自定义：Selenium 隐性等待秒数
    EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "10"))  # 自定义：显式等待默认秒数
    PAYMENT_WAIT = int(os.getenv("PAYMENT_WAIT", "30"))  # 自定义：支付相关长等待秒数
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"  # 自定义：是否无头浏览器
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")  # 自定义：REST API 路径前缀

    @classmethod  # 自定义：类方法装饰器
    def api_url(cls, path=""):  # 自定义：拼接 API 完整 URL
        base = cls.BASE_URL.rstrip("/")  # 自定义
        prefix = cls.API_PREFIX if cls.API_PREFIX.startswith("/") else f"/{cls.API_PREFIX}"  # 自定义
        return f"{base}{prefix}{path}"  # 自定义返回

    @classmethod  # 自定义：类方法装饰器
    def product_url(cls, sku_id=None):  # 自定义：拼接商品页 URL
        sku = sku_id or cls.DEFAULT_SKU  # 自定义：SKU 默认 DEFAULT_SKU
        return f"{cls.BASE_URL}/product/{sku}"  # 自定义：返回完整商品 URL 字符串

    @classmethod  # 自定义
    def checkout_url(cls, price_change=False):  # 自定义：结算页 URL，可选价格变动场景
        url = f"{cls.BASE_URL}/checkout"  # 自定义：基础结算路径
        if price_change:  # 自定义：需要弹窗场景时加 query
            url += "?price_change=1"  # 自定义：触发 demo_shop 价格变动弹窗
        return url  # 自定义返回
