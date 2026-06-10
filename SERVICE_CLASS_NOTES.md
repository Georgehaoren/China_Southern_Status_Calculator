# Service Class Notes / 服务等级与产品命名歧义说明

本说明用于解释项目中“服务等级 / Service Class”字段的边界。它不是航空公司官方解释，也不替代任何航空公司的官网、App、小程序、客服、票规或账户最终入账。

## 1. 核心原则

本工具中的 `service_class`、`service_class_cn`、`service_class_en`、`service_class_display` 仅用于本地规则库归类和显示。

实际测算和入账应优先看：

1. 订座舱位代码 / RBD；
2. 市场方承运人；
3. 实际承运人；
4. 票号前缀；
5. 南航明珠或相关常旅客计划当前公布的累积表；
6. 实际账户入账结果。

不要仅凭“First”“Business”“Premium Economy”“明珠经济舱”等产品名称判断定级里程、奖励里程或定级航段。

## 2. American Airlines 示例

美国航空的 “First” 与 “Flagship First” 容易产生歧义：

- “First” 可用于美国国内航班的 First 产品语境；
- “Flagship First” 可用于特定国际或跨大陆产品语境；
- 即使产品名称都含 “First”，最终累积到南航明珠时仍应以南航合作伙伴累积表中的 AA 订座舱位代码和实际入账为准；
- 本工具中 AA `F/A` 显示为“头等舱 / First Class”，仅代表规则库中的服务等级归类，不代表具体是 Domestic First、Flagship First International、Flagship First Transcontinental，或任何特定座椅/休息室产品。

## 3. China Southern 示例

南航产品命名也可能出现中文/英文差异：

- 南航英文页面可使用 “Premium Economy Class”；
- 南航中文页面可使用“明珠经济舱”；
- 南航会员手册的累积表中也出现“明珠经济舱”作为服务等级；
- 本工具为了跨航司显示一致，使用“超级经济舱 / Premium Economy”作为通用标签；涉及南航自身产品时，可在备注中说明“南航产品名称可能显示为明珠经济舱”。

## 4. 建议写法

如需在 README 或 UI 中说明，建议使用：

> 服务等级仅为规则库显示标签。航司产品名称、座椅名称、舱等营销名与常旅客累积分类不一定一一对应。请以实际订座舱位代码、市场方/实际承运人、票号、官方累积表及账户最终入账为准。

## 5. 维护建议

如某航司存在明显产品命名歧义，可在数据文件中增加：

- `product_name_note_cn`
- `product_name_note_en`
- `accrual_basis_note_cn`
- `display_warning_cn`

但不建议在计算逻辑中根据产品营销名自动推断累积比例。
