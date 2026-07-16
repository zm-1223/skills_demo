# run_server.py — 启动 demo_shop 演示站点（自定义入口脚本）
import sys  # 标准库：修改 module 搜索路径
from pathlib import Path  # 标准库：路径

ROOT = Path(__file__).resolve().parent  # 自定义：项目根目录
sys.path.insert(0, str(ROOT))  # 标准库：确保可 import demo_shop

from demo_shop.app import app  # 自定义调用：Flask app，来源 demo_shop.app

if __name__ == "__main__":  # 自定义：直接运行入口
    print("Demo Shop 运行在 http://127.0.0.1:5000")  # 自定义：控制台提示
    app.run(host="127.0.0.1", port=5000, debug=True)  # 框架调用：Flask 开发服务器
