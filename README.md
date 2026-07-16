# skills_demo

Cursor Agent Skills 示例仓库，内含 **UI + 接口双层可运行** 的电商自动化测试工程。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动演示站点（终端 1）

```bash
python run_server.py
```

- 浏览器 UI：http://127.0.0.1:5000
- REST API：http://127.0.0.1:5000/api/v1
- 测试账号：`test@demo.com` / `123456`

### 3. 运行测试（终端 2）

```bash
pytest                  # UI + API 全部
pytest -m api           # 仅接口（无需浏览器，速度快）
pytest -m ui            # 仅 UI E2E
```

### 4. 查看 Allure 报告

```bash
python generate_allure_report.py
```

| 类型 | 路径 |
|------|------|
| **单文件 HTML（浏览器直接打开）** | `reports/allure-report-complete.html` |
| Allure 站点 | `reports/allure-report/index.html` |
| 原始结果 | `reports/allure-results/` |
| 运行日志 | `logs/test_*.log` |
| UI 失败截图 | `reports/screenshots/`（并 attach 到 Allure） |

需安装 Allure CLI：`scoop install allure`（Windows）或见 [官方文档](https://allurereport.org/docs/install/)。

环境变量见 `.env.example`。

## 项目结构

```
skills_demo/
├── demo_shop/
│   ├── app.py                 # UI 路由
│   ├── api_routes.py          # REST API /api/v1/*
│   └── common.py              # UI/API 共享业务逻辑
├── tests/
│   ├── conftest.py            # 全局日志
│   ├── api/                   # 接口测试（pytest + requests）
│   │   ├── test_cart_api.py
│   │   └── test_order_payment_api.py
│   ├── e2e/                   # UI 测试（pytest + Selenium）
│   │   ├── test_cart.py
│   │   └── test_checkout_payment.py
│   ├── clients/shop_api_client.py
│   └── pages/                 # POM Page Object（UI 强制）
├── .cursor/skills/ecommerce-cart-payment-tests/
│   ├── SKILL.md
│   ├── case.md                # 用例范围、数量、前置、数据
│   └── ...
├── pytest.ini
├── generate_allure_report.py  # Allure HTML 生成
└── run_server.py
```

## 双层测试策略

| 层级 | 技术 | 职责 |
|------|------|------|
| **接口** | pytest + requests | 业务逻辑、契约、边界、幂等、快速回归 |
| **UI** | pytest + Selenium | 用户路径、页面交互、弹窗、沙箱支付页 |

## Cursor Skill

路径：`.cursor/skills/ecommerce-cart-payment-tests/`

约定摘要：

- **测试范围矩阵**与 [case.md](case.md)（用例数量、前置、数据）
- UI + API 双层，真实环境，禁止 mock
- **POM 强制** / **Token 复用** / **flaky(reruns=2, reruns_delay=1)**
- **Allure 报告**：pytest → `generate_allure_report.py` → `allure-report-complete.html` 浏览器打开
- **不含**：性能/压力/负载/benchmark 测试
- API：`ShopApiClient` + **auth_token 复用** + `code/data` 断言
- UI：POM、显式/隐性等待、按需弹窗、Allure 失败截图

## 用例一览

### 接口（API-*）

| ID | 说明 |
|----|------|
| API-CART-001~005 | 加购、合并、超库存、删除、改数量 |
| API-CHK-001~002 | 下单、空车失败 |
| API-PAY-001~003 | 支付成功、取消、幂等 |
| API-AUTH-001~002 | 登录成功/失败 |

### UI（CART/CHK/PAY/AUTH-*）

| ID | 说明 |
|----|------|
| CART-001~004 | 加购、累加、改数量、删除 |
| CHK-001~002 | 结算金额、价格变动弹窗 |
| PAY-001~002 | 支付成功、取消 |
| AUTH-001 | 登录 |

## API 端点

```
POST   /api/v1/auth/login
GET    /api/v1/products
GET    /api/v1/cart
POST   /api/v1/cart/items
PUT    /api/v1/cart/items/{sku}
DELETE /api/v1/cart/items/{sku}
POST   /api/v1/orders/checkout
GET    /api/v1/orders/{id}
POST   /api/v1/payment/confirm
```

## 常用命令

```bash
pytest
python generate_allure_report.py   # 生成 HTML 报告
pytest -m api               # 仅接口
pytest -m ui                # 仅 UI
pytest -m cart              # 两层购物车
pytest -m payment           # 两层支付
pytest -m ui                # 仅 UI（含 flaky 重试）
HEADLESS=true pytest -m ui  # UI 无头
```

## 本地开发

```bash
python main.py
```
