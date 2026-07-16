# tests/conftest.py — 全局 pytest：日志、Allure 环境信息（UI + API 共用，自定义）
import logging  # 标准库：logging 模块
import platform  # 标准库：操作系统信息，供 Allure 环境块
from datetime import datetime  # 标准库：时间戳
from pathlib import Path  # 标准库：目录操作

import pytest  # 框架：pytest hook

from tests.utils.config import Config  # 自定义：BASE_URL 等


def _ensure_dirs():  # 自定义：创建 logs/reports 目录
    Path("logs").mkdir(exist_ok=True)  # 标准库
    Path("reports/screenshots").mkdir(parents=True, exist_ok=True)  # 标准库
    Path("reports/allure-results").mkdir(parents=True, exist_ok=True)  # 标准库：Allure 原始结果


def pytest_configure(config):  # 框架 hook：pytest 启动时执行
    _ensure_dirs()  # 自定义调用
    log_file = Path("logs") / f"test_{datetime.now():%Y%m%d_%H%M%S}.log"  # 自定义：带时间戳日志文件
    logging.basicConfig(  # 标准库：配置 root logger
        level=logging.INFO,  # 自定义：INFO 级别
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",  # 自定义格式
        handlers=[  # 自定义：双输出 handler
            logging.FileHandler(log_file, encoding="utf-8"),  # 标准库：写文件
            logging.StreamHandler(),  # 标准库：控制台
        ],
        force=True,  # 标准库：覆盖已有 logging 配置
    )
    logging.info("测试会话开始，日志: %s", log_file)  # 自定义


@pytest.fixture(scope="session", autouse=True)  # 框架：会话级自动 fixture
def allure_environment():  # 自定义：写入 Allure 报告 Environment 区块
    env_path = Path("reports/allure-results/environment.properties")  # 自定义：Allure 环境文件路径
    env_path.parent.mkdir(parents=True, exist_ok=True)  # 标准库
    lines = [  # 自定义：环境键值对
        f"Base.URL={Config.BASE_URL}",  # 自定义：被测 URL
        f"API.Prefix={Config.API_PREFIX}",  # 自定义：API 前缀
        f"Python={platform.python_version()}",  # 标准库：Python 版本
        f"OS={platform.system()} {platform.release()}",  # 标准库：操作系统
    ]
    env_path.write_text("\n".join(lines), encoding="utf-8")  # 标准库：会话开始前写入
    logging.info("Allure environment 已写入: %s", env_path)  # 自定义
    yield  # 框架：保持 fixture 存活至会话结束


def pytest_sessionfinish(session, exitstatus):  # 框架 hook：测试会话结束
    logging.info(  # 自定义：提示生成 HTML 报告命令
        "Allure 原始结果: reports/allure-results — 生成浏览器 HTML: python generate_allure_report.py"
    )
