# 可复用资产库（总目录）

可复用资产库 `scripts/reusable/`。分层对应《可复用模块与资产整理需求文档》的三层模型：**基础通用层 / 业务支撑层 / 应用集成层**。库把索引（本文件）与模块放在一起，目录即分层。

```text
scripts/reusable/
├── README.md              ← 本目录（分层索引）
├── foundation/   基础通用层 —— common / email_core / doc_utils
├── integration/  应用集成层 —— llm_client
└── examples/              各模块使用示例
```

> 业务支撑层目前尚无已抽取的独立模块；email_pipeline 中已识别、可复用的业务支撑层/应用集成层**模块级**资产，见文末"待抽取模块级资产"。

## 已抽取模块一览

| 层次 | 模块 | 做什么用 | 位置 | 接口说明 | 示例 |
|---|---|---|---|---|---|
| 基础通用层 | common | 与业务无关的通用小工具：解析/计算日期、归一化专利号、按路径存取嵌套数据、处理 HTML 文本 | `foundation/common/` | `foundation/common/README.md` | `examples/common_utils_demo.py` |
| 基础通用层 | email_core | 收发和解析邮件：IMAP 收信、解析正文/附件、按记录增量去重、SMTP 发信 | `foundation/email_core/` | `foundation/email_core/README.md` | `examples/email_core_demo.py` |
| 基础通用层 | doc_utils | 处理 PDF/Word：填 PDF 表单、转 PDF/A、从 PDF/docx 抽文本并切分说明书 | `foundation/doc_utils/` | `foundation/doc_utils/README.md` | `examples/doc_utils_demo.py` |
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

---

## 一、基础通用层

与具体业务无关、多项目可直接用的能力。

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

在基础能力之上、服务多个业务场景的处理模块。目前尚无已抽取的独立模块，下列为已识别、待抽取的模块级资产（见文末）。

---

## 三、应用集成层

与具体应用运行方式相关、组合底层能力的模块。

### llm_client — 大模型调用与路由
一个入口调 DeepSeek（文本）或千问（图片），密钥集中配置、可选自动解析 JSON、出错返回 None 不中断主流程。

| 能力 | 作用 | 函数 |
|---|---|---|
| 文本调用 | 发文本给大模型，可要求返回并解析 JSON | `chat` |
| 图片调用 | 发图片给多模态模型做 OCR/判断 | `vision` |

出处：`oa/{filter_oa_email,oa_schemes,oa_report_ai,parse_us_pdf,parse_cn_pdf,parse_us_refs,word_to_wiki}.py`、`report/classify_report.py`、`submission/qa_seed.py` 内联的 16 处 DeepSeek/千问调用。

---

## 附：待抽取的模块级资产（已识别）

email_pipeline 中除上述工具型模块外，还有**模块级**可复用能力，与业务规则有耦合、尚未抽为独立模块，先按需求文档层次登记，供后续抽取：

| 层次 | 资产 | 做什么用 | 现位置 |
|---|---|---|---|
| 业务支撑层 | 文档解析范式 | 从官文 PDF 抽答复期限/对比文件，正则→大模型→图片 OCR 三级兜底 | `oa/parse_cn_pdf.py`、`oa/parse_us_pdf.py`、`oa/parse_us_refs.py` |
| 业务支撑层 | 规则引擎 | 客户×官文类型×次数 → 动作(立项/转发/跳过)，规则外置 JSON、多级 fallback | `report/read_email.py`（`_resolve_oa_action`）+ `report/oa_report_rules.json` |
| 业务支撑层 | 指令(提示词)外置 | 提示词存库、改库即生效、读不到回退默认 | `oa/oa_schemes.py`、`oa/oa_report_ai.py`（读 `zxassist_result_instruction`） |
| 业务支撑层 | 文档生成器骨架 | "字段映射 ↔ 生成器"分离，按数据生成 PDF/docx 表单 | `report/submission/`（fields_mapping + 各 *_generator） |
| 应用集成层 | 单入口扇出编排 | 一封邮件只读一次、只分类一次，按开关扇出多个下游 | `scripts/main.py` |
| 应用集成层 | 隔离加载 | 让同名模块（oa/ 与 report/）在同进程互不串味 | `scripts/loader.py` |
| 应用集成层 | 邮件分类引擎 | 按发件域分派 CN/US/EP，抽案号/类型/期限、判断是否立项 | `oa/filter_oa_email.py`、`report/classify_report.py` |
