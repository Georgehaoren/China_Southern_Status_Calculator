# Data, Attribution, and AI Notice / 数据、引用与 AI 声明

The files in `data/` are maintainer-managed reference datasets for local calculation and testing. They are not official airline databases, official fare-rule publications, official loyalty-program statements, or official ticketing outputs.

`data/` 目录中的文件为维护者维护的本地测算参考数据，不是航空公司官方数据库、官方票规出版物、官方常旅客规则解释或官方出票结果。

## Data-source policy / 数据来源原则

- Record source URLs, query dates, valid-from dates, valid-to dates, and notes whenever possible.
- Prefer short factual fields, labels, and source references over copying long policy text.
- Do not commit references, account pages, ticket images, personal information, member numbers, ticket numbers, order numbers, passport/ID data, payment records, or long copied excerpts from airline websites.
- If a rule is uncertain, expired, suspended, terminated, partner-specific, route-specific, or based on user observation, mark it clearly and avoid automatic accrual by default.
- If a rights holder requests removal or correction of a data entry, review and update or remove the entry.

## Included data scope / 随包数据范围

The included data is intended to demonstrate the project structure and support personal planning. It may contain working-copy rules derived from public information, user references, and anonymized observations. Users should independently verify the data before relying on it.

随包数据用于展示项目结构并辅助个人规划，可能包含基于公开信息、公开页面人工整理和匿名化实际观察整理的工作副本规则。使用前应自行核对。

## Explicit source registry / 明确来源登记

This repository includes `DATA_SOURCES.md` and `data/data_sources_2026.json/csv` to document where each working dataset came from. Relevant public reference pages are:

- China Southern Sky Pearl flight earning / partner airline page: `https://www.csair.com/mcms/mcmsNewSite/mows/cn/#/skypearl/earning/fly_/fly_operation`
- China Southern Sky Pearl partner airline elite-benefit page: `https://www.csair.com/mcms/mcmsNewSite/mows/cn/#/skypearl/member/hyqy/hzhs`

Original image materials, account records, and full handbook/PDF copies are not bundled for redistribution. Only short, maintainer-managed reference fields are included.

## AI-assisted code and content / AI 辅助代码与内容

Some code, documentation, comments, wording, and test descriptions in this repository were generated or revised with AI assistance. The human maintainer is responsible for reviewing, testing, and deciding whether to publish or use the generated content. AI-assisted generation may introduce inaccuracies, non-idiomatic code, security issues, license concerns, or outdated assumptions.

本仓库中的部分代码、文档、注释、措辞和测试说明由 AI 辅助生成或修改。人工维护者应负责审阅、测试，并自行决定是否发布或使用相关内容。AI 辅助生成可能引入错误、非最佳实践、安全问题、许可证问题或过时假设。

## Publication reminder / 公开发布提醒

Before publishing this repository, review all files for private information, third-party copyrighted materials, references, long policy excerpts, and data that may be outdated or misleading. When in doubt, replace complete working datasets with sample data and keep private notes outside the public repository.

公开发布前，请检查仓库中是否包含隐私信息、第三方版权材料、页面信息、大段规则原文，以及可能过时或误导的数据。若不确定，建议用示例数据替换完整工作库，并将私人备注保存在公开仓库之外。


## Service-class naming notice / 服务等级命名提示

Service-class labels in this repository are descriptive compatibility labels. Airline products with similar names may differ substantially by route, aircraft, region, ticketing channel, and date. Users should verify the actual booking class and loyalty-program posting rules before using any result for status planning.

本仓库中的服务等级标签仅为描述兼容用途。名称相近的航司产品可能因航线、机型、地区、出票渠道和日期不同而差异很大。使用者应在用于保级/冲级规划前自行核验实际订座舱位及常旅客计划入账规则。
