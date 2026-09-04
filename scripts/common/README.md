# common —— 可复用纯函数工具集（接口说明）

零依赖（仅标准库）、零业务耦合。从现有业务文件抽出，逻辑不变。目前为纯新增，未迁移原调用方。
可运行示例：`python3 scripts/examples/common_utils_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts")
from common import parse_date, add_months, move_to_workday, normalize_pub_no, \
    get_by_path, set_by_path, strip_tags, split_cells
```

## 逐函数：调用方法 / 输入 / 返回

### dates（`common/dates.py`）

| 函数 | 调用方法 | 输入 | 返回 |
|---|---|---|---|
| `parse_date` | `parse_date("2026-02-14")` | date_str: str｜None（支持 ISO / `02/14/2026` / `February 12, 2026`） | datetime；空或无法解析→None |
| `add_months` | `add_months(datetime(2026,1,31), 1)` | dt: datetime；months: int（可负） | datetime（落月末按当月最大天数，闰年 2 月 29） |
| `move_to_workday` | `move_to_workday(datetime(2026,2,14))` | dt: datetime | datetime（周末前移到周五，工作日原样） |

### patents（`common/patents.py`）

| 函数 | 调用方法 | 输入 | 返回 |
|---|---|---|---|
| `normalize_pub_no` | `normalize_pub_no("US 9,123,456 B2")` | raw: str｜None；default_country: str="US" | str，如 `"US9123456B2"`；无前缀补国别；空→`""` |

### jsonpath（`common/jsonpath.py`）

| 函数 | 调用方法 | 输入 | 返回 |
|---|---|---|---|
| `get_by_path` | `get_by_path(d, "inventors.0.name")` | obj: dict/list 嵌套；path: str（`.` 分段，纯数字段=下标） | 取到的值；任一段缺失/越界/类型不符→None |
| `set_by_path` | `set_by_path(d, "inventors.0.name", "李四")` | obj: dict/list；path: str；val: 任意 | 无（就地改 obj）；中间段缺失抛 KeyError/IndexError |

### html_text（`common/html_text.py`）

| 函数 | 调用方法 | 输入 | 返回 |
|---|---|---|---|
| `strip_tags` | `strip_tags("<td> 张三&nbsp;</td>")` | s: str｜None | str（去标签/&nbsp;/\xa0 并 strip），如 `"张三"`；None→`""` |
| `split_cells` | `split_cells("<tr><td>a</td><td>b</td></tr>")` | row_html: str（一行 HTML） | list[str]，每项一个完整 `<td…>…</td>` |

## 使用示例

```python
from datetime import datetime
from common import parse_date, add_months, move_to_workday, \
    normalize_pub_no, get_by_path, set_by_path, strip_tags, split_cells

parse_date("2026-02-14")                 # -> datetime.datetime(2026, 2, 14, 0, 0)
parse_date("February 12, 2026")          # -> datetime.datetime(2026, 2, 12, 0, 0)
add_months(datetime(2026, 1, 31), 1)     # -> datetime.datetime(2026, 2, 28, 0, 0)  月末
move_to_workday(datetime(2026, 2, 14))   # -> datetime.datetime(2026, 2, 13, 0, 0)  周六→周五

normalize_pub_no("US 9,123,456 B2")      # -> 'US9123456B2'
normalize_pub_no("2015/0123456 A1")      # -> 'US20150123456A1'  无前缀默认美国

d = {"inventors": [{"name": "张三"}, {"name": "李四"}]}
get_by_path(d, "inventors.1.name")       # -> '李四'
get_by_path(d, "inventors.9.name")       # -> None  越界
set_by_path(d, "inventors.0.name", "王五")  # d["inventors"][0]["name"] 变 '王五'

strip_tags("<td>  张三&nbsp;</td>")       # -> '张三'
split_cells("<tr><td>a</td><td>b</td></tr>")  # -> ['<td>a</td>', '<td>b</td>']
```

## 来源

| 本模块 | 抽自 |
|---|---|
| dates.* | `oa/filter_oa_email.py` `_parse_date/_add_months/_move_to_workday` |
| patents.normalize_pub_no | `oa/parse_us_refs.py` `normalize_pub_no` |
| jsonpath.* | `report/submission/qa_seed.py` `get_by_path/set_by_path` |
| html_text.* | `oa/oainfo_cli.py` `_strip_tags/_split_cells` |
