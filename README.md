# 南航明珠等级测算 WebUI（非官方）

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)
![Status](https://img.shields.io/badge/status-local%20webui-green)
![License](https://img.shields.io/badge/license-MIT-blue)

> **China Southern Sky Pearl Status Calculator WebUI / 南航明珠会员等级测算 WebUI**  
> 本项目是一个**非官方、本地运行、维护者自行维护**的规划与数据分析工具，用于辅助测算南航明珠会员等级、定级里程、定级航段、奖励里程和成本效率。  
> 项目不隶属于、不代表、也未获得中国南方航空、南航明珠俱乐部或任何航空公司、机场、联盟、票务平台授权、认证、赞助或背书。

---

## 目录

- [请先阅读：重要声明](#请先阅读重要声明)
- [功能概览](#功能概览)
- [推荐运行方式](#推荐运行方式)
- [启动器说明](#启动器说明)
- [手动运行方式](#手动运行方式)
- [日志与故障排查](#日志与故障排查)
- [计算口径提示](#计算口径提示)
- [数据来源标注](#数据来源标注)
- [数据与规则库](#数据与规则库)
- [API 与模块结构](#api-与模块结构)
- [维护建议](#维护建议)
- [发布包建议](#发布包建议)
- [版本更新记录](#版本更新记录)
- [许可证](#许可证)

---

## 请先阅读：重要声明

- **非官方**：本项目不是南航、南航明珠、任何航空公司、任何常旅客计划、任何联盟或任何 OTA 的官方工具。
- **非保证**：所有计算结果、规则匹配、状态提示、成本效率和导出文件均为估算与数据整理结果，不保证准确、完整、实时、可入账、可出票、可复现或适用于你的账户。
- **以官方为准**：航司官网、官方 App/小程序、客服回复、出票页面、客票规则、运输总条件、常旅客账户最终入账结果始终优先于本项目。
- **非专业建议**：本项目不构成法律、财务、税务、签证、保险、安全、票务、常旅客规则解释、购票或旅行建议。使用者应自行核验并自行承担决策后果。
- **不鼓励违规玩法**：本项目不鼓励、不指导、不保证任何违反承运人运输总条件、票价规则、入境规则、法律法规或平台规则的行为，包括但不限于弃程、隐藏城市、规避票规、滥用权益、利用系统漏洞、虚假行程或不符合真实出行目的的操作。
- **数据为工作副本**：`data/` 中的 JSON/CSV 是维护者维护的本地测算工作库，不是官方数据库。合作关系、代码共享、累积资格、航司权益、舱位规则、票号规则、促销规则和保级政策均可能变化。
- **AI 生成声明**：本项目的部分代码、文案、结构、注释和测试说明由 AI 辅助生成，并经人工整理。AI 生成内容可能存在错误、遗漏或过时信息；本项目不代表任何 AI 服务提供商、模型提供方或航空公司观点。
- **商标归属**：项目中出现的航空公司名称、二字码、常旅客计划名称、联盟名称、商标、服务名称和页面链接仅用于描述兼容对象、字段含义或来源索引，相关权利归各自权利人所有。

更完整的说明见：

```text
DISCLAIMER.md
NOTICE.md
DATA_SOURCES.md
AI_USAGE.md
SERVICE_CLASS_NOTES.md
```

---

## 功能概览

本项目主要用于辅助规划南航明珠会员等级、保级、冲级和航段/里程成本效率，当前功能包括：

- 南航明珠银卡、金卡、铂金卡冲级 / 保级测算。
- 连续第几年保级折扣测算。
- 定级里程、定级航段、奖励里程和成本效率计算。
- 784 票号现金消费金额测算。
- 784 票号、CZ/OQ 市场方、非 CZ/OQ 实际承运场景的代码共享 / 非南航承运测算。
- 南航 / 重航标准里程模式。
- 航空合作伙伴参考规则库。
- 合作状态 / 变动提示库，用于区分当前参考、历史规则、暂停/终止/需核对等状态。
- 航司代码查询与自动补全。
- 里程工具代码查询与自动补全。
- 标准里程来源记录，包括官方/公开工具手动查询、实际入账、南航明珠查询、对应航司工具、机场距离估算等。
- CSV / JSON 导入。
- CSV / JSON 导出，便于后续数据分析。
- 本地 WebUI 运行，不需要上传个人行程数据到第三方服务器。
- 命令行启动器与图形化启动器，降低非技术用户使用门槛。

---

## 推荐运行方式

### 方式一：Windows 用户

如果你只是想使用 WebUI，推荐直接双击：

```text
start.bat
```

启动器会自动完成：

```text
检查 Python
创建 / 复用 .venv 虚拟环境
安装 requirements.txt
启动本地 Flask WebUI
自动打开浏览器
```

默认访问地址：

```text
http://127.0.0.1:5055/
```

如果希望使用命令行模式，可以运行：

```text
start_cli.bat
```

### 方式二：macOS 用户

推荐双击：

```text
start.command
```

如果系统提示没有执行权限，可以在终端进入项目目录后执行：

```bash
chmod +x start.command
./start.command
```

也可以使用命令行启动：

```bash
chmod +x start.sh
./start.sh
```

### 方式三：Linux 用户

```bash
chmod +x start.sh
./start.sh
```

### 方式四：开发者 / 技术用户

```bash
python tools/cli_launcher.py
```

可选参数示例：

```bash
python tools/cli_launcher.py --port 5055
python tools/cli_launcher.py --no-browser
python tools/cli_launcher.py --reinstall
python tools/cli_launcher.py --reset-venv
python tools/cli_launcher.py --debug
```

---

## 启动器说明

本项目现在采用“双启动器”设计：

```text
CLI Launcher = 稳定启动核心，便于排错和开发
GUI Launcher = 图形化外壳，面向普通用户
```

推荐结构：

```text
tools/
├── launcher_core.py      # CLI 和 GUI 共用的启动核心
├── cli_launcher.py       # 命令行启动器
└── gui_launcher.py       # GUI 启动器
```

### 启动器负责的事情

```text
1. 检查项目根目录
2. 检查 app.py / requirements.txt
3. 检查 Python 版本
4. 创建或复用 .venv
5. 安装 / 更新依赖
6. 检查默认端口 5055
7. 端口被占用时自动尝试 5056、5057 等后备端口
8. 使用 CZ_APP_PORT 环境变量启动 Flask
9. 检查 /api/health
10. 自动打开浏览器
11. 写入 logs/launcher.log 和 logs/flask_server.log
12. 退出时停止 Flask 子进程
```

### GUI 启动器

GUI 启动器用于面向不熟悉命令行的用户，提供：

```text
启动 WebUI
停止 WebUI
打开浏览器
查看运行状态
显示日志
重新安装依赖
打开项目目录
```

如果安装了 `CustomTkinter`，界面会使用更现代的控件样式；如果没有安装，仍可回退到 Python 自带的 Tkinter 风格。

可选安装 GUI 美化依赖：

```bash
python -m pip install -r requirements-gui.txt
```

### Windows UNC 路径兼容

如果项目放在 Parallels / VMware / VirtualBox 共享目录、NAS、公司共享盘或类似路径中，路径可能是：

```text
\\Mac\Home\Desktop\...
\\server\share\...
```

旧版 Windows 批处理脚本可能因为 `cmd.exe` 不支持把 UNC 路径作为当前目录而启动失败。新版 `start.bat` / `start_cli.bat` 应使用 `pushd "%~dp0"` 临时映射共享目录，避免相对路径被错误解析到 `C:\Windows\tools\...`。

如果仍然遇到 `.venv`、`pip install` 或权限问题，建议将项目复制到 Windows 本地目录后再运行，例如：

```text
C:\Users\<你的用户名>\Desktop\China_Southern_Status_Calculator
```

---

## 手动运行方式

如果不使用启动器，也可以手动运行。

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Windows CMD

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

默认地址：

```text
http://127.0.0.1:5055/
```

如需修改端口，可设置环境变量：

### macOS / Linux

```bash
CZ_APP_PORT=5056 python app.py
```

### Windows PowerShell

```powershell
$env:CZ_APP_PORT="5056"
python app.py
```

### Windows CMD

```bat
set CZ_APP_PORT=5056
python app.py
```

---

## 日志与故障排查

启动器和 Flask 服务会写入本地日志：

```text
logs/
├── launcher.log
├── flask_server.log
└── batch_bootstrap.log
```

说明：

- `launcher.log`：Python 启动器日志。
- `flask_server.log`：Flask 后端运行日志。
- `batch_bootstrap.log`：Windows `.bat` 启动阶段日志，用于记录 Python 启动器尚未开始前的错误。

### 常见问题

#### 1. 浏览器没有自动打开

手动访问：

```text
http://127.0.0.1:5055/
```

如果端口被占用，启动器可能会自动切换到：

```text
http://127.0.0.1:5056/
http://127.0.0.1:5057/
```

请查看终端或 `logs/launcher.log` 中实际地址。

#### 2. Windows 从 Parallels 共享目录启动失败

请确认 `start.bat` 中使用了：

```bat
pushd "%~dp0"
```

如果仍然失败，请将项目复制到 Windows 本地目录后运行。

#### 3. 依赖安装失败

尝试重新安装依赖：

```bash
python tools/cli_launcher.py --reinstall
```

或重建虚拟环境：

```bash
python tools/cli_launcher.py --reset-venv
```

#### 4. 端口被占用

指定其他端口：

```bash
python tools/cli_launcher.py --port 5056
```

---

## 计算口径提示

本项目用于规划测算，默认规则包括：

- 级别门槛：银卡 2 万定级里程或 20 定级航段；金卡 4 万或 40 段；铂金卡 10 万或 80 段。
- 保级折扣仅用于保至当前或以下精英级别，不用于向上冲级。
- 784 票号、CZ/OQ 市场方且 CZ/OQ 实际承运时，可按现金消费金额模式测算。
- 784 票号、CZ/OQ 市场方但非 CZ/OQ 实际承运时，可使用“784 代码共享 / 非南航承运”模式：定级里程按非南航承运参考规则，定级航段按南航票面舱位代码参考测算。
- 合作伙伴标准里程模式会读取合作状态库；未标记为当前可累积的航司默认不纳入汇总。
- 多航段联程票可通过“成本分摊组”和“成本口径”进行整单成本拆分，但该拆分仅用于本地测算。
- 产品营销名称、客舱体验名称、座椅名称或媒体/论坛称呼不得单独作为定级里程、奖励里程、定级航段或服务等级判断依据。

以上口径只是程序默认值，不替代航空公司规则、官方客服解释、出票页面或实际入账。

---

## 标准里程填写建议

本工具不强制联网抓取标准里程。建议按以下优先级手动填写：

1. 已有实际入账样本。
2. 南航明珠官方查询或航空公司官方/公开工具手动查询结果。
3. 对应航司官方工具的参考结果。
4. 机场三字码距离估算，仅作为 fallback，并在来源字段中标记为估算。

其他航司自有里程工具通常反映该航司自身常旅客计划口径，不一定等同于累积到南航明珠的实际入账。

---

## 数据来源标注

本项目包含统一来源登记表：

```text
data/data_sources_2026.json
data/data_sources_2026.csv
DATA_SOURCES.md
```

核心来源拆分为：

- 南航会员手册官方页面，用于会员级别、定级里程/航段、奖励里程、现金消费金额、品类系数、会员级别系数等基础规则。
- 南航明珠乘机累积 / 合作伙伴航班页面，用于人工核对合作伙伴累积表。
- 南航明珠合作航司精英权益页面，用于人工核对合作航司权益 / 合作展示，并作为状态变动提示来源之一。
- 公开页面人工整理的合作伙伴累积表、合作航司权益信息；仓库中仅保留人工整理后的短字段和数值，不保存原始图片材料。
- 匿名化实际入账样本，仅用于 784 代码共享 / 非南航承运样本规则，不推广到其他承运方、舱位或航线。
- 人工整理的航空公司里程工具链接，仅用于引导使用者自行查询标准里程，不代表本项目自动抓取或验证结果。

每个 JSON 规则库都应包含 `source_registry` 与 `source_refs` 字段；每个 CSV 工作库也应保留 `source_registry`、`source_refs`、`source_url_reference` 等字段。公开发布时请保留这些字段。

---

## 数据与规则库

项目采用可替换 JSON / CSV 规则库，便于后续维护：

```text
data/
├── cz_rules_2025_2027.json
├── cz_partner_accrual_rules_2026.json
├── cz_partner_accrual_rules_2026.csv
├── cz_codeshare_784_accrual_rules_2026.json
├── cz_codeshare_784_accrual_rules_2026.csv
├── cz_partner_status_2026.json
├── cz_partner_status_2026.csv
├── cz_carrier_directory_2026.json
├── cz_carrier_directory_2026.csv
├── mileage_tool_links_2026.json
├── mileage_tool_links_2026.csv
├── data_sources_2026.json
├── data_sources_2026.csv
├── service_class_notes_2026.json
└── service_class_notes_2026.csv
```

### 服务等级双语显示

合作伙伴规则库与 784 代码共享规则库中的 `service_class` 字段保留稳定英文枚举：

```text
first
business
premium_economy
economy
unknown
```

前端与导出结果会同时显示中文与英文，例如：

```text
头等舱 / First Class
公务舱 / Business Class
超级经济舱 / Premium Economy
经济舱 / Economy Class
```

### 服务等级与产品命名歧义说明

本工具中的“服务等级 / Service Class”仅用于规则库归类和前端显示，不能替代航空公司的实际产品名称、机型配置、订座舱位代码或常旅客实际入账。

例如，美国航空的 “First / First Class” 可能指美国国内 First，也可能在特定国际或跨大陆航线语境中与 Flagship First 产品相关；这些产品体验、休息室权益、机型和航线范围均可能不同。

因此，本项目计算时应优先依据：

1. 实际出票与行程单中的市场方承运人、实际承运人、票号、航班号和订座舱位代码。
2. 南航明珠或相关常旅客计划当前公布的合作伙伴累积表。
3. 航空公司官方 App/官网/客服或账户最终入账。
4. 使用者自行维护的实际入账样本。

详见：

```text
SERVICE_CLASS_NOTES.md
```

---

## API 与模块结构

本项目自 v26 起将 Flask 入口、API 路由、页面路由、配置、业务计算和导出逻辑拆分，便于后续维护。

```text
app.py                  # Flask app factory / 应用入口
config.py               # 统一配置：路径、端口、版本号、数据文件索引

api/
├── __init__.py
├── health.py           # /api/health
├── reference_data.py   # 规则库、来源库、工具库等只读 API
├── calculate.py        # /api/calculate
└── exports.py          # /api/export/json, /api/export/csv

web/
└── routes.py           # 首页路由

services/
├── rules.py            # JSON/CSV 规则读取与降级逻辑
├── calculator.py       # 核心测算逻辑
└── exporter.py         # CSV/JSON 导出逻辑

tools/
├── launcher_core.py    # CLI / GUI 共用启动器核心
├── cli_launcher.py     # 命令行启动器
└── gui_launcher.py     # 图形化启动器

logs/                   # 本地运行日志，不建议提交 .log 文件
```

### 主要 API

```text
GET  /api/health
GET  /api/reference/...
POST /api/calculate
POST /api/export/json
POST /api/export/csv
```

实际接口以 `api/` 目录中的蓝图实现为准。

---

## 维护建议

1. 不要把规则库视为官方数据库。它们只是本地测算用的工作副本。
2. 若航空公司公告或官网页面更新，应更新 JSON / CSV 后再测算。
3. 若某合作关系已暂停、终止、到期或仅保留权益/代码共享，应在 `cz_partner_status_2026.json` 中明确状态。
4. 如无法确认当前常旅客累积资格，建议将 `current_accrual_eligible` 设为 `false`，并写明核验备注。
5. 对外发布时，请保留来源链接、查询日期和版本号，避免复制大段第三方页面原文或页面信息。
6. 不要上传个人账户图片材料、票号、身份证件、订单号、会员号、支付记录、旅行证件或其他隐私信息。
7. 不建议把便携 Python、虚拟环境、pip 缓存或打包产物直接提交到主仓库。
8. 建议将小白版压缩包、Windows `.exe`、macOS `.app` 放在 GitHub Releases 或网盘中单独发布。

---

## 发布包建议

推荐分层发布：

```text
GitHub main branch:
- 源码
- 启动器脚本
- 规则库工作副本
- README / docs

GitHub Releases:
- Windows ZIP 小白包
- macOS ZIP 小白包
- 可选 GUI launcher 打包产物
```

### 不建议直接提交到仓库的内容

```text
.venv/
__pycache__/
logs/*.log
dist/
build/
*.spec
portable_python/
```

如果后续使用 PyInstaller 打包，建议优先使用 one-folder 模式，而不是一开始就追求单文件 exe。原因是本项目包含 `templates/`、`static/`、`data/` 等资源目录，one-folder 模式更容易排查文件路径问题。

---

## 版本更新记录

### v28：GUI 启动器与小白运行体验

- 新增图形化 WebUI 启动器。
- 支持启动、停止、打开浏览器、查看状态和日志。
- 可选使用 CustomTkinter 美化界面。
- GUI 启动器与 CLI 启动器共用启动核心，避免重复维护。

### v27：命令行启动器与跨平台入口

- 新增 `tools/launcher_core.py`。
- 新增 `tools/cli_launcher.py`。
- 新增 Windows / macOS / Linux 入口脚本。
- 自动创建 `.venv`、安装依赖、启动 Flask、检查 `/api/health`、打开浏览器。
- 支持端口自动 fallback。
- 支持 `--reinstall`、`--reset-venv`、`--no-browser`、`--debug` 等参数。
- 修复 Windows 从 UNC 共享路径启动时相对路径解析错误的问题。

### v26：模块化结构

- 将 Flask 入口、API 路由、页面路由、配置、业务计算和导出逻辑拆分。
- 新增 `api/`、`services/`、`web/` 等目录。
- 提高后续维护、扩展其他航司或增加规则库的可维护性。

### v25：前端表单显示优化

- “市场方”“承运方”输入框保留手动输入，同时使用航司代码库 datalist 辅助补全。
- “工具代码”改用里程工具库 datalist，而不是航司代码库。
- lookup 字段在聚焦时临时展开宽度，便于查看候选项；失焦后恢复紧凑表格布局。

### v22：成本分摊与导入

- 航段 / 产品明细表新增“成本分摊组”和“成本口径”。
- 多航段联程票可将同一订单的多行填入同一个成本分摊组。
- 支持按段数均分或按标准里程分摊。
- 新增 CSV / JSON 导入按钮。

### v21：目标与场景默认值调整

- “会员与目标设置”中的当前级别、奖励里程级别、目标级别默认均为“请选择”。
- “连续第几年保级”调整为“评定场景 / 连续保级年限”。
- 新增“升级 / 新定级（不使用保级折扣）”选项。
- 未选择目标级别时，仅汇总明细，不判断升级 / 保级达标。

---

## 贡献与问题反馈

本项目主要是个人维护的本地测算工具。若发现：

```text
规则库过期
某航司合作状态变化
某舱位代码测算异常
前端字段显示异常
启动器在特定系统下无法运行
```

建议通过 GitHub Issue 记录：

```text
系统版本
Python 版本
运行方式
错误截图或 logs/launcher.log
涉及的航司、票号、市场方、承运方、舱位代码
```

请不要在 Issue 中公开个人会员号、票号、订单号、证件号、支付记录、完整行程单截图或其他敏感信息。

---

## 许可证

本包默认附带 MIT License 作为代码开源模板。数据文件、航空公司名称、商标及第三方页面内容不因本项目许可证而改变其原有权利归属。

如果你不准备以 MIT 开源，请在发布前替换或删除 `LICENSE` 文件。

---

## 再次提醒

本项目只是一个**非官方、本地运行、辅助规划与数据分析工具**。  
任何与购票、保级、冲级、里程入账、权益使用、航班变更、签证入境、保险、安全或实际旅行相关的决定，都应以官方渠道和实际账户结果为准。
