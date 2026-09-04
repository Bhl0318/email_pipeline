# doc_utils —— 可复用文档处理工具集（接口说明）

抽自 `submission/common.py`、`run_uspto_upload.py`、`oa/oa_report_ai.py`、`oa/parse_us_refs.py`，逻辑不变，零业务耦合。目前为纯新增，未迁移原调用方。
不含 `flatten_pdf`（耦合 pdfRest 云）、扫描件 OCR（耦合大模型——用 `llm_client.vision` 组合）。
可运行示例：`python3 scripts/reusable/examples/doc_utils_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/services")
from doc_utils import fill_pdf_form, gs_bin, to_pdfa, others_to_pdfa, \
    pdf_text, docx_text, split_spec, pick_latest_docx
```

## 逐函数：调用方法 / 输入 / 返回

### pdf_form（`pdf_form.py`，依赖 PyMuPDF）

| 函数 | 调用方法 | 输入 | 返回 |
|---|---|---|---|
| `fill_pdf_form` | `fill_pdf_form("POA.pdf", "out.pdf", {"name": "张三", "cb": True})` | template_pdf: 模板路径；output_pdf: 输出路径；field_updates: dict（checkbox 命中即勾 Yes，模板没有的字段名忽略） | 无（写出 output_pdf）；模板不存在抛 FileNotFoundError |

### pdfa（`pdfa.py`，依赖系统 Ghostscript）

| 函数 | 调用方法 | 输入 | 返回 |
|---|---|---|---|
| `gs_bin` | `gs_bin()` | 无 | Ghostscript 可执行路径 str；找不到→None |
| `to_pdfa` | `to_pdfa("a.pdf", "out_dir")` | src: PDF 路径；out_dir: 输出目录；timeout: int=300 | str（输出 PDF/A-2b 路径）；无 gs 或失败抛异常 |
| `others_to_pdfa` | `others_to_pdfa(["a.pdf","b.docx"], "out_dir")` | others: 路径列表；out_dir: 输出目录 | list[str]（PDF 转 PDF/A、非 PDF 原样返回） |

### doc_text（`doc_text.py`，惰性依赖 PyMuPDF / python-docx）

| 函数 | 调用方法 | 输入 | 返回 |
|---|---|---|---|
| `pdf_text` | `pdf_text("oa.pdf", max_pages=6)` | pdf_path: str；max_pages: int=6 | str（文本层）；**扫描件无文本层→`""`**（需 OCR 另用 llm_client.vision） |
| `docx_text` | `docx_text("spec.docx")` | path: str | str（python-docx，失败退解压 XML）；缺文件→`""` |
| `split_spec` | `desc, claims = split_spec(text)` | spec_text: str（说明书全文） | (description, claims)；权要以 WHAT IS CLAIMED IS/CLAIMS/权利要求 起、到 ABSTRACT/摘要 止；切不出→claims=`""` |
| `pick_latest_docx` | `pick_latest_docx("申请文件", keywords=["spec"])` | dirpath: str；keywords: list[str]｜None | str（最新匹配 docx 路径，本层优先、无则递归子目录）；无→None |

## 使用示例

```python
from doc_utils import pick_latest_docx, docx_text, split_spec, pdf_text, \
    fill_pdf_form, gs_bin, to_pdfa

# 1. 定位并抽取说明书，再切成 说明/权要（实测输出见 demo）
spec = pick_latest_docx("申请文件", keywords=["spec"])
# -> '.../2022-09-15-SPEC-20618-0424US00.docx'
text = docx_text(spec)                       # -> 说明书全文 str
desc, claims = split_spec(text)
# desc 约 10.9 万字；claims 以 'WHAT IS CLAIMED IS:' 起，约 2.8 万字

# 2. 抽 PDF 文本层（扫描件无文本层返回 ''，需 OCR 时用 llm_client.vision）
pdf_text("oa.pdf", max_pages=6)              # -> 文本 str 或 ''

# 3. 填 AcroForm 表单
fill_pdf_form("POA.pdf", "out.pdf", {"applicant_name": "张三", "checkbox_a": True})

# 4. 转 PDF/A-2b（需 Ghostscript）
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
