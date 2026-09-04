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

## 整理思路（模块化方法）

基于现有 DS 应用（email_pipeline）的开发，按"**是否与具体业务耦合**"识别可复用件：与客户/国别/人名等业务规则绑定的不动，**零业务耦合**的抽成独立模块。抽出的模块再按"**依赖什么**"分层——纯语言工具在底层（`foundation/`），封装外部系统/服务的在上层（`services/`）；每个模块内部再按能力域分子模块。目的是形成"层次 → 分组 → 模块 → 函数"的结构，而不是把几十个函数平铺罗列。

每个模块均带接口说明（逐函数：调用方法/输入/返回）与使用示例；均为纯新增，尚未迁移原调用方。

## 一览

| 层次 | 模块 | 位置（库内） | 接口说明 | 示例 |
|---|---|---|---|---|
| 基础工具层 | common | `foundation/common/` | `foundation/common/README.md` | `examples/common_utils_demo.py` |
| 外部服务封装层 | llm_client | `services/llm_client.py` | `services/llm_client.README.md` | `examples/llm_client_basic.py` |
| 外部服务封装层 | email_core | `services/email_core/` | `services/email_core/README.md` | `examples/email_core_demo.py` |
| 外部服务封装层 | doc_utils | `services/doc_utils/` | `services/doc_utils/README.md` | `examples/doc_utils_demo.py` |

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
