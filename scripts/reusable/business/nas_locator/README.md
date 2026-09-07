# nas_locator —— NAS 申请文件定位（接口说明）

**做什么用**：按案号 + 地区在 NAS（Z 盘）目录树里定位案件的「递交文件」目录、取其中的说明书 docx。是模块级组件：NAS 路径规则作 config 传入、"客户码→客户简称"这类查库动作注入为 `shortname_lookup`（调用方用 `db.mysql_query` 实现），所以组件本身不依赖数据库；选文件复用 `doc_utils.pick_latest_docx`。

范式抽自 `oa/oa_report_ai.py` 的 `_resolve_app_dir` / `find_application_files`。

可运行示例：`python3 scripts/reusable/examples/nas_locator_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/business")
from nas_locator import find_application_file, resolve_app_dir
```

## NAS 路径规则（config，默认 `DEFAULT_NAS_CONFIG`）

| 键 | 含义 |
|---|---|
| `nas_base` | 普通案号根：`{码}-{简称}\{组内号}\{案号}\*递交文件*\` |
| `zhuohui_dir` | 含 `-H` 案号的根：`\{名字含码的目录}\{案号}\*递交文件*\` |
| `toplevel_customers` | 列在根目录的客户码集合，其余在 `其他客户\` 下 |
| `keywords` | 各地区在「递交文件」里挑说明书的文件名关键词（US=["spec"]/CN=["说明书","申请文件"]/EP=None 取最新） |

换环境（如挂载点不是 Z 盘）时传自己的 config 覆盖。

## 接口

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `resolve_app_dir(project, region, config=None, shortname_lookup=None)` | 定位案号对应的「递交文件」目录 | project 案号（≥10位）；region US/CN/EP；config（可选）；shortname_lookup（可选，callable(code)->简称，普通案号必需） | 目录路径 str 或 None |
| `find_application_file(project, region="", config=None, shortname_lookup=None)` | 定位说明书 docx（先定位目录，再按地区关键词取最新） | 同上 | docx 路径 str 或 None |

## 使用示例

```python
from nas_locator import find_application_file
from db import mysql_query          # foundation/db

def shortname(code):                # 客户码→客户简称（查 atw）
    rows = mysql_query("SELECT customer_shortname FROM customer WHERE customer_code=%s", (code,))
    return rows[0]["customer_shortname"] if rows else ""

spec = find_application_file("20849-0032US01", "US", shortname_lookup=shortname)  # 默认 Z 盘规则
# -> '.../递交文件/xxx-spec.docx' 或 None
```

## 来源与改动

- 抽自：`oa/oa_report_ai.py`（`_resolve_app_dir`/`find_application_files`）。
- 改动：NAS 路径规则由硬编码常量改为 config 传入；客户简称查库改为注入 `shortname_lookup`（原来内部 `_customer_shortname` 直接查 db）。逻辑不变。
