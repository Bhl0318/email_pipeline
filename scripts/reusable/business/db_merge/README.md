# db_merge —— 跨库按键合并（接口说明）

**做什么用**：同一个键（如案号）分别查多个数据源（atw MySQL + 唯德 IPEasy MSSQL），在应用层把结果合并成一个 dict——不跨库 JOIN、某个源查不到/连不上就跳过不阻塞。是模块级组件：引擎只管"按键调多源、合并、逐源兜底"，每个源查什么、字段叫什么由调用方写在 fetcher 里。

范式抽象自 `report/enrich_report.py` 的 `enrich_cn_fields`。

可运行示例：`python3 scripts/reusable/examples/db_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/business")
from db_merge import merge_by_key
```

## 接口

### `merge_by_key(key, fetchers, skip_empty=True)`
**作用**：按同一 key 调多个数据源取 dict 并合并成一个；某源出错记 stderr 跳过、不阻塞。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `key` | **必填** | 关联键（如案号 project），传给每个 fetcher |
| `fetchers` | **必填** | 列表，每项 `callable(key)->dict`（一个数据源的查询+字段命名） |
| `skip_empty` | 可选 | 默认 True：跳过值为 None/空串的字段（保留调用方原占位） |

**返回**：合并后的 dict（后面的源同名键覆盖前面的）。

## 使用示例

```python
from db import mysql_query, mssql_query          # foundation/db
from db_merge import merge_by_key

def from_atw(project):                            # 源1：atw(MySQL)
    rows = mysql_query("SELECT customer_name FROM customer WHERE customer_code=%s", (project[:5],))
    return {"客户名称": rows[0]["customer_name"] if rows else ""}

def from_ipeasy(project):                         # 源2：唯德 IPEasy(MSSQL)
    rows = mssql_query("SELECT app_no, app_date FROM p_case_info WHERE case_volume=%s", (project,))
    r = rows[0] if rows else {}
    return {"申请号": r.get("app_no"), "申请日": str(r.get("app_date"))[:10] if r.get("app_date") else ""}

merge_by_key("20618-0424US00", [from_atw, from_ipeasy])
# -> {'客户名称': '众慧', '申请号': '17456882'}   空字段跳过、某源断开也不阻塞
```

## 来源

范式来源：`report/enrich_report.py`（`enrich_cn_fields`：查 atw + IPEasy 按 project 合并）。
