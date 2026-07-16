# generate_allure_report.py — 将 Allure 结果生成为浏览器可打开的 HTML 报告（自定义脚本）
import shutil  # 标准库：检测 allure 命令是否在 PATH 中
import subprocess  # 标准库：调用 allure generate / allure-combine
import sys  # 标准库：退出码与 executable 路径
from pathlib import Path  # 标准库：路径操作

RESULTS_DIR = Path("reports/allure-results")  # 自定义：pytest --alluredir 输出目录
REPORT_DIR = Path("reports/allure-report")  # 自定义：allure generate 静态站点目录
COMPLETE_HTML = Path("reports/allure-report-complete.html")  # 自定义：单文件 HTML，便于浏览器直接打开


def _require_results():  # 自定义：校验是否已运行 pytest 产出结果
    if not RESULTS_DIR.exists() or not any(RESULTS_DIR.iterdir()):  # 自定义：目录空则报错
        print("未找到 Allure 结果，请先运行：pytest --alluredir=reports/allure-results")  # 自定义提示
        sys.exit(1)  # 标准库：非零退出


def _generate_allure_site():  # 自定义：调用 Allure CLI 生成静态报告站
    allure_bin = shutil.which("allure")  # 标准库：查找 allure 可执行文件
    if not allure_bin:  # 自定义：未安装 CLI
        print("未找到 Allure 命令行，请安装后重试。")  # 自定义
        print("  Windows: scoop install allure")  # 自定义
        print("  macOS:   brew install allure")  # 自定义
        print("  文档: https://allurereport.org/docs/install/")  # 自定义
        sys.exit(1)  # 标准库
    REPORT_DIR.mkdir(parents=True, exist_ok=True)  # 标准库：确保输出目录存在
    cmd = [allure_bin, "generate", str(RESULTS_DIR), "-o", str(REPORT_DIR), "--clean"]  # 自定义命令
    print("执行:", " ".join(cmd))  # 自定义
    subprocess.run(cmd, check=True)  # 标准库：框架级 subprocess 调用外部 allure


def _combine_single_html():  # 自定义：allure-combine 合并为单 HTML 文件
    combined_src = Path("reports/complete.html")  # 自定义：allure-combine 默认输出名
    combine_bin = shutil.which("allure-combine")  # 标准库：查找 allure-combine CLI
    if not combine_bin:  # 自定义：未安装则跳过单文件合并
        print("未找到 allure-combine，跳过单文件 HTML。请 pip install allure-combine")  # 自定义
        return  # 自定义
    cmd = [  # 自定义：allure-combine 命令
        combine_bin,  # 第三方 CLI
        str(REPORT_DIR),  # 自定义：输入 allure-report 目录
        "--dest",  # 第三方参数
        "reports",  # 自定义：单文件写到 reports/
        "--auto-create-folders",  # 第三方：自动建目录
    ]
    print("执行:", " ".join(cmd))  # 自定义
    subprocess.run(cmd, check=True)  # 标准库
    if combined_src.exists():  # 自定义：合并成功则复制为固定文件名
        shutil.copy(combined_src, COMPLETE_HTML)  # 标准库：复制到 allure-report-complete.html
        print(f"单文件报告: {COMPLETE_HTML.resolve()}")  # 自定义：可直接用浏览器 file:// 打开


def main():  # 自定义：脚本入口
    _require_results()  # 自定义调用
    _generate_allure_site()  # 自定义调用
    _combine_single_html()  # 自定义调用
    index = (REPORT_DIR / "index.html").resolve()  # 自定义：多文件报告入口
    print(f"Allure 站点报告: {index}")  # 自定义
    print("浏览器打开上述路径，或双击 allure-report-complete.html")  # 自定义


if __name__ == "__main__":  # 自定义：python generate_allure_report.py
    main()  # 自定义调用
