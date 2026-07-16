# skills_demo

Cursor Agent Skills 示例仓库，内含 **UI + 接口双层可运行** 的电商自动化测试工程。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

安装 **Allure Commandline**（生成 HTML 需要，需 Java）：

- https://github.com/allure-framework/allure2/releases
- Windows：`scoop install allure`

### 2. 启动演示站点（终端 1）

```bash
python run_server.py
```

- 浏览器 UI：http://127.0.0.1:5000
- REST API：http://127.0.0.1:5000/api/v1
- 测试账号：`test@demo.com` / `123456`

### 3. 运行测试（终端 2）

```bash
pytest                              # 采集 Allure 结果
python generate_allure_report.py    # 生成浏览器可打开 HTML
```

### 4. 查看结果

| 类型 | 路径 | 打开方式 |
|------|------|----------|
| Allure HTML 站点 | `reports/allure-report/index.html` | 双击或浏览器打开文件 |
| Allure 单文件 HTML | `reports/allure-report.html` | 双击或浏览器打开文件 |
| 运行日志 | `logs/test_*.log` | 文本编辑器 |
| UI 失败截图 | `reports/screenshots/` + Allure 附件 | 报告内查看 |

```bash
pytest -m api           # 仅接口
pytest -m ui            # 仅 UI
```

环境变量见 `.env.example`。

## 项目结构

```
skills_demo/
├── demo_shop/
├── tests/
│   ├── api/
│   ├── e2e/
│   ├── clients/
│   └── pages/
├── generate_allure_report.py    # Allure → 浏览器 HTML
├── .cursor/skills/ecommerce-cart-payment-tests/
├── pytest.ini
└── run_server.py
```

## Cursor Skill

约定摘要：

- **Allure 报告**：pytest 采集 + `generate_allure_report.py` 生成 HTML
- **测试范围矩阵**、POM、重试、UI+API 双层（详见 SKILL.md）

## 常用命令

```bash
pytest
python generate_allure_report.py
pytest -m api
pytest -m ui --reruns 2 --reruns-delay 1
allure open reports/allure-report   # 可选：本地服务预览
```

## 本地开发

```bash
python main.py
```
