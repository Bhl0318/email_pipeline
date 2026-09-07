# doc_extract —— 分级文档抽取组件（接口说明）

**做什么用**：从 PDF 抽结构化数据，按"**正则 → 大模型读文本 → 扫描件图片OCR**"三级自动兜底。你只需按自己的文档给出正则和提示词，取文本、调模型、扫描件转图片这些内部编排都由它做。是"模块级"资产：一个组件完成一整块"文档→结构化"的能力，内部复用了基础通用层的 `doc_utils`（取文本）和应用集成层的 `llm_client`（调模型）。

范式抽象自 `oa/parse_us_pdf.py`、`oa/parse_cn_pdf.py`（原本每种官文各写一套三级兜底）。

可运行示例：`python3 scripts/reusable/examples/doc_extract_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/business")
from doc_extract import extract_from_pdf
```

## 接口

### `extract_from_pdf(pdf_path, *, regex=None, text_prompt=None, image_prompt=None, max_pages=6, text_profile="deepseek", image_profile="qwen", extract="json")`

**作用**：三级兜底把一个 PDF 抽成结构化数据。有文本层时先试正则、不中再让大模型读文本；无文本层（扫描件）时把页面转成图片交多模态模型。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `pdf_path` | **必填** | PDF 路径 |
| `regex` | 可选 | callable(text)→结果｜None，一级；命中即返回 |
| `text_prompt` | 可选 | str，二级；正则未命中时把它+正文发给大模型 |
| `image_prompt` | 可选 | str，三级；扫描件无文本层时发图片给多模态模型 |
| `max_pages` | 可选 | 取文本/渲染的最大页数，默认 6 |
| `text_profile` / `image_profile` | 可选 | 大模型 profile，默认 `deepseek` / `qwen` |
| `extract` | 可选 | `"json"`（默认，自动解析）｜`"text"` |

**返回**：结构化结果（dict/list 或 str）；三级都没抽到→None。只给哪一级的参数就走哪一级。

## 使用示例

```python
import re
from doc_extract import extract_from_pdf

# 按自己的文档写一个正则抽取器
def us_months_regex(text):
    m = re.search(r"(\d+)\s+MONTHS?", text, re.IGNORECASE)
    return {"months": int(m.group(1))} if m else None

# 一级正则（离线，见 demo 实测）
extract_from_pdf("oa.pdf", regex=us_months_regex)
# -> {'months': 3}

# 三级完整：正则未中→大模型读文本→扫描件图片OCR
extract_from_pdf(
    "oa.pdf",
    regex=us_months_regex,
    text_prompt='从下面官文提取答复期限月数，只输出 JSON：{"months": <int>}',
    image_prompt='这些官文页答复期限几个月？只输出 JSON：{"months": <int>}',
)
# -> {"months": 3}
```

## 依赖与来源

- 依赖：`doc_utils.pdf_text`（基础通用层）、`llm_client.chat/vision`（应用集成层）、PyMuPDF（扫描件渲染）。
- 范式来源：`oa/parse_us_pdf.py`、`oa/parse_cn_pdf.py`、`oa/parse_us_refs.py` 的三级兜底逻辑。
