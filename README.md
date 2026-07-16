# skills_demo

Cursor Agent Skills 示例仓库。

## 已包含 Skills

### ecommerce-cart-payment-tests

路径：`.cursor/skills/ecommerce-cart-payment-tests/`

用于设计与编写**电商平台购物车、结算、支付**相关的 **UI/E2E 自动化**测试用例与脚本。当对话涉及购物车、结算、支付、下单或电商购物流程测试时，Agent 会自动参考该 Skill。

**目录结构：**

```
.cursor/skills/ecommerce-cart-payment-tests/
├── SKILL.md                 # 主指令：UI/E2E、等待、弹窗、日志、报告
├── test-case-template.md    # 单条用例与 UI 断言模板
└── examples.md              # Playwright/Selenium 与 conftest 示例
```

**使用方式：**

1. 在 Cursor 中打开本仓库，Skill 作为项目级 Skill 生效
2. 在对话中描述需求，例如：
   - 「帮我设计购物车 UI 测试用例」
   - 「写从加购到沙箱支付成功的 Playwright E2E」
   - 「失败自动截图和 pytest-html 报告怎么配」

**Skill 核心约定：**

| 项 | 说明 |
|----|------|
| 测试类型 | 仅 UI/E2E，不含 API 测试 |
| 环境 | 真实测试/预发环境 + 官方支付沙箱，不用 mock |
| 等待 | 显式等待为主、隐性超时兜底，禁止 sleep |
| 弹窗 | 步骤级局部处理，禁止全局扫描关闭 |
| 日志 | 自动生成 `logs/test_*.log` |
| 报告 | pytest-html / Allure + 失败截图 `reports/screenshots/` |

**覆盖范围：**

- 购物车：加购、改数量、删除、合并、库存边界
- 结算：地址、运费、优惠券、积分、金额展示
- 支付：真实沙箱跳转、成功/失败/取消
- 订单：支付后页面状态展示

## 本地开发

```bash
python main.py
```
