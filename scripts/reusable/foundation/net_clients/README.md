# net_clients —— 网络与服务调用客户端（接口说明）

**做什么用**：从外部专利数据源下文档的两个客户端——按申请号从 USPTO 官方 API 下官文、按号从 FreePatentsOnline 下专利 PDF。与业务无关。从现有业务文件抽出，逻辑不变；USPTO 的 API key 改为走配置（不再硬编码）。

可运行示例：`python3 scripts/reusable/examples/net_clients_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/foundation")
from net_clients import USPTOApplication, download_patent_pdf
```

USPTO key 优先级：`api_key` 参数 > 环境变量 `USPTO_API_KEY` > `scripts/email_config.json` 的 `uspto.api_key`。

## uspto（`uspto.py`，依赖 requests）

### `USPTOApplication(download_dir="output", mail_id=None, project=None, log_path=None, api_key=None)`
**作用**：按申请号从 USPTO 官方 API 下文档的客户端。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `download_dir` | 可选 | 下载基目录，默认 "output" |
| `project` | 可选 | 项目子目录名（下到 `download_dir/project/`） |
| `log_path` | 可选 | JSONL 日志路径；默认 `download_dir/uspto_download_log.jsonl`，可用环境变量 `USPTO_DOWNLOAD_LOG` 覆盖 |
| `api_key` | 可选 | 不给则走环境变量/配置 |

### `USPTOApplication.downLoad_Documents_ByAPI(application, document_code, official_date, project, descriptionWiki, kind="oa")`
**作用**：列出申请下的文档，按 documentCode + officialDate 精确匹配并逐个下载。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `application` | **必填** | 申请号 |
| `document_code` | **必填** | 文档代码（如 CTNF/CTFR/EGRANT.PDF） |
| `official_date` | **必填** | 官方日期 YYYY-MM-DD |
| `project` | **必填** | 项目名（用于命名/归目录） |
| `descriptionWiki` | **必填** | 文件名用的描述（空则用 API 返回的描述） |
| `kind` | 可选 | "oa"(官文)/"ref"(892·1449)，默认 oa，仅记日志用 |

**返回**：`{project: [本地文件路径...]}`（无匹配/失败为空）；下载后可查 `app.last_http_status`（403=未公开/受限）。

其它方法：`filter_documents(documents, code, date)`（挑匹配文档，纯函数）、`sanitize_filename(name)`（清理非法字符）、`downLoad_file(...)`（下单个文件）。模块级 `log_download(entry, log_path)` 写 JSONL 日志。

## patent_pdf（`patent_pdf.py`，建议装 curl_cffi）

### `download_patent_pdf(raw_no, out_path=None, session=None)`
**作用**：按号从 FreePatentsOnline 下一件专利 PDF（curl_cffi 绕 Cloudflare，抠页面 iframe 的 S3 直链再下、校验 %PDF）。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `raw_no` | **必填** | 专利号，多种写法（`US20250150762A1`/`20250150762`/`US 2025/0150762 A1`/`CN110693604A`） |
| `out_path` | 可选 | 输出路径，默认 `{数字号}.pdf` |
| `session` | 可选 | 复用会话（批量下多件时传同一个） |

**返回**：本地路径 str；失败→None。

## 使用示例

```python
from net_clients import USPTOApplication, download_patent_pdf

# USPTO 官文（key 走参数/环境变量/配置）
app = USPTOApplication(download_dir="out", project="20849-0032US01")
app.downLoad_Documents_ByAPI("17456882", "CTNF", "2025-02-11", "20849-0032US01", "官文")
# -> {"20849-0032US01": ["out/20849-0032US01/2025-02-11-...-....pdf"]}

# FreePatentsOnline 专利 PDF
download_patent_pdf("US20250150762A1", "out.pdf")   # -> 'out.pdf' 或 None

# 纯逻辑（离线，见 demo）
app.filter_documents(bag, "CTNF", "2025-02-11")     # 挑匹配文档
```

## 来源与改动

- 抽自：`oa/downloadByAPI.py`（USPTO）、`oa/download_patent_pdf.py`（FPO）。
- 改动：USPTO API key 由硬编码改为 参数 > 环境变量 `USPTO_API_KEY` > `email_config.json` 的 `uspto.api_key`；其余逻辑不变。
