# 可复用资产库（总目录）

可复用资产库 `scripts/reusable/`。分层对应《可复用模块与资产整理需求文档》的三层模型：**基础通用层 / 业务支撑层 / 应用集成层**。库把索引（本文件）与模块放在一起，目录即分层。

```text
scripts/reusable/
├── README.md              ← 本目录（分层索引）
├── foundation/   基础通用层 —— common / email_core / doc_utils
├── business/     业务支撑层 —— doc_extract / rule_engine / doc_generator
├── integration/  应用集成层 —— llm_client
├── datasets/     数据资产 —— 模板 / 规则表 / 提示词（归纳副本）
└── examples/              各模块使用示例
```

> 除已抽取模块外，email_pipeline 中还有其它已识别、可复用的模块级资产（规则引擎/编排骨架等），见文末"待抽取模块级资产"。

## 已抽取模块一览

| 层次 | 模块 | 做什么用 | 位置 | 接口说明 | 示例 |
|---|---|---|---|---|---|
| 基础通用层 | common | 与业务无关的通用小工具：解析/计算日期、归一化专利号、按路径存取嵌套数据、处理 HTML 文本 | `foundation/common/` | `foundation/common/README.md` | `examples/common_utils_demo.py` |
| 基础通用层 | email_core | 收发和解析邮件：IMAP 收信、解析正文/附件、按记录增量去重、SMTP 发信 | `foundation/email_core/` | `foundation/email_core/README.md` | `examples/email_core_demo.py` |
| 基础通用层 | doc_utils | 处理 PDF/Word：填 PDF 表单、转 PDF/A、从 PDF/docx 抽文本并切分说明书 | `foundation/doc_utils/` | `foundation/doc_utils/README.md` | `examples/doc_utils_demo.py` |
| 业务支撑层 | doc_extract | 从 PDF 抽结构化数据，正则→大模型→图片OCR 三级兜底（组合 doc_utils+llm_client） | `business/doc_extract/` | `business/doc_extract/README.md` | `examples/doc_extract_demo.py` |
| 业务支撑层 | rule_engine | 规则外置 JSON，按多维键分级查表（通配符→精确→有序兜底）出结论 | `business/rule_engine/` | `business/rule_engine/README.md` | `examples/rule_engine_demo.py` |
| 业务支撑层 | doc_generator | 按数据生成表单的骨架：字段映射→选模板→编排一组生成器（统一契约+逐个兜底） | `business/doc_generator/` | `business/doc_generator/README.md` | `examples/doc_generator_demo.py` |
| 应用集成层 | llm_client | 统一调用大模型：一个入口发文本/图片给 DeepSeek/千问，密钥集中配置，出错不中断 | `integration/llm_client.py` | `integration/llm_client.README.md` | `examples/llm_client_basic.py` |

## 按能力检索（想做什么 → 找哪个）

| 想做什么 | 模块 | 函数 |
|---|---|---|
| 解析日期 / 加月算期限 / 逢周末移工作日 | common.dates | `parse_date` / `add_months` / `move_to_workday` |
| 专利公开号归一化 | common.patents | `normalize_pub_no` |
| 按点号路径读写嵌套 dict/list | common.jsonpath | `get_by_path` / `set_by_path` |
| 剥 HTML 标签 / 切表格单元格 | common.html_text | `strip_tags` / `split_cells` |
| 读收件箱（IMAP）/ 增量只取新邮件 / 归档 / 发信 | email_core | `read_emails` / `filter_new_emails` / `move_emails` / `send_html` |
| 解析一封邮件的正文/附件/地址/日期 | email_core.mime_parse | `parse_message` |
| 填 AcroForm 表单 / 转 PDF/A / 抽文本 / 切说明书 | doc_utils | `fill_pdf_form` / `to_pdfa` / `pdf_text` / `docx_text` / `split_spec` |
| 调大模型文本（可要 JSON）/ 图片 OCR | llm_client | `chat` / `vision` |
| 从 PDF 抽结构化数据（正则→大模型→图片 三级兜底） | doc_extract | `extract_from_pdf` |
| 按多维键查规则表、层层兜底出结论 | rule_engine | `load_rules` / `resolve` |
| 按数据生成表单（字段映射/选模板/编排一组生成器） | doc_generator | `map_fields` / `select_template` / `build_documents` |

---

## 一、基础通用层

纯技术工具，不含任何专利/邮件业务规则，换个项目也能直接用：日期与字符串处理、收发解析邮件、PDF/Word 读写。

### common — 通用纯函数工具
零依赖、零业务耦合。按能力域分四个子模块：

| 子模块 | 作用 | 函数 |
|---|---|---|
| dates | 日期解析与计算 | `parse_date` / `add_months` / `move_to_workday` |
| patents | 专利号归一化 | `normalize_pub_no` |
| jsonpath | 按点号路径读写嵌套数据 | `get_by_path` / `set_by_path` |
| html_text | HTML 文本处理 | `strip_tags` / `split_cells` |

出处：`oa/filter_oa_email.py`（日期）、`oa/parse_us_refs.py`（专利号）、`submission/qa_seed.py`（JSON 路径）、`oa/oainfo_cli.py`（HTML）。

### email_core — 邮件收发核心
封装邮箱的收、发、解析与增量去重，账号信息由调用方传入。按能力域分五个子模块：

| 子模块 | 作用 | 函数 |
|---|---|---|
| config | 读账号配置 | `load_config` / `get_account_config` |
| imap_client | 收信 | `get_oauth2_token` / `login_imap` / `list_folders` / `read_emails` / `move_emails` |
| mime_parse | 把邮件解析成结构化数据 | `decode_str` / `html_to_text` / `get_body` / `get_attachments` / `save_attachments` / `parse_email_date` / `parse_address_list` / `parse_message` |
| checkpoint | 记录已处理、增量去重 | `set_checkpoint_path` / `load_checkpoint` / `save_checkpoint` / `get_checkpoint` / `update_checkpoint` / `filter_new_emails` |
| smtp_client | 发信 | `get_smtp_oauth2_token` / `send_smtp` / `send_html` |

出处：`oa/read_email.py`（收信/解析/断点，与 `report/read_email.py` 逐字相同）、`report/submission_mailer.py`（发信）。

### doc_utils — 文档与 PDF 处理
填表单、转 PDF/A、抽文本，与具体业务无关。按能力域分三个子模块：

| 子模块 | 作用 | 函数 |
|---|---|---|
| pdf_form | 填 PDF AcroForm 表单 | `fill_pdf_form` |
| pdfa | PDF 转 PDF/A-2b（存档格式） | `gs_bin` / `to_pdfa` / `others_to_pdfa` |
| doc_text | 从文档抽文本、切分说明书 | `pdf_text` / `docx_text` / `split_spec` / `pick_latest_docx` |

出处：`submission/common.py`（填表）、`run_uspto_upload.py`（PDF/A）、`oa/parse_us_refs.py` 与 `oa/oa_report_ai.py`（抽文本/切分）。

---

## 二、业务支撑层

针对本领域（专利 OA/递交）的处理组件：内部有一套固定流程，但把具体的正则、规则表、模板等业务内容留给调用方传入，所以同一套流程能用在不同案子/客户上。

### doc_extract — 分级文档抽取组件
从 PDF 抽结构化数据，按"正则 → 大模型读文本 → 扫描件图片OCR"三级自动兜底；调用方给正则/提示词，内部编排。是模块级组件，组合了 `doc_utils`（取文本）和 `llm_client`（调模型）。

| 能力 | 作用 | 入口 |
|---|---|---|
| 三级兜底抽取 | 给 PDF + 正则/提示词 → 结构化结果 | `extract_from_pdf` |

出处：范式抽象自 `oa/parse_us_pdf.py`、`oa/parse_cn_pdf.py`、`oa/parse_us_refs.py`。

### rule_engine — 分级规则解析引擎
把规则外置成嵌套 JSON，按多维键逐层查表，最后一层"通配符 → 精确 → 有序兜底"命中。用于任何"按几个维度查规则、层层兜底出结论"的场景。引擎只管查表，维度键怎么算由调用方决定。

| 能力 | 作用 | 入口 |
|---|---|---|
| 读规则表 | 加载嵌套规则 JSON（带缓存） | `load_rules` |
| 分级查表 | 按多维键+通配符+有序兜底命中 | `resolve` |

出处：`report/read_email.py`（`_load_oa_rules`/`_resolve_oa_action`）+ `report/oa_report_rules.json`。

### doc_generator — 文档生成器骨架
按数据生成表单（PDF/docx）的通用骨架，把流程拆成三步分离：字段映射、模板选择、生成器编排（统一结果契约、逐个兜底、汇总）。骨架只管机制，各生成器怎么填模板是业务（填 PDF 用 `doc_utils.fill_pdf_form`）。

| 能力 | 作用 | 入口 |
|---|---|---|
| 字段映射 | 原始数据按规格转成生成器要的结构 | `map_fields` |
| 模板选择 | 按条件键挑模板 | `select_template` |
| 生成器编排 | 跑一组生成器、逐个兜底、汇总 | `build_documents` |

出处：范式抽象自 `report/submission/`（fields_mapping ↔ 各 *_generator、filing_preparation）。

---

## 三、应用集成层

对外把一件事封装成一个入口、内部组合调用下层能力的模块（如统一调大模型：调用方只管发文本/图片，取文本、选模型、解析结果、出错兜底都在里面）。

### llm_client — 大模型调用与路由
一个入口调 DeepSeek（文本）或千问（图片），密钥集中配置、可选自动解析 JSON、出错返回 None 不中断主流程。

| 能力 | 作用 | 函数 |
|---|---|---|
| 文本调用 | 发文本给大模型，可要求返回并解析 JSON | `chat` |
| 图片调用 | 发图片给多模态模型做 OCR/判断 | `vision` |

出处：`oa/{filter_oa_email,oa_schemes,oa_report_ai,parse_us_pdf,parse_cn_pdf,parse_us_refs,word_to_wiki}.py`、`report/classify_report.py`、`submission/qa_seed.py` 内联的 16 处 DeepSeek/千问调用。

---

## 四、数据资产（模板 / 规则表 / 提示词）

按需求文档 §2.2，数据资产与代码模块**并列管理、不混入代码目录**。已归纳到 `datasets/` 一处（详见 `datasets/README.md`）。

| 类型 | 数据资产 | 被哪个模块消费 | 库内位置 | 真源（流水线仍读这里） |
|---|---|---|---|---|
| 模板 | US 递交空白表单（POA / ADS / Transmittal×3 / Declaration×2 / Assignment 共 8 件） | doc_generator、doc_utils.fill_pdf_form | `datasets/templates/us_filing/` | `report/submission/templates/` |
| 模板 | 汇报信模板库（CN/US/EP 结项+OA 各类，md + docx） | 汇报信生成 | `datasets/templates/report_letters/` | `scripts/templates/` |
| 规则表 | OA 分派规则（国别×类型×客户码→动作） | rule_engine | `datasets/rules/oa_report_rules.json` | `report/oa_report_rules.json` |
| 提示词/指令 | 可外部编辑的模型指令（改库即生效） | llm_client 的调用方（指令外置） | `datasets/prompts/`（说明，非文件） | atw 表 `zxassist_result_instruction` |

> `datasets/` 是**归纳副本**，方便成套查看/打包；在跑的流水线仍从"真源"读取，改副本不生效，真源更新后需刷新副本。

---

## 附：待抽取的模块级资产（已识别）

email_pipeline 中除上述工具型模块外，还有**模块级**可复用能力，与业务规则有耦合、尚未抽为独立模块，先按需求文档层次登记，供后续抽取：

| 层次 | 资产 | 做什么用 | 现位置 |
|---|---|---|---|
| 业务支撑层 | 指令(提示词)外置 | 提示词存库、改库即生效、读不到回退默认 | `oa/oa_schemes.py`、`oa/oa_report_ai.py`（读 `zxassist_result_instruction`） |
| 应用集成层 | 单入口扇出编排 | 一封邮件只读一次、只分类一次，按开关扇出多个下游 | `scripts/main.py` |
| 应用集成层 | 隔离加载 | 让同名模块（oa/ 与 report/）在同进程互不串味 | `scripts/loader.py` |
| 应用集成层 | 邮件分类引擎 | 按发件域分派 CN/US/EP，抽案号/类型/期限、判断是否立项 | `oa/filter_oa_email.py`、`report/classify_report.py` |
