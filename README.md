# skills_demo

Cursor Agent Skills 示例仓库。

## 已包含 Skills

### ecommerce-cart-payment-tests

路径：`.cursor/skills/ecommerce-cart-payment-tests/`

用于设计与编写**电商平台购物车、结算、支付**相关的自动化测试用例与脚本。当对话涉及购物车、结算、支付、下单或电商购物流程测试时，Agent 会自动参考该 Skill。

**目录结构：**

```
.cursor/skills/ecommerce-cart-payment-tests/
├── SKILL.md                 # 主指令：范围、清单、实现原则、输出格式
├── test-case-template.md    # 单条用例与测试计划模板
└── examples.md              # 用例清单与 pytest/Playwright 示例
```

**使用方式：**

1. 在 Cursor 中打开本仓库，Skill 作为项目级 Skill 生效
2. 在对话中描述需求，例如：
   - 「帮我设计购物车 API 测试用例」
   - 「写从加购到支付成功的 pytest 自动化」
   - 「支付回调幂等怎么测」

**Skill 覆盖范围：**

- 购物车：加购、改数量、删除、合并、库存边界
- 结算：地址、运费、优惠券、积分、金额一致性
- 支付：发起、成功/失败、超时、回调幂等、沙箱隔离
- 订单：状态流转与清理策略

## 本地开发

```bash
python main.py
```
