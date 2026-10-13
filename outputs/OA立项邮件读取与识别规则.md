# OA 立项邮件读取与识别规则（CN / US / EP）

本文记录截至 2026-10-13 的**实际统一流水线**规则。入口是 `scripts/main.py`：按 `scripts/pipeline_config.json` 读取邮件，用 `scripts/report/read_email.py` 和 `scripts/report/classify_report.py` 分类，再把同一批结果交给 `scripts/oa/read_email.py:dispatch_oa` 立项。`scripts/oa/read_email.py`、`scripts/oa/filter_oa_email.py` 也能单独运行，但有下文注明的差异。代码为最终依据。

## 1. 读取哪些邮件

统一流水线当前配置读取以下账号和 IMAP 文件夹：

| 邮箱账号配置名 | 文件夹 | 归档处理 |
| --- | --- | --- |
| `docketing` | `INBOX` | 按统一流水线的分类结果归档 |
| `docketing` | `Metis+Porus+Poseidon/Done` | `no_archive=true`，只读，不移动 |
| `attorneys` | `INBOX` | 按统一流水线的分类结果归档 |

每个“账号 + 文件夹”分别维护 checkpoint。已有断点时，从上次邮件时间往前回溯 1 小时；没有断点时，只读最近 1 天。IMAP 按日期搜索，单次每个文件夹最多取最新 50 封，然后通过已记录的 `Message-ID` 去重。读取后更新 checkpoint，再分类。这里的“最多 50 封”是当前 `read_emails` 默认参数，不代表文件夹中只会有 50 封邮件。

读取后先从邮件解析主题、发件人、纯文本正文、HTML 正文、日期、`Message-ID` 和附件。分类主要使用**发件人、主题、正文表格**；初次识别不靠审查意见 PDF 判断官文类型。

## 2. 三类邮件共同的排除和分流

分类前，以下邮件直接跳过：

1. 主题以 `RE:`、`Re：`、`回复:`、`回复：` 等回复前缀开头（忽略 `RE` 大小写）。
2. 主题包含 `reminder`（忽略大小写）。
3. 主题包含 `向外国申请专利保密审查意见通知书`。

之后按 **US → EP → CN** 的顺序分流。一封邮件只走首先匹配的法域分支。当前匹配规则使用字符串包含判断；除专门标注的规则外，并没有做大小写归一。

| 法域 | 进入该分支的条件 | 进一步判断的位置 |
| --- | --- | --- |
| US | 发件人含 `noreply@uspto.gov`，**或**主题含 `USPTO` | 正文表格的 `Document Type` |
| EP | 发件人含 `@panovision-ip.com` | 主题中的英文通信类型关键词 |
| CN | 统一流水线要求发件人含 `xing.wu@metis-ip.com` | 主题中的中文通知名称 |

**运行入口差异：**单独运行 `scripts/oa/read_email.py` 时，CN 发件人条件较宽，为包含 `@metis-ip.com`；其默认邮箱文件夹是 `docketing/TEST` 与 `attorneys/TEST`。统一流水线以 `scripts/pipeline_config.json` 和 `scripts/report/classify_report.py` 为准。

## 3. CN：按邮件主题中的通知名称识别

进入 CN 分支后，代码按下表**从上到下**检查主题是否包含通知名称；命中第一个即停止。主题无需完全等于通知名称。

| 主题必须包含的文字 | 生成的立项名称 | 其他条件 |
| --- | --- | --- |
| `审查意见通知书` | 主题含“第X次审查意见”时生成“第X次审查意见答复”；取不到次数则为“审查意见答复” | X 为中文数字 |
| `复审请求补正通知书` | `复审补正答复` | 排在“补正通知书”前，避免被后者先命中 |
| `补正通知书` | `补正答复` | — |
| `驳回决定` | `驳回复审评估` | — |
| `办理登记手续通知书` | `分案评估` | **仅案号第一段为 `20618` 或 `20735`**；其他客户跳过 |
| `复审通知书` | `复审意见答复` | — |

主题优先按 `YYYY-MM-DD-通知类型-案号` 提取发文日和案号；不符合该整体格式时，再尝试从主题抓案号，并从主题开头抓日期。正文中的 `答复期限：...` 用于提取期限；非标准期限文字在有发文日时交由 DeepSeek 换算。主题、正文或 HTML 含“预审案件”会被标记；预审且属于第一/二次审查意见的结果还会附带预审备注。

## 4. US：按正文表格的 Document Type 识别

进入 US 分支后，主题含 `egrant notification`（忽略大小写）的邮件整封跳过。其他邮件优先解析 HTML 正文表格；没有解析到表格行时才按纯文本正文解析。每个有效表格行读取四列：`Application No.`、`Document Type`、`Mailroom Date`、`Attorney Docket No.`（案号）。一封邮件可以生成多条立项候选记录。

### 4.1 需要立项的 Document Type

| Document Type | 立项名称 | OA 序号 |
| --- | --- | --- |
| `CTNF` | `OA{N}-Non-Final Rejection答复` | 要 |
| `CTFR` | `OA{N}-Final Rejection答复` | 要 |
| `CTAV` | `OA{N}-Advisory Action答复` | 要 |
| `CTRS` | `Requirement for Restriction Election答复` | 不要 |
| `EXIN` | `Examiner Interview Summary Record答复` | 不要；后续仍可能因官文内容跳过 |
| `NT.CR.APP.PA` | `Notice to file corrected application papers补正答复` | 不要 |
| `NTC.MISS.PRT` | `NOTICE TO FILE MISSING PARTS OF NONPROVISIONAL APPLICATION补正答复` | 不要 |
| `CTEQ` | `Ex Parte Quayle Action答复` | 不要 |

`{N}` 从 TIP `projects` 表中同案号既有答复案的 OA 序号推算；同批同案号多条记录会逐条递增。

### 4.2 明确跳过的 Document Type

`ISSUE.NTF`、`892`、`1449`、`COCX`、`ABN`、`APP.FILE.REC`、`NTC.PUB`、`NTC.PUB.DATE`、`OA.APPENDIX`、`WELCOME.LET`、`M327`、`PREDOCK.NTF`、`EGRANT.NTF`、`TRACK1.GRANT`、`NOA`、`PPH.DECISION`、`PETDEC`、`M903`、`N570`。

其中 `892`、`1449` 自身不立项；若同一封邮件中同案号还有 OA 立项行，它们会挂到该候选记录上，供下游下载引用文献。`NOA`、`PPH.DECISION` 当前**均不自动立项**。

**未知代码的实际行为：**若表格行的 `Document Type` 既不在需立项列表、也不在跳过列表，代码会生成名称为 `[未知类型] <代码>` 的候选记录，并打印“需确认”统计。输出字段过滤会丢掉 `needs_confirmation` 标记，OA 写库阶段也没有用这个标记阻止立项；因此它并非人工确认后才写库。

US 期限不是通过初始邮件的 `Document Type` 表格直接取得。OA 下游会下载官文 PDF 并解析期限；`CTNF`、`CTFR`、`CTRS` 在解析失败时分别有 3、3、2 个月的兜底规则。

## 5. EP：按邮件主题中的英文通信类型识别

进入 EP 分支后，按下表从上到下检查主题是否包含英文关键词，关键词匹配忽略大小写。

| 主题关键词 | 立项名称 | OA 序号 | 是否单独 OA 立项 |
| --- | --- | --- | --- |
| `European search report` | `OA{N}-EESR答复` | 要 | 是 |
| `Communication R.70(2)` | 无独立立项名称 | 不要 | 否；仅识别/合并 EESR 期限，汇报信侧可使用 |
| `Communication A.94(3)` | `OA{N}-Communication Pursuant to Article 94(3) EPC答复` | 要 | 是 |
| `Intention to grant` | `Communication under Rule 71(3) EPC（授权意向通告）答复` | 不要 | 是 |
| `Decision to Grant` | `授权决定书(Decision to Grant A.97(1) EPC)` | 不要 | **否；仅供汇报信侧使用** |
| `Further search fee` | `Partial Supplementary European Search Report` | 不要 | 是 |
| `Communication R.62a(1)` | `Communication pursuant to Rule 62a(1) EPC答复` | 不要 | 是 |
| `Summons to oral proceedings` | `OA{N}-Summons to attend oral proceedings pursuant to Rule 115(1)EPC（口头审理通知书）答复` | 要 | 是 |

案号从主题的 `Your Ref.: ...` 提取，主题还需符合包含 `【通信类型】`、`(EP编号)`、`Our Ref.: ...` 的整体格式才能由主正则提取这些字段。若关键词命中但案号未提取成功，仍会形成分类结果；下游写 `projects` 时因缺案号跳过。正文的 `issued/on ...` 用于提取发文日；`within X months` 可用于计算期限。`Communication R.70(2)`、`Summons to oral proceedings`、`Intention to grant` 强制用 DeepSeek 解读期限；其他类型正则取不到期限时也会尝试 DeepSeek。

## 6. 从“识别成功”到“真正立项”

1. 分类阶段给候选记录补案号申请类型、日期、计划送审日、预立项状态等字段。需 OA 序号的类型查询现有 `projects` 记录并生成 `OA{N}-...` 名称。
2. OA 下游先剔除 EP 的 `standalone_project=False` 记录（`Communication R.70(2)` 与 `Decision to Grant`）、主题含“结案报告”的记录，以及 IPEasy 状态为终止、维持或结案的案件。
3. US `EXIN` 下载官文后，若官文含 `It is not necessary for applicant`，则不立项。
4. 写 TIP `projects` 表时，必须有案号和立项名称；同案号 + 同立项名称已存在时跳过。只有成功插入 `projects` 的记录才进入待分配案件库。数据库或其他下游操作失败，也可能导致“已识别但未成功立项”。

## 7. 对应代码

- 统一入口与扇出：`scripts/main.py`
- 正式读取范围：`scripts/pipeline_config.json`
- 正式邮件读取与 checkpoint：`scripts/report/read_email.py`
- 正式 CN/US/EP 分类：`scripts/report/classify_report.py`
- OA 下游过滤及 `projects` 写入：`scripts/oa/read_email.py`
- OA 单独运行版本：`scripts/oa/filter_oa_email.py`

注意：旧文档 `scripts/oa/OA类型与期限规则.md` 的 US 类型表包含已停用的 `NOA`、`PPH.DECISION`、`PETDEC` 自动立项规则；本文件按当前代码记录。
