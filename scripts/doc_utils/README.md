# doc_utils —— 可复用文档处理工具集（接口说明）

抽自 `report/submission/common.py`、`run_uspto_upload.py`、`oa/oa_report_ai.py`、`oa/parse_us_refs.py`，
逻辑不变，零业务耦合。目前为纯新增资产，未迁移原调用方。

不含：`flatten_pdf`（耦合 pdfRest 云服务与凭据）、扫描件 OCR（耦合大模型——用 `llm_client.vision` 逐页图片识别来组合）。

可运行示例：`python3 scripts/examples/doc_utils_demo.py`（对 `申请文件/` 真实样本跑文本抽取/切分；PDF/A 需 Ghostscript，缺则示范写法）。

## 如何调

```python
import os, sys
sys.path.insert(0, "<...>/scripts")
from doc_utils import fill_pdf_form, to_pdfa, docx_text, pdf_text, split_spec, pick_latest_docx
```

## 接口

### pdf_form（`pdf_form.py`，依赖 PyMuPDF）

| 函数 | 输入 | 输出 / 副作用 |
|---|---|---|
| `fill_pdf_form(template_pdf, output_pdf, field_updates)` | 模板路径、输出路径、`{字段名:值}`（checkbox 命中即勾 Yes，模板没有的字段名忽略） | 无（写出 output_pdf）；模板不存在抛 FileNotFoundError |

示例：`fill_pdf_form("POA.pdf", "out.pdf", {"applicant_name": "张三", "checkbox_a": True})`

### pdfa（`pdfa.py`，依赖系统 Ghostscript）

| 函数 | 输入 | 输出 / 副作用 |
|---|---|---|
| `gs_bin()` | — | Ghostscript 可执行路径 str｜None |
| `to_pdfa(src, out_dir, timeout=300)` | 源 PDF、输出目录 | 输出 PDF/A-2b 路径 str；无 gs 或失败抛异常 |
| `others_to_pdfa(others, out_dir)` | 路径列表、输出目录 | list[str]（PDF 转 PDF/A、非 PDF 原样） |

### doc_text（`doc_text.py`，惰性依赖 PyMuPDF / python-docx）

| 函数 | 输入 | 输出 |
|---|---|---|
| `pdf_text(pdf_path, max_pages=6)` | PDF 路径、页数 | str（文本层；**扫描件无文本层返回 ""**，需 OCR 另用 llm_client.vision） |
| `docx_text(path)` | docx 路径 | str（python-docx，失败退解压 XML；缺文件 ""） |
| `split_spec(spec_text)` | 说明书全文 str | (description, claims)；权要以 WHAT IS CLAIMED IS/CLAIMS/权利要求 起、到 ABSTRACT/摘要 止；切不出则 claims="" |
| `pick_latest_docx(dirpath, keywords=None)` | 目录、关键词列表 | 最新匹配 docx 路径 str｜None（本层优先，无则递归子目录） |

示例（实测，见 demo 输出）：
```python
spec = pick_latest_docx("申请文件", keywords=["spec"])   # -> ".../SPEC-20618-0424US00.docx"
desc, claims = split_spec(docx_text(spec))                # claims 以 "WHAT IS CLAIMED IS:" 起
```

## 来源与替代

| 本模块 | 抽自 | 迁移状态 |
|---|---|---|
| pdf_form.fill_pdf_form | `submission/common.py` `fill_pdf_form`（declaration 内另有重复私副本） | 未迁移 |
| pdfa.* | `run_uspto_upload.py` `_gs_bin/_to_pdfa/_others_to_pdfa` | 未迁移 |
| doc_text.pdf_text | `oa/parse_us_refs.py` `_pdf_to_text` | 未迁移 |
| doc_text.docx_text/split_spec/pick_latest_docx | `oa/oa_report_ai.py` 同名私有函数 | 未迁移 |
