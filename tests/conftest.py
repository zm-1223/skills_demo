# tests/conftest.py — 全局 pytest 配置：日志（UI + API 共用，自定义）
import logging  # 标准库：logging
from datetime import datetime  # 标准库：时间戳
from pathlib import Path  # 标准库：目录


def _ensure_dirs():  # 自定义：创建 logs/reports 目录
    Path("logs").mkdir(exist_ok=True)  # 标准库
    Path("reports/screenshots").mkdir(parents=True, exist_ok=True)  # 标准库


def pytest_configure(config):  # 框架 hook：pytest 启动时配置日志（来源 pytest）
    _ensure_dirs()  # 自定义调用
    log_file = Path("logs") / f"test_{datetime.now():%Y%m%d_%H%M%S}.log"  # 自定义日志路径
    logging.basicConfig(  # 标准库：配置 root logger
        level=logging.INFO,  # 自定义级别
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",  # 自定义格式
        handlers=[  # 自定义双输出
            logging.FileHandler(log_file, encoding="utf-8"),  # 标准库：文件
            logging.StreamHandler(),  # 标准库：控制台
        ],
        force=True,  # 标准库：覆盖已有配置
    )
    logging.info("测试会话开始，日志: %s", log_file)  # 自定义
