# common —— 可复用纯函数工具集（接口说明）

零依赖（仅标准库）、零业务耦合。从现有业务文件抽出，逻辑不变，作为独立资产供直接引用。
目前为纯新增，未迁移原调用方（原文件仍保留各自私有实现）。

可运行示例：`python3 scripts/examples/common_utils_demo.py`（打印每个函数的输入→输出）。

## 如何调

```python
import os, sys
sys.path.insert(0, "<...>/scripts")      # 让 common 包可被 import
from common import parse_date, normalize_pub_no, get_by_path, strip_tags
# 或按域：from common import dates, patents, jsonpath, html_text
```

## 接口

### dates（`common/dates.py`）

| 函数 | 输入 | 输出 | 示例 |
|---|---|---|---|
| `parse_date(date_str)` | str｜None | datetime｜None | `parse_date("2026-02-14")` → `datetime(2026,2,14)`；支持 `02/14/2026`、`February 12, 2026`；空/无法解析→None |
| `add_months(dt, months)` | datetime, int（可负） | datetime | `add_months(datetime(2026,1,31),1)` → `2026-02-28`（落月末按当月最大天数，闰年2月29） |
| `move_to_workday(dt)` | datetime | datetime | `move_to_workday(2026-02-14 周六)` → `2026-02-13 周五`（周末前移，工作日原样） |

### patents（`common/patents.py`）

| 函数 | 输入 | 输出 | 示例 |
|---|---|---|---|
| `normalize_pub_no(raw, default_country="US")` | str｜None, str | str | `"US 9,123,456 B2"`→`"US9123456B2"`；`"US-2015/0123456-A1"`→`"US20150123456A1"`；`"2015/0123456 A1"`→`"US20150123456A1"`（无前缀补默认国别）；空→`""` |

### jsonpath（`common/jsonpath.py`）

| 函数 | 输入 | 输出 | 示例 |
|---|---|---|---|
| `get_by_path(obj, path)` | dict/list 嵌套, str（`"a.0.b"`） | 值｜None | `get_by_path({"inv":[{"name":"张三"}]}, "inv.0.name")` → `"张三"`；缺失/越界→None |
| `set_by_path(obj, path, val)` | dict/list, str, 任意 | 无（就地改） | `set_by_path(d, "inv.0.name", "李四")`；中间段须已存在，否则抛 KeyError/IndexError |

### html_text（`common/html_text.py`）

| 函数 | 输入 | 输出 | 示例 |
|---|---|---|---|
| `strip_tags(s)` | str｜None | str | `strip_tags("<td> 张三&nbsp;</td>")` → `"张三"`（去标签/&nbsp;/\xa0 并 strip；None→""） |
| `split_cells(row_html)` | str（一行 HTML） | list[str] | `split_cells("<tr><td>a</td><td>b</td></tr>")` → `["<td>a</td>","<td>b</td>"]`（td 不嵌套 td） |

## 来源与替代

| 本模块函数 | 抽自 | 迁移状态 |
|---|---|---|
| dates.* | `oa/filter_oa_email.py` `_parse_date/_add_months/_move_to_workday` | 未迁移（原文件保留私有实现） |
| patents.normalize_pub_no | `oa/parse_us_refs.py` `normalize_pub_no` + `_COUNTRIES` | 未迁移 |
| jsonpath.* | `report/submission/qa_seed.py` `get_by_path/set_by_path` | 未迁移 |
| html_text.* | `oa/oainfo_cli.py` `_strip_tags/_split_cells` | 未迁移 |

> 说明：oainfo_cli 里 `_splice_oa_row/_find_oa_row` 等**绑 OA/Confluence 表格结构**的函数不属于本通用集，仍留在 oainfo_cli。
