# 可复用资产库（总目录）

本文件是可复用资产库 `scripts/reusable/` 的索引。库把**目录（本文件）与抽取的模块放在一起**，目录结构本身即分层体系：

```text
scripts/reusable/
├── README.md            ← 本目录（分层索引）
├── foundation/          第一层 · 基础工具层（纯 Python，零外部依赖）
│   └── common/          日期 / 专利号 / JSON路径 / HTML
├── services/            第二层 · 外部服务与资源封装层（封装外部系统/API/库）
│   ├── llm_client.py    大模型服务（DeepSeek 文本 / qwen 图片）
│   ├── email_core/      邮件系统（IMAP 收 / SMTP 发 / 解析 / 断点）
│   └── doc_utils/       文档与 PDF（表单填充 / PDF-A / 抽文本）
└── examples/            各模块使用示例
```

每个模块均带接口说明（逐函数：调用方法/输入/返回）与使用示例；均为纯新增，尚未迁移原调用方。

## 一览

| 层次 | 模块 | 位置（库内） | 接口说明 | 示例 |
|---|---|---|---|---|
| 基础工具层 | common | `foundation/common/` | `foundation/common/README.md` | `examples/common_utils_demo.py` |
| 外部服务封装层 | llm_client | `services/llm_client.py` | `services/llm_client.README.md` | `examples/llm_client_basic.py` |
| 外部服务封装层 | email_core | `services/email_core/` | `services/email_core/README.md` | `examples/email_core_demo.py` |
| 外部服务封装层 | doc_utils | `services/doc_utils/` | `services/doc_utils/README.md` | `examples/doc_utils_demo.py` |

---

## 按能力检索（想做什么 → 找哪个模块）

按使用需求检索现成件，不一定要先懂分层。

| 想做什么 | 去哪个模块 | 函数/子模块 |
|---|---|---|
| 解析日期（ISO / `02/14/2026` / `February 12, 2026`） | foundation/common → dates | `parse_date` |
| 算期限/加月（月末落点） | foundation/common → dates | `add_months` |
| 期限逢周末移到工作日 | foundation/common → dates | `move_to_workday` |
| 专利公开号归一化 | foundation/common → patents | `normalize_pub_no` |
| 深嵌套 dict/list 按点号路径读写 | foundation/common → jsonpath | `get_by_path` / `set_by_path` |
| 剥 HTML 标签 / `&nbsp;` | foundation/common → html_text | `strip_tags` |
| 切开一行 HTML 的表格单元格 | foundation/common → html_text | `split_cells` |
| 调 DeepSeek / qwen 文本（可要 JSON） | services → llm_client | `chat` |
| 扫描件 OCR / 图片判断（多模态） | services → llm_client | `vision` |
| 读收件箱（IMAP，含 OAuth2/降级密码） | services → email_core | `read_emails` |
| 增量去重（只取新邮件） | services → email_core.checkpoint | `filter_new_emails` / `update_checkpoint` |
| 邮件归档（不可逆） | services → email_core | `move_emails` |
| 发 HTML 邮件（SMTP） | services → email_core | `send_html` |
| 解析一封邮件的正文/附件/地址/日期 | services → email_core.mime_parse | `parse_message` 等 |
| 填 AcroForm 表单 | services → doc_utils | `fill_pdf_form` |
| PDF 转 PDF/A-2b | services → doc_utils | `to_pdfa` / `others_to_pdfa` |
| 抽 PDF 文本层 | services → doc_utils.doc_text | `pdf_text` |
| 抽 docx 文本 / 切说明书权要 | services → doc_utils.doc_text | `docx_text` / `split_spec` |
| 定位最新匹配的 docx | services → doc_utils.doc_text | `pick_latest_docx` |

---

## 第一层 · 基础工具层

### common — 通用纯函数工具

零依赖、零业务耦合。按能力域分四个子模块：

| 子模块 | 能力 | 函数 |
|---|---|---|
| dates | 日期解析/计算 | `parse_date` / `add_months` / `move_to_workday` |
| patents | 专利号归一化 | `normalize_pub_no` |
| jsonpath | 点号路径读写 | `get_by_path` / `set_by_path` |
| html_text | HTML 文本处理 | `strip_tags` / `split_cells` |

出处：`oa/filter_oa_email.py`（日期）、`oa/parse_us_refs.py`（专利号）、`submission/qa_seed.py`（JSON 路径）、`oa/oainfo_cli.py`（HTML）。

---

## 第二层 · 外部服务与资源封装层

### llm_client — 大模型服务封装

统一 DeepSeek/qwen 调用，key 走配置、异常 fail-soft 返回 None。

| 能力 | 函数 |
|---|---|
| 文本调用（可自动解析 JSON） | `chat` |
| 图片多模态调用（OCR/判断） | `vision` |

出处：`oa/{filter_oa_email,oa_schemes,oa_report_ai,parse_us_pdf,parse_cn_pdf,parse_us_refs,word_to_wiki}.py`、`report/classify_report.py`、`submission/qa_seed.py` 内联的 16 处 DeepSeek/qwen 调用。

### email_core — 邮件系统封装

IMAP 收信、SMTP 发信、MIME 解析、增量去重。按能力域分五个子模块：

| 子模块 | 能力 | 函数 |
|---|---|---|
| config | 账号配置读取 | `load_config` / `get_account_config` |
| imap_client | 收信 | `get_oauth2_token` / `login_imap` / `list_folders` / `read_emails` / `move_emails` |
| mime_parse | 邮件解析 | `decode_str` / `html_to_text` / `get_body` / `get_attachments` / `save_attachments` / `parse_email_date` / `parse_address_list` / `parse_message` |
| checkpoint | 增量去重 | `set_checkpoint_path` / `load_checkpoint` / `save_checkpoint` / `get_checkpoint` / `update_checkpoint` / `filter_new_emails` |
| smtp_client | 发信 | `get_smtp_oauth2_token` / `send_smtp` / `send_html` |

出处：`oa/read_email.py`（收信/解析/断点，与 `report/read_email.py` 逐字相同）、`report/submission_mailer.py`（发信）。

### doc_utils — 文档与 PDF 处理

AcroForm 填表、PDF/A 转换、文档抽文本。按能力域分三个子模块：

| 子模块 | 能力 | 函数 |
|---|---|---|
| pdf_form | 表单填充 | `fill_pdf_form` |
| pdfa | PDF→PDF/A-2b | `gs_bin` / `to_pdfa` / `others_to_pdfa` |
| doc_text | 文档抽文本/切分 | `pdf_text` / `docx_text` / `split_spec` / `pick_latest_docx` |

出处：`submission/common.py`（填表）、`run_uspto_upload.py`（PDF/A）、`oa/parse_us_refs.py` 与 `oa/oa_report_ai.py`（抽文本/切分）。
