# generate_allure_report.py — 将 allure-results 生成为浏览器可打开的 HTML 报告（自定义脚本）
import logging  # 标准库：日志输出
import shutil  # 标准库：检测 allure 命令是否在 PATH
import subprocess  # 标准库：调用 allure generate 外部命令
import sys  # 标准库：退出码与 argv
from pathlib import Path  # 标准库：路径处理

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")  # 标准库：脚本日志格式
logger = logging.getLogger(__name__)  # 标准库：模块 logger

RESULTS_DIR = Path("reports/allure-results")  # 自定义：pytest --alluredir 输出目录
REPORT_DIR = Path("reports/allure-report")  # 自定义：allure generate 静态站点目录
SINGLE_HTML = Path("reports/allure-report.html")  # 自定义：allure-combine 单文件 HTML


def _find_allure_cmd():  # 自定义：查找 allure 可执行文件
    return shutil.which("allure")  # 标准库：在 PATH 中查找 allure 命令


def generate_allure_site():  # 自定义：调用 Allure CLI 生成静态报告目录
    allure_cmd = _find_allure_cmd()  # 自定义调用
    if not allure_cmd:  # 自定义：未安装 CLI
        logger.error("未找到 allure 命令。请安装 Allure Commandline（需 Java）后重试。")  # 自定义
        logger.error("参考: https://github.com/allure-framework/allure2/releases")  # 自定义
        logger.error("Windows 示例: scoop install allure  或下载 zip 并加入 PATH")  # 自定义
        return False  # 自定义：失败返回
    if not RESULTS_DIR.exists() or not any(RESULTS_DIR.iterdir()):  # 自定义：无结果数据
        logger.error("目录 %s 为空或不存在，请先运行: pytest --alluredir=reports/allure-results", RESULTS_DIR)  # 自定义
        return False  # 自定义
    REPORT_DIR.mkdir(parents=True, exist_ok=True)  # 标准库：确保父目录存在
    cmd = [  # 自定义：allure generate 命令参数列表
        allure_cmd,  # 自定义：allure 可执行路径
        "generate",  # 自定义：子命令 generate
        str(RESULTS_DIR),  # 自定义：输入 results
        "-o",  # 自定义：输出参数
        str(REPORT_DIR),  # 自定义：输出目录
        "--clean",  # 自定义：清理旧报告
    ]
    logger.info("执行: %s", " ".join(cmd))  # 自定义
    result = subprocess.run(cmd, check=False)  # 标准库：运行外部命令
    if result.returncode != 0:  # 自定义：命令失败
        logger.error("allure generate 失败，退出码 %s", result.returncode)  # 自定义
        return False  # 自定义
    logger.info("静态报告已生成: %s/index.html （可用浏览器直接打开）", REPORT_DIR.resolve())  # 自定义
    return True  # 自定义：成功


def combine_single_html():  # 自定义：合并为单个 HTML 文件便于分享
    try:  # 自定义：捕获 import 失败
        from allure_combine import combine_allure  # 第三方：allure-combine 包
    except ImportError:  # 自定义
        logger.warning("未安装 allure-combine，跳过单文件 HTML。可执行: pip install allure-combine")  # 自定义
        return False  # 自定义
    if not REPORT_DIR.exists():  # 自定义
        logger.error("请先成功执行 allure generate")  # 自定义
        return False  # 自定义
    dest_folder = str(Path("reports"))  # 自定义：输出到 reports/ 目录
    combine_allure(  # 第三方调用：合并为 complete.html
        str(REPORT_DIR),  # 自定义：allure generate 输出目录
        dest_folder=dest_folder,  # 自定义：单文件输出目录
        remove_temp_files=True,  # 自定义
        auto_create_folders=True,  # 自定义
    )
    combined = Path(dest_folder) / "complete.html"  # 自定义：allure-combine 固定输出名
    if combined.exists():  # 自定义
        if SINGLE_HTML.exists():  # 自定义：删除旧文件
            SINGLE_HTML.unlink()  # 标准库
        combined.replace(SINGLE_HTML)  # 标准库：重命名为 allure-report.html
        logger.info("单文件报告: %s （双击用浏览器打开）", SINGLE_HTML.resolve())  # 自定义
        return True  # 自定义
    logger.warning("allure-combine 未生成 complete.html")  # 自定义
    return False  # 自定义


def main():  # 自定义：脚本入口
    ok = generate_allure_site()  # 自定义调用：生成静态站点
    if ok:  # 自定义
        combine_single_html()  # 自定义调用：可选单文件
    sys.exit(0 if ok else 1)  # 标准库：进程退出码


if __name__ == "__main__":  # 自定义：直接运行入口
    main()  # 自定义调用
