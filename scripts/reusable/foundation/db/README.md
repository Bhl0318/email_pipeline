# db —— 数据库查询客户端（接口说明）

**做什么用**：两个数据库的查询客户端——查 atw（TIP，MySQL）和唯德 IPEasy（SQL Server）。统一从 `db_config.json` 读连接信息、参数化查询、返回 `list[dict]`。跨库把结果合并成一条见 `business/db_merge`。

从现有业务文件抽出，逻辑不变。改动：MySQL 连接不再硬编码（原 `db_query.py` 写死），统一走配置；MSSQL 消掉了三处重复的 connect 样板。

可运行示例：`python3 scripts/reusable/examples/db_demo.py`。

## 如何 import + 配置

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/foundation")
from db import mysql_query, mssql_query
```

连接信息读 `scripts/report/db_config.json`（键 `mysql_atw` / `mssql_ipeasy`，各含 host/port/user/password/database/charset）；可用环境变量 `DB_CONFIG_PATH` 覆盖路径，或给 `config=` 参数直接传连接 dict。

## 接口

### `mysql_query(sql, params=None, config=None)`
**作用**：对 atw(MySQL) 执行 SQL。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `sql` | **必填** | SQL；**建议 `%s` 占位 + params 参数化**，避免注入 |
| `params` | 可选 | 参数元组/列表 |
| `config` | 可选 | 连接 dict；不给则读 `db_config.mysql_atw` |

**返回**：SELECT/SHOW/DESC → `list[dict]`；增删改 → 影响行数 int。

### `mssql_query(sql, params=None, config=None)`
**作用**：对唯德 IPEasy(SQL Server) 执行 SQL。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `sql` | **必填** | SQL，`%s` 占位 + params |
| `params` | 可选 | 参数元组/列表 |
| `config` | 可选 | 连接 dict；不给则读 `db_config.mssql_ipeasy` |

**返回**：SELECT → `list[dict]`；增删改 → 影响行数 int；**未配置（host 空/占位）→ `[]`**（不阻塞，与原行为一致）；连接/查询出错会抛异常，交上层（如 db_merge）兜底。

## 使用示例

```python
from db import mysql_query, mssql_query

mysql_query("SELECT customer_name FROM customer WHERE customer_code=%s", ("20618",))
# -> [{'customer_name': '众慧'}]

mssql_query("SELECT app_no, app_date FROM p_case_info WHERE case_volume=%s", ("20618-0424US00",))
# -> [{'app_no': '17456882', 'app_date': datetime(...)}]  未配置IPEasy→[]
```

## 来源与改动

- 抽自：`report/db_query.py`（MySQL execute/execute_params）、`report/enrich_report.py`（MSSQL 的 pymssql 连接样板）。
- 改动：MySQL 连接由硬编码改为读 `db_config.json`；MSSQL 三处重复 connect 归一为一个函数、返回改为按列名 `list[dict]`。逻辑不变。
