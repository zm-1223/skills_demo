# tests/pages/login_page.py — 登录页 Page Object（自定义）
import logging  # 标准库

from tests.pages.base_page import BasePage  # 自定义调用：基类
from tests.utils.wait_helper import WaitHelper  # 自定义调用

logger = logging.getLogger(__name__)  # 标准库


class LoginPage(BasePage):  # 自定义：登录页
    PATH = "/login"  # 自定义：路由路径

    def open_login(self):  # 自定义：进入登录页
        self.open(self.PATH)  # 自定义调用：BasePage.open

    def login(self, email, password):  # 自定义：执行登录
        logger.info("登录账号: %s", email)  # 自定义日志
        email_by, email_loc = WaitHelper.by_testid("login-email")  # 自定义
        pwd_by, pwd_loc = WaitHelper.by_testid("login-password")  # 自定义
        submit_by, submit_loc = WaitHelper.by_testid("login-submit-btn")  # 自定义
        self.wait.until_visible(email_by, email_loc).clear()  # 框架调用：WebElement.clear
        self.wait.until_visible(email_by, email_loc).send_keys(email)  # 框架调用：send_keys
        self.wait.until_visible(pwd_by, pwd_loc).clear()  # 框架调用
        self.wait.until_visible(pwd_by, pwd_loc).send_keys(password)  # 框架调用
        self.wait.until_clickable(submit_by, submit_loc).click()  # 框架调用 click
        self.wait.until_url_contains("/")  # 自定义调用：登录后跳转
