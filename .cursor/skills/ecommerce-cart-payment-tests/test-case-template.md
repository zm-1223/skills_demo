# 购物车与支付测试用例模板

## 单条用例模板

```markdown
### [ID] 用例标题

- **优先级**: P0 | P1 | P2
- **模块**: 购物车 | 结算 | 支付 | 订单
- **类型**: API | UI | 集成
- **前置条件**:
  - 用户已登录 / 游客 session
  - 商品 SKU-xxx 库存 ≥ N，状态上架
  - （可选）优惠券 COUPON-xxx 已领取且未使用
- **测试数据**:
  | 字段 | 值 |
  |------|-----|
  | skuId | |
  | quantity | |
  | expectedAmount | |
- **步骤**:
  1. ...
  2. ...
- **预期结果**:
  - HTTP 200，业务 code = 0
  - 购物车 lineItems 数量 = ...
  - 订单 status = PENDING_PAYMENT
  - ...
- **清理**: 删除测试订单 / 恢复库存
- **自动化备注**: fixture 名称、mock 点、不稳定因素
```

## 测试计划总表模板

```markdown
# [项目名] 购物车与支付测试计划

## 环境
- Base URL:
- 支付: 沙箱 / Mock
- 测试账号:

## 范围
- In: 加购、结算、支付回调、订单状态
- Out: 物流、售后（除非用户指定）

## 用例列表
| ID | 优先级 | 模块 | 标题 | 自动化 |
|----|--------|------|------|--------|
| | | | | Y/N |

## 风险
- 支付回调延迟
- 库存超卖并发
```

## API 断言检查表

复制到实现时逐项核对：

```
响应
- [ ] status code
- [ ] 业务 errorCode / message
- [ ] 响应体关键字段类型与值

购物车
- [ ] items[].skuId, quantity, unitPrice, lineTotal
- [ ] cartTotal 与各 lineTotal 之和一致

订单
- [ ] orderNo 唯一
- [ ] totalAmount 与结算页一致
- [ ] status 符合状态机

支付
- [ ] paymentId 与 orderNo 关联
- [ ] 重复 notify 不改变终态
```

## UI 元素定位建议

优先顺序：`data-testid` > role + name > 稳定 CSS > XPath

常见 testid 命名：

| 区域 | 建议 testid |
|------|-------------|
| 加购按钮 | `add-to-cart-btn` |
| 购物车图标角标 | `cart-badge-count` |
| 数量输入 | `cart-item-qty-{skuId}` |
| 去结算 | `checkout-btn` |
| 提交订单 | `submit-order-btn` |
| 支付确认 | `pay-confirm-btn` |

## 订单状态机（参考）

测试断言前先确认项目实际枚举：

```
CREATED → PENDING_PAYMENT → PAID → (SHIPPED → COMPLETED)
                ↓
            CANCELLED / CLOSED (timeout)
```

支付失败通常保持 `PENDING_PAYMENT`；关单后不可再次支付（除非业务允许重新下单）。
