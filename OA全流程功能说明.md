# OA 全流程功能说明

> 覆盖从收邮件到 OA 立项、转 OA、OA 人员分配的端到端功能。代码在 `DS/email_pipeline/scripts/`（`oa/` 立项+分配后端、`report/` 汇报信服务+分配 REST、`web/` 前端页面）。立项类型与期限的细则见同目录 `scripts/oa/OA类型与期限规则.md`。

## 一、总览

一封 docketing/attorneys 邮箱的邮件，被**读取一次、分类一次**，扇出给两个下游：**OA 立项**与**汇报信**。OA 立项完成后逐案**转给 OA 处理团队**，并把该案写进「待分配」；操作人在 **OA 分配页**为每案选定答复负责人 + QC，提交后回写 Wiki 与库。

```
邮件(docketing/attorneys)
   │ 读取+分类(一次)
   ├─→ OA 立项 sink ── 建Wiki OA信息表/传官文/写projects/写待分配 ── 转OA邮件 ── 发分配链接
   │        └─→ 立项即生成 AI 报告+方案 → oa_assign_report
   └─→ 汇报信 sink
   归档(TEST_AUTO / TEST_SKIPPED，一次)
                         ↓
            OA 分配页(report_server:8501) ── 选人提交 → 回写 Wiki 人员分配 + projects + 待分配置已分配
```

调度入口 `main.py`：每 30 分钟一轮（`--interval`），读 `pipeline_config.json` 的账号与 `sinks` 开关；`send_email=false` 只写库不发信；`--dry-run` 只读+分类+打印。

## 二、邮件读取与分类

- 账号（`pipeline_config.json`）：docketing/INBOX、docketing/Metis+Porus+Poseidon/Done、attorneys/INBOX。
- 分类器 `report/classify_report.py`（`oa/filter_oa_email.py` 的超集，二者保持同步）：按发件人/主题分流 **US（noreply@uspto.gov 或主题含 USPTO）/ EP（@panovision-ip.com）/ CN**。
- 全局排除（不立项）：主题以 `RE:/回复:` 开头、含 `reminder`、「向外国申请专利保密审查意见通知书」、主题含「结案报告」。
- 归档：命中（OA 或汇报信任一）→ `TEST_AUTO`；都不命中 → `TEST_SKIPPED`。

## 三、OA 立项（`oa/read_email.py::dispatch_oa`）

### 1. 结案跳过
按案号查 IPEasy `p_case_info` 法律状态，**终止/维持/结案**的不立项（`is_case_closed`）。

### 2. 分类与类型判定
- **CN**：审查意见通知书、办登（20618/20735 默认立项做分案评估）、补正等；预审案件识别。
- **EP**：`@panovision-ip.com` 邮件，Communication/Intention to grant 等；非独立项（R.70(2)/70a(2)）不立项。
- **US**：按 Document Type 判定——
  - 需立项 `US_TYPES_NEED_PROJECT`：CTNF/CTFR/CTAV/CTRS/EXIN/CTEQ/NT.CR.APP.PA/NTC.MISS.PRT；
  - 不立项 `US_TYPES_SKIP`：ISSUE.NTF/892/1449/NOA/PPH.DECISION/TRACK1.GRANT/M327/PREDOCK.NTF/EGRANT.NTF/PETDEC/M903 等。
  - 多次下发的无期限 NOA、EXIN「无需 action」等特殊情形按规则跳过。

### 3. 答复期限
- CN/EP：正则 + DeepSeek 从正文/PDF 抽发文日与绝限日；预审案件按发文日起算（含当天、跳周末节假日）。
- US：下载官文 PDF，正则/DeepSeek/OCR 抽月数 + 代码算截止日；解析失败按标准月数表（CTNF/CTFR=3、CTRS=2）兜底。
- 细则见 `scripts/oa/OA类型与期限规则.md`。

### 4. 官文获取
- **US**：经 USPTO ODP API（`downloadByAPI.py`）下载官文；**PDF 与 Word 都下**，落 `attachment/{案号}/`。同案号 892/1449 文献一并下载。403=未公开/受限申请，正文标注、无附件。
- **CN/EP**：官文是邮件附件，读取时存 `output/_inbox/{msgid}/`，立项时复制到 `attachment/{案号}/`（与 US 同目录，供分配页按案号读）。
- **盖章**：仅 US 的 OA 答复类 + 补正类 PDF 盖「DOCKETED」红戳（`stamp_us_pdf.py`），生成 `_stamped` 副本；Word 版不盖章。
- **审意 OCR**：扫描件无文本层时用 qwen-vl OCR（供分配页第四类）。

### 5. 写 Wiki 与库
- **OA 信息记录表页**（每案号一页）：建页 → 上传官文附件（PDF/Word/892·1449/公布公告文件）→ 解析对比文件填「OA 过程」对应 OA{N} 行的对比文件链接列（Google Patents 超链接）：**CN** 解析「本通知书引用对比文件」表（`parse_cn_pdf`）；**US** 从 **PTO‑892**（审查员正式引用清单，优先）或主官文正文抽号（`parse_us_refs`，正则+DeepSeek 兜底），号码**归一化**成 Google Patents 格式（去逗号/空格/斜杠、补 US 前缀）后复用同一 `fill_ref_docs_in_oa_row`；仅取审查员引用（892），不取申请人 IDS（1449）。**官文正文另转成该记录表页下的子页**（`oa/word_to_wiki.py`，email_pipeline 自包含，复用 `WikiClient`）：US/CN/EP 的**主官文**——US 有 Word 用 Word（python-docx）、没 Word 用主官文 PDF（PyMuPDF），CN/EP 用邮件主官文 PDF（多附件按「通知书/决定/审查意见」等关键词挑主官文）；每份主官文建**两个子页**：有序号版（段落带【0001】编号，便于按段引用）+ 无序号版（标题加「【无序号版】」，干净可拷）；正文只抽一次、渲染两版（**扫描/图片型 PDF 无文本层时用 qwen-vl 逐页 OCR（上限 10 页），只 OCR 一次**），OCR 也拿不到则不建空页；只转主官文（892/1449/对比文件/公布文件不转）；同名子页已存在则更新。
- **新增 OA 汇总页「测试页面-写入新增OA」**：每案追加一行（12 列：案号/备注/OA收到日/OA发文日/答复期限/OA类别/跟进人/其它备注事项/人员分配/**分配人**/**分配时间**/是否正式立项），行上埋 `class="oaid-{id}"`（供分配页按 id 定位/回写）。分配人/分配时间在提交分配时回写（分配人=收到分配链接的人，按案号路由；分配时间=提交时刻）。备注：CN 办登=分案评估、补正=补正、其它 OA=同族首案/非同族首案（按同族 project_name 是否含 OA 判定）、预审案件加注。
- **projects 表**：INSERT，`id = oa_id`(uuid4)，project_type=中国答复及其他/海外答复及其他，customer=atw 客户简称等。
- **待分配表 `oa_assign_task`**：仅**成功写进 projects** 的案子写入（id + status）。

### 6. 立项即生成分配报告
对本轮立项每案调 `build_case_report + build_assignment_schemes` → 落 `oa_assign_report`，使随后点开分配链接即秒读缓存。

## 四、转 OA 立项通知（`oa/forward_oa.py`）

- 收件人 = 固定（杨姣 jiao.yang、薄佳璐 jialu.bo）+ 该客户公共邮箱（未列出客户兜底 patents_pa）。
- 抄送 = 固定 9 人（伍美欣/赵敏/李晶晶/oa/苏雅/姚涓涓/张琴/丁玲/王圆）。
- 主题 `【OA自动立项通知】{发文日-官文名-案号}`；正文 OP02 模板（预审/未公开另加注）。
- 附件：官文（US 盖章 PDF + Word、CN/EP 邮件官文）、892/1449 文献（PDF/Word）。
- **OA 分配链接**：不进转 OA 正文，**单独按案号路由收件人、均抄送海灵（hailing.bi）**，每轮按收件人分组，**每案一条链接 `{基址}/oa-assign?assignee={本人}&oaid={oa_id}`**——点开**直达该案**、且列表按 assignee 过滤（只显示分配给本人的案件；分配人按案号+OA类别路由算，与发信同源）。**无 oaid（如基址 `/oa-assign`）则显示汇总（全部）**。基址由 `pipeline_config.json` 的 `oa_assign_base_url` 提供。路由（`forward_oa._assign_notify_to`）：**补正类（OA类别含「补正」）→杨姣（jiao.yang），不看案号**；否则按案号——**20608 开头→王志刚（zhigang.wang）**；**20849/5*/6*/8* 开头→杨姣**；**其余→薛虹（hxue）**。

## 五、OA 人员分配（`report/oa_assign.py` + `web/assign.html`，report_server:8501）

入口 `/oa-assign`（全部待分配，供海灵/管理）、`/oa-assign?assignee={人}&oaid={oa_id}`（各分配人从邮件链接进：**列表过滤到该人 + 直达该案**）、`/oa-assign/{oa_id}`（汇总里定位到某案）。三栏：待分配列表 / 中栏 AI 案件报告 / 右栏人员方案。**过滤仅在带 oaid 时生效**（无 oaid=汇总）；过滤时左栏顶部标「{人} 的待分配案件（N 件）」。

### 1. AI 案件报告（`oa/oa_report_ai.py`）
中栏 markdown，首次打开时若 `oa_assign_report` 无缓存则现场生成（DeepSeek），生成后落库；含：
- 顶部「读取的文档」：列出本次实际读取的申请文件名 + 审意官文各文件名（缺失标「未找到/未获取」），便于核对报告依据的材料
- 一、案件基础信息　二、权利要求结构解析　三、技术方案速览　四、审查意见深度解析（前四类由 DeepSeek 依据**申请文件 + 审意 PDF** 生成；提示词默认读 atw `zxassist_result_instruction.mtype='oaInstruct'`）
- 内部人员档案（代码查 `projects/users` 拼，非 AI）
- 预估工作量（DeepSeek）
- 本次 OA 人员安排建议（下述 schemes 渲染）
- 申请文件按真实 NAS 定位（`MATCH_BY_CASE_NO`；普通 `Z:\{码-简称}\{组内号}\{案号}\*递交文件*`，含 -H 走众慧优创知识产权，US 取含 spec、CN 取含说明书/申请文件、EP 进新申请，取最新 docx，本层无则递归子目录）。
- 审意 PDF 按案号读 `attachment/{案号}/`，缺件回退 `_inbox`。

### 2. 人员安排方案（`oa/oa_schemes.py`）
DeepSeek 从**候选人 + 白名单 + 负荷**出 ≥3 组（每组答复负责人 + QC），提示词默认读 `mtype='oa_schemes'`：
- **档位**：案号 5/6 开头→普及；否则 US/EP→海外、CN→标准。
- **技术领域**：DeepSeek 从报告判定（通用/结构/生化）。
- **白名单**（`oa_assign_whitelist`）：从该档位×领域取 QC/梯队名单；连续性（本案/同族承办，来自 `oa_personnel.collect_candidates`）优先、梯队 1 优先；推荐人须在白名单∪候选池内（防编造）；角色空则同领域白名单兜底补人。
- **人员负荷**（`oa/oa_workload.py`）：读 Confluence 负荷页（pageId 151195467）抽饱和度%+请假/培训，优先低负荷、避开请假/培训。
- 在职判定：`users.status<>'离职'` 且 `usermail` 有值（无 usermail 视同离职）。

### 3. 选人与提交
- 自定义选人只能从 `users`（在职）搜索选择，不能手填（`/api/staff/list`）。
- 提交（单案/批量）：**回写 Wiki**「测试页面-写入新增OA」人员分配格（按 **oa_id + 案号双重比对**定位——案号取自 projects 的权威值，防手动复制导致 `class="oaid-{id}"` 被复制到别案号行而写错行；对不上任何行则不写，**追加不覆盖**），同时回写**分配人**（=收到分配链接的人，按案号路由）+ **分配时间**（提交时刻，空则填）+ 写 `projects`（leader/qc/participant）+ `oa_assign_task` 置已分配 + 把**选中结果+分配附言(postscript)+分配原因(customNote)**存入 `oa_assign_report.submit_json`（UPSERT，`save_submission`）。

## 六、OA 白名单维护（`web/whitelist.html` + `report/oa_whitelist.py`）

- 真源为 atw 表 `oa_assign_whitelist`（梯队×档位×领域→人员，值域开放可外拓）+ `oa_assign_tier_desc`。
- 维护页 `/oa-whitelist`：增删改**实时写 atw**；姓名从 `users` 搜索选择、强校验为在职 users。
- 一键「同步到 Wiki」：把 atw 全量回渲染写回 pageId 241276196（当前按钮隐藏，接口保留）。
- 名字简称↔全名对齐：`oa/resolve_whitelist_names.py` 回填 `username_zn`。

## 七、报告生成性能

三处生成，`save_report` UPSERT 不冲突：**立项即生成**（发链接即秒读）、**分配页懒生成**（缓存没有才现场）、**预热脚本**（`oa/prewarm_oa_reports.py` 后台补缺/`--force`）。

## 八、数据源 / 表 / Wiki 页 / 环境

| 类别 | 明细 |
|---|---|
| atw(MySQL) | projects、users、customer、oa_assign_task、oa_assign_report、oa_assign_whitelist、oa_assign_tier_desc、zxassist_result_instruction |
| IPEasy(SQL Server) | p_case_info（结案状态、案件主数据） |
| Confluence(10.10.70.90:9090) | OA信息记录表页、测试页面-写入新增OA、白名单页(241276196)、人员负荷页(151195467) |
| NAS(Z:\) | 申请文件（递交文件/新申请）、公布公告文件 |
| 外部 AI | DeepSeek(报告/方案/期限)、qwen-vl(审意 OCR)、USPTO ODP API(US 官文下载) |
| 服务 | report_server:8501（分配页 + REST + 白名单维护）；外部指令编辑系统 10.10.70.88:8082 |

## 九、关键配置（`scripts/pipeline_config.json`）

`accounts`、`sinks{oa,report}`、`send_email`、`send_assign_link`（是否发 OA 分配链接邮件，默认 true；false 则立项/转OA/生成报告照常，仅不发分配链接）、`oa_test_project_prefix`、`oa_assign_base_url`。环境变量：`DEEPSEEK_API_KEY`、`QWEN_API_KEY`、`OA_ASSIGN_BASE_URL`、`OA_SEND_ASSIGN_LINK`（0/false/no/off 关闭分配链接）、`PIPELINE_NO_EMAIL`、`USPTO_DOWNLOAD_LOG`。

## 十、待完善 / 已知边界

- US 对比文件抽取（`parse_us_refs`）优先用 892；号码只取到公开号/专利号（非申请号），日期列多为空；扫描件无文本层时暂不 OCR（回退 DeepSeek 也依赖文本层）。
- 官文正文转 Wiki 子页覆盖 US/CN/EP 主官文（`oa/word_to_wiki.py`，PDF/Word 皆可，扫描件走 qwen-vl OCR）；但其审意内容仍不参与 AI 报告第四类。CN/EP 多附件时按关键词挑主官文，命名不规范时可能挑错；OCR 有页数上限（10 页）与识别误差，超长官文尾部可能截断。
- 白名单同步 Wiki 按钮暂隐藏；外部 oaInstruct 提示词若含「人员档案/人员安排建议」段，DeepSeek 可能重复生成（应从提示词删除，交由代码查库/schemes）。
- NAS/atw/Confluence 为内网，相关功能须在可达内网的机器（report_server 所在机）运行。
