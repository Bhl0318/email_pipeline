# doc_generator —— 文档生成器骨架（接口说明）

**做什么用**：按数据生成表单文件（PDF/docx）的通用骨架，把流程拆成分离的三步——**字段映射**（原始数据→生成器要的结构）、**模板选择**（按条件挑模板）、**生成器编排**（跑一组生成器、各自返回统一结果、逐个兜底、汇总）。是模块级组件：骨架只管这三步机制，每个生成器具体怎么填模板是业务（填 PDF 表单用 `doc_utils.fill_pdf_form`，填 docx 用 python-docx）。

范式抽象自 `report/submission/`（fields_mapping ↔ 各 *_generator 分离、filing_preparation 编排）。

可运行示例：`python3 scripts/reusable/examples/doc_generator_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/business")
from doc_generator import map_fields, select_template, build_documents
```

## 生成器契约

每个生成器是 `callable(data, **kwargs) -> dict`，至少返回
`{"file_path": 路径, "file_name": 文件名, "type": 类型}`，可含 `"warnings": [str]`。

## 接口

### `map_fields(raw, spec)`
**作用**：按映射规格把原始数据转成生成器要的结构（字段映射层）。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `raw` | **必填** | 原始数据 dict |
| `spec` | **必填** | dict `{目标键: 来源}`；来源为源键名 str（取 `raw[源键]`）或 callable(raw)→值 |

**返回**：映射后的 dict。

### `select_template(templates, key, default=None)`
**作用**：按 key 从候选里挑模板（模板选择层）。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `templates` | **必填** | dict `{条件键: 模板路径}` |
| `key` | **必填** | 条件键（大小写/别名归一由调用方算 key 时处理） |
| `default` | 可选 | 未命中时返回，默认 None |

**返回**：命中的模板路径；未命中→default。

### `build_documents(data, jobs)`
**作用**：跑一组生成器，逐个兜底，汇总结果（生成器编排层）。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `data` | **必填** | 各生成器共享的输入（通常是映射后的结构） |
| `jobs` | **必填** | 列表，每项 `(生成器callable, kwargs字典)` |

**返回**：`{"documents": [成功结果...], "warnings": [str...]}`；某生成器抛异常不中断，记一条 warning 继续，各结果自带的 warnings 也汇总进来。

## 使用示例

```python
from doc_generator import map_fields, select_template, build_documents

# ① 映射：原始 fields_json → 生成器要的结构
case_info = map_fields(
    {"case_volume": "64504-H006US00", "sm": "utl", "inv_first": "Wei", "inv_last": "LIN"},
    {"case_no": "case_volume", "subject": "sm",
     "inventor": lambda r: f'{r["inv_first"]} {r["inv_last"]}'})
# -> {'case_no': '64504-H006US00', 'subject': 'utl', 'inventor': 'Wei LIN'}

# ② 选模板
TEMPLATES = {"utl": "Transmittal.pdf", "design": "Design-Transmittal.pdf", "371": "371-Transmittal.pdf"}
select_template(TEMPLATES, case_info["subject"], default="Transmittal.pdf")  # -> 'Transmittal.pdf'

# ③ 编排：跑生成器（业务生成器内部用 doc_utils.fill_pdf_form 等填模板），逐个兜底
result = build_documents(case_info, [(gen_poa, {"output_dir": d}), (gen_transmittal, {"output_dir": d})])
# result == {"documents": [{...POA...}, {...Transmittal...}], "warnings": [...]}
```

## 依赖与来源

- 配合：`doc_utils.fill_pdf_form`（生成器填 PDF 表单）、python-docx（填 docx）。
- 范式来源：`report/submission/`（`fields_mapping.py`、各 `*_generator.py`、`filing_preparation.py`）。
