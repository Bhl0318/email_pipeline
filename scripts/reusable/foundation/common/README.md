# common —— 通用纯函数工具（接口说明）

**做什么用**：与业务无关的通用小工具——解析和计算日期、把专利号归一化、按路径存取嵌套数据、处理 HTML 文本。零依赖（仅标准库）、零业务耦合。从现有业务文件抽出，逻辑不变；纯新增，未迁移原调用方。

可运行示例：`python3 scripts/reusable/examples/common_utils_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/foundation")
from common import parse_date, add_months, move_to_workday, normalize_pub_no, \
    get_by_path, set_by_path, strip_tags, split_cells
```

## 逐函数：作用 / 输入 / 返回

### dates（`common/dates.py`）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `parse_date(date_str)` | 把各种写法的日期字符串解析成 datetime | date_str: str｜None（支持 `2026-02-14`、`02/14/2026`、`February 12, 2026`） | datetime；空或无法解析→None |
| `add_months(dt, months)` | 在某日期上加/减若干月 | dt: datetime；months: int（可负） | datetime（落月末按当月最大天数，闰年 2 月取 29） |
| `move_to_workday(dt)` | 日期若在周末就前移到最近的周五 | dt: datetime | datetime（工作日原样返回） |

### patents（`common/patents.py`）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `normalize_pub_no(raw, default_country="US")` | 把各种写法的专利号统一成 Google Patents 格式（去逗号/空格/斜杠等） | raw: str｜None；default_country: str（**可选**，无国别前缀时补它，默认 US） | str，如 `"US9123456B2"`；空输入→`""` |

### jsonpath（`common/jsonpath.py`）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `get_by_path(obj, path)` | 按 `"a.0.b"` 点号路径从嵌套 dict/list 取值 | obj: dict/list 嵌套；path: str（纯数字段=列表下标） | 取到的值；任一段缺失/越界/类型不符→None |
| `set_by_path(obj, path, val)` | 按 `"a.0.b"` 点号路径给嵌套结构写值 | obj: dict/list；path: str；val: 任意 | 无（就地改 obj）；中间段不存在会抛 KeyError/IndexError |

### html_text（`common/html_text.py`）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `strip_tags(s)` | 去掉 HTML 标签、`&nbsp;` 等得到纯文本 | s: str｜None | str（strip 后），如 `"张三"`；None→`""` |
| `split_cells(row_html)` | 把一行 HTML 拆成各个 `<td>` 单元格 | row_html: str（一行 HTML） | list[str]，每项一个完整 `<td…>…</td>` |

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
