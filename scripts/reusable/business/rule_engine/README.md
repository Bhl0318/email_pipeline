# rule_engine —— 分级规则解析引擎（接口说明）

**做什么用**：把规则外置成嵌套 JSON，按多维键逐层查表，最后一层按"**通配符 → 精确键 → 有序兜底**"命中。用于任何"按几个维度查规则、层层兜底出结论"的场景（如 OA 分派：按 国别×官文类型×客户码 决定立项/转发/跳过）。是模块级组件：引擎只管通用的查表+兜底，具体维度键怎么算由调用方决定。

范式抽象自 `report/read_email.py` 的 OA 分派规则（`_load_oa_rules`/`_resolve_oa_action`）+ `report/oa_report_rules.json`。

可运行示例：`python3 scripts/reusable/examples/rule_engine_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/business")
from rule_engine import load_rules, resolve
```

## 接口

### `load_rules(json_path, cache=True)`
**作用**：加载规则表 JSON。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `json_path` | **必填** | 规则表 JSON 路径 |
| `cache` | 可选 | 默认 True，同一路径只读一次（改文件后需重启或传 False） |

**返回**：dict（读失败→`{}`）。

### `resolve(rules, path, fallbacks=(), wildcard="*")`
**作用**：在嵌套规则表里按 path 逐层下钻，最后一层按"通配符 → 精确键 → 有序兜底"命中。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `rules` | **必填** | 嵌套 dict（load_rules 的结果） |
| `path` | **必填** | 逐层键序列，如 `["CN", "审查意见通知书@1", "20849"]` |
| `fallbacks` | 可选 | 最后一层未精确命中时依次尝试的兜底键，如 `["5开头", "其他"]` |
| `wildcard` | 可选 | 最后一层若含此键表示"全部同规则"，优先返回；默认 `"*"` |

**返回**：命中的叶子值；任一中间层缺失或最后层全不命中→None。
"某兜底键只在特定条件下才试"（如客户码 5 开头）这类判断，由调用方拼 `fallbacks` 时决定。

## 使用示例

```python
from rule_engine import resolve

RULES = {"CN": {
    "审查意见通知书@1": {"20849": {"action": "assign"}, "5开头": {"action": "skip"}, "其他": {"action": "assign"}},
    "补正通知书": {"*": {"action": "ignore"}},   # 所有客户同规则
}}

def resolve_oa(region, rule_type, project):
    code = (project or "")[:5]                             # 客户码=案号前5位（业务）
    fallbacks = (["5开头"] if code.startswith("5") else []) + ["其他"]
    return resolve(RULES, [region, rule_type, code], fallbacks=fallbacks)

resolve_oa("CN", "审查意见通知书@1", "20849-0032CN01")   # -> {'action': 'assign'}  精确
resolve_oa("CN", "审查意见通知书@1", "50021-0001CN00")   # -> {'action': 'skip'}    5开头
resolve_oa("CN", "审查意见通知书@1", "30011-0002CN00")   # -> {'action': 'assign'}  其他兜底
resolve_oa("CN", "补正通知书", "任意")                    # -> {'action': 'ignore'}  通配符
resolve_oa("CN", "不存在类型", "20849")                  # -> None
```

## 来源

范式来源：`report/read_email.py`（`_load_oa_rules`/`_resolve_oa_action`）、`report/oa_report_rules.json`。
