# 购物车与支付测试用例模板（UI + 接口）

> 设计用例前先查阅 [SKILL.md](SKILL.md) 中的 **测试范围矩阵** 与各模块测试清单。

## 单条用例模板

```markdown
### [ID] 用例标题

- **优先级**: P0 | P1 | P2
- **模块**: 购物车 | 结算 | 支付 | 订单 | 登录
- **类型**: API | UI | UI+API
- **环境**: 测试/预发 URL + /api/v1（真实环境，非 mock）
- **前置条件**:
  - 测试账号 / 独立 session
  - 商品 SKU 库存充足
- **测试数据**:
  | 字段 | 值 |
  |------|-----|
  | sku_id | |
  | quantity | |
  | expectedTotal | |
- **步骤（API）**:
  1. POST /api/v1/cart/items
  2. GET /api/v1/cart 断言
- **步骤（UI）**:
  1. 打开商品页 → 按需关 cookie
  2. 点击加购 → 显式等待 toast/角标
- **预期结果（API）**:
  - HTTP 200, code=0
  - data.items[0].quantity = 1
- **预期结果（UI）**:
  - 角标 = 1
  - 支付成功页文案
- **弹窗处理点**（仅 UI）:
  | 步骤后 | 弹窗 | 处理 |
  |--------|------|------|
  | 提交订单 | 价格变动 | 局部等待并确认 |
- **清理**: clear_cart / 取消订单
- **POM（UI 必填）**:
  | 字段 | 值 |
  |------|-----|
  | Page 类 | ProductPage / CartPage / ... |
  | 编排方法 | open_product → add_to_cart → ... |
  | 断言位置 | test 层 assert，Page 只返回值 |
```

## 测试计划总表

```markdown
# [项目名] 购物车与支付测试计划

## 环境
- Base URL: https://test.example.com
- API: /api/v1
- 日志: logs/
- 报告: reports/report.html
- UI 失败截图: reports/screenshots/

## 范围
- In: API 契约 + UI 关键路径 + 真实沙箱支付
- Out: mock 支付、物流售后（除非指定）

## 用例列表
| ID | 优先级 | 模块 | 标题 | API | UI |
|----|--------|------|------|-----|-----|
| API-CART-001 | P0 | 购物车 | 加购 | Y | — |
| CART-001 | P0 | 购物车 | 加购角标 | — | Y |
```

## POM 检查表（UI 用例）

```
- [ ] locator 全部在 tests/pages/ 内
- [ ] test_*.py 无 find_element / By / WebDriverWait
- [ ] Page 继承 BasePage，一页面一文件
- [ ] Page 方法名体现业务动作
- [ ] 显式等待在 Page 方法内，不在 test 内
- [ ] assert 在 test 层；Page 返回待断言数据
- [ ] 弹窗由 Page 步骤后调用 PopupHelper
```

## API 断言检查表

```
- [ ] HTTP status code
- [ ] body.code（业务码）
- [ ] body.message
- [ ] body.data 结构与字段值
- [ ] 错误场景 code 与 HTTP 状态匹配

购物车 API
- [ ] items[].sku_id, quantity, line_total
- [ ] cart_total 一致
- [ ] item_count

订单 API
- [ ] order_id 唯一
- [ ] status 状态机
- [ ] total = subtotal + shipping

支付 API
- [ ] 成功后 status=PAID
- [ ] 重复 payment_id 幂等
- [ ] 取消后 status=PENDING_PAYMENT
```

## UI 断言检查表

```
- [ ] 显式等待关键元素
- [ ] 角标/金额/订单文案
- [ ] 沙箱支付页跳转与回站
- [ ] 失败截图 + 日志 + HTML 报告
```

## 等待策略（UI）

```
- [ ] 无 time.sleep
- [ ] 隐性等待 setup 一次
- [ ] 显式 WebDriverWait 用于关键步骤
- [ ] 弹窗仅步骤级局部处理
```

## API Client 检查表

```
- [ ] 使用 requests.Session 保持 cookie
- [ ] 每用例独立 session / clear_cart
- [ ] 请求与响应写 logging
- [ ] ShopApiClient.assert_ok 统一断言
```

## 订单状态机

```
PENDING_PAYMENT → PAID（支付成功）
               ↘ 保持 PENDING（取消/失败）
```

API 断言 `data.status`；UI 断言页面文案或 `data-testid`。
