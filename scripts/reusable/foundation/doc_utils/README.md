# doc_utils —— 文档与 PDF 处理（接口说明）

**做什么用**：处理 PDF/Word 文档——填 PDF 表单、把 PDF 转成 PDF/A 存档格式、从 PDF/docx 抽文本并把说明书切成"说明"和"权利要求"。与具体业务无关。从现有业务文件抽出，逻辑不变。
不含 `flatten_pdf`（耦合 pdfRest 云）、扫描件 OCR（耦合大模型——用 `llm_client.vision` 组合）。

可运行示例：`python3 scripts/reusable/examples/doc_utils_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/foundation")
from doc_utils import fill_pdf_form, gs_bin, to_pdfa, others_to_pdfa, \
    pdf_text, docx_text, split_spec, pick_latest_docx
```

## 逐函数：作用 / 输入 / 返回

### pdf_form（`pdf_form.py`，依赖 PyMuPDF）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `fill_pdf_form(template_pdf, output_pdf, field_updates)` | 用给定字段值填 PDF AcroForm 表单并另存 | template_pdf: 模板路径；output_pdf: 输出路径；field_updates: dict（checkbox 命中即勾 Yes，模板没有的字段名忽略） | 无（写出 output_pdf）；模板不存在抛 FileNotFoundError |

### pdfa（`pdfa.py`，依赖系统 Ghostscript）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `gs_bin()` | 找到本机 Ghostscript 可执行文件 | 无 | 路径 str；找不到→None |
| `to_pdfa(src, out_dir, timeout=300)` | 把一个 PDF 转成 PDF/A-2b 存档格式 | src: PDF 路径；out_dir: 输出目录；timeout: int（**可选**，默认 300 秒） | 输出 PDF/A 路径 str；无 gs 或失败抛异常 |
| `others_to_pdfa(others, out_dir)` | 批量把 PDF 转 PDF/A，非 PDF 原样保留 | others: 路径列表；out_dir: 输出目录 | list[str] |

### doc_text（`doc_text.py`，惰性依赖 PyMuPDF / python-docx）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `pdf_text(pdf_path, max_pages=6)` | 抽 PDF 的文本层 | pdf_path: str；max_pages: int（**可选**，默认前 6 页） | str（文本层）；**扫描件无文本层→`""`**（需 OCR 另用 llm_client.vision） |
| `docx_text(path)` | 抽 docx 的纯文本 | path: str | str（python-docx，失败退解压 XML）；缺文件→`""` |
| `split_spec(spec_text)` | 把说明书全文切成"说明"和"权利要求"两部分 | spec_text: str（说明书全文） | (description, claims)；切不出权要则 claims=`""` |
| `pick_latest_docx(dirpath, keywords=None)` | 在目录里找最新的 docx（可按文件名关键词过滤） | dirpath: str；keywords: list[str]（**可选**，命中任一即可，默认不过滤） | 最新匹配 docx 路径 str；无→None |

## 使用示例

```python
from doc_utils import pick_latest_docx, docx_text, split_spec, pdf_text, fill_pdf_form, gs_bin, to_pdfa

# 定位说明书 → 抽全文 → 切成 说明/权要（实测输出见 demo）
spec = pick_latest_docx("申请文件", keywords=["spec"])   # -> '.../SPEC-20618-0424US00.docx'
text = docx_text(spec)                                   # -> 说明书全文 str
desc, claims = split_spec(text)
# desc 约 10.9 万字；claims 以 'WHAT IS CLAIMED IS:' 起，约 2.8 万字

pdf_text("oa.pdf", max_pages=6)              # -> 文本 str 或 ''（扫描件）
fill_pdf_form("POA.pdf", "out.pdf", {"applicant_name": "张三", "checkbox_a": True})
if gs_bin():
    to_pdfa("draft.pdf", "out_dir")          # -> 'out_dir/draft.pdf'
```

## 来源

| 本模块 | 抽自 |
|---|---|
| pdf_form.fill_pdf_form | `submission/common.py` `fill_pdf_form` |
| pdfa.* | `run_uspto_upload.py` `_gs_bin/_to_pdfa/_others_to_pdfa` |
| doc_text.pdf_text | `oa/parse_us_refs.py` `_pdf_to_text` |
| doc_text.docx_text/split_spec/pick_latest_docx | `oa/oa_report_ai.py` 同名私有函数 |
