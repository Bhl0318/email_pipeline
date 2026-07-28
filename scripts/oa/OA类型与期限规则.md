# OA 立项：类型覆盖与期限计算规则

> 本文档汇总 OA 立项邮件的类型识别与期限计算规则。
> 代码为准,规则实现见 `filter_oa_email.py`(分类/期限)、`us_deadline.py` + `parse_us_pdf.py`(US 官文期限)。
> 术语区分:**答复期限 `project_deadline`**(法定回复截止)vs **计划送审日 `dueDate`**(内部计划,`calc_dueDate`)。

---

## 一、OA 类型覆盖

### CN（发件人含 `@metis-ip.com`,按主题关键词匹配）
| 通知类型（主题关键词） | 立项名称 | 备注 |
|---|---|---|
| 审查意见通知书 | 第N次审查意见答复 | N 从主题"第X次"提取,取不到为"审查意见答复" |
| 复审请求补正通知书 | 复审补正答复 | 顺序排在"补正通知书"前,避免误判 |
| 补正通知书 | 补正答复 | |
| 驳回决定 | 驳回复审评估 | |
| 办理登记手续通知书 | 分案评估 | **仅 20618、20735 客户立项**（`CN_DENGJI_CUSTOMERS`） |
| 复审通知书 | 复审意见答复 | |

### EP（发件人含 `@panovision-ip.com`,按主题关键词匹配）
| 通信类型 | 立项名称 | 要 OA 序号 |
|---|---|---|
| European search report | EESR答复 | 是 |
| Communication A.94(3) | Communication Pursuant to Article 94(3) EPC答复 | 是 |
| Summons to oral proceedings | 口头审理通知书（Rule 115(1)）答复 | 是 |
| Intention to grant | Communication under Rule 71(3) EPC（授权意向通告）答复 | 否 |
| Further search fee | Partial Supplementary European Search Report | 否 |
| Communication R.62a(1) | Communication pursuant to Rule 62a(1) EPC答复 | 否 |
| Communication R.70(2) | **不单独立项**,期限合并到同案号 EESR | — |

### US（发件人含 `noreply@uspto.gov` 或主题含 USPTO;按正文表格 Document Type）
**需立项的 11 种 Document Type（`US_TYPES_NEED_PROJECT`）**
| 代码 | 立项名称 | 要 OA 序号 |
|---|---|---|
| CTNF | Non-Final Rejection答复 | 是 |
| CTFR | Final Rejection答复 | 是 |
| CTAV | Advisory Action答复 | 是 |
| NOA | 分案/续案评估 | 否（**仅 20608/20618/20849/20633/20609 客户立项**,`NOA_PROJECT_CUSTOMERS`） |
| CTRS | Requirement for Restriction Election答复 | 否 |
| EXIN | Examiner Interview Summary Record答复 | 否 |
| CTEQ | Ex Parte Quayle Action答复 | 否 |
| PPH.DECISION | PPH Decision dismissed补正答复 | 否 |
| NT.CR.APP.PA | Notice to file corrected application papers补正答复 | 否 |
| NTC.MISS.PRT | NOTICE TO FILE MISSING PARTS…补正答复 | 否 |
| PETDEC | Petition Decision Dismissed补正答复 | 否 |

**跳过不立项（`US_TYPES_SKIP`）**:`ISSUE.NTF、892、1449、COCX、ABN、APP.FILE.REC、NTC.PUB、NTC.PUB.DATE、OA.APPENDIX、WELCOME.LET、M327、PREDOCK.NTF`

**其它 US 规则**
- **eGrant Notification**(主题命中）整封跳过（其表格为 5 列会错位,且本就不需立项）。
- 未知 Document Type → 仍立项但标 `[未知类型]` + `needs_confirmation`(待人工确认)。

### 全局排除（任何区域,先于 US/EP/CN 判断）
- 主题含 `reminder`（不分大小写）→ 不立项。
- 主题含 `向外国申请专利保密审查意见通知书` → 不立项（注意它含"审查意见通知书"子串,必须先拦）。

---

## 二、答复期限（`project_deadline`）来源
| 区 | 来源 |
|---|---|
| **CN** | 正文 `答复期限：X`;标准日期直接用,非标准表述(如"两个月""五个工作日")→ **DeepSeek** 按发文日换算成绝限日 |
| **EP** | 正文 `within X months` → 发文日 + X 月;`R.70(2)`/`Summons`/`Intention to grant` 及正则取不到 → **DeepSeek** 从正文提取 |
| **US** | **不取自邮件**:`us_deadline` 用 USPTO API **下载官文 PDF** → `parse_us_pdf` 提取答复月数(正则 `expire X MONTHS` → DeepSeek 文本 → qwen-vl 图片,三级降级)→ **deadline = 发文日(mailing date) + X 月** |

---

## 三、计划送审日（`dueDate`,`calc_dueDate`）
前提:必须有发文日,否则返回空。

| 区 | 规则 |
|---|---|
| **CN / CM / CS** | 有期限且(期限−发文日)≥4 个月 → 发文日 + 2 月;否则 发文日 + 1 月;无期限 → 默认 发文日 + 2 月 |
| **US** | `CTAV`(Advisory)→ 查同案号 Final Rejection 绝限日 + 1 月作为期限,送审 = **收到日 + 15 天**;`CTFR`(Final)→ **收到日 + 15 天**;其它(Non-Final 等)→ **发文日 + 45 天** |
| **EP** | 有期限且 ≥6 个月 → 发文日 + 60 天;否则 发文日 + 40 天;无期限 → 默认 发文日 + 60 天 |
| 其它国家 | 发文日 + 1 月 |

**通用后处理（所有区）**
1. 约束:计划送审日 ≤ 答复期限 − 15 天;若超出,取 `(收到日或发文日) → 答复期限` 的**中点**。
2. 落在周末 → 前移到最近工作日。

---

## 附:字段来源速查
| 字段 | 来源 |
|---|---|
| 发文日 `oa_doc_date`/`issue_date` | CN=主题日期前缀;EP=正文 `issued/on`;US=正文表格 Mailroom Date |
| 案号 `project` | CN/EP=主题正则;US=正文表格 Attorney Docket No. |
| OA 序号 `oaNum` | 标 `needs_oaNum` 的查 `projects` 表取最大+1,立项名前缀 `OA{N}-` |
| 客户简称 `customer` | 按案号前 5 位查 atw `customer` 表 |
