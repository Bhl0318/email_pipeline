"""分级规则解析引擎（业务支撑层）。

范式抽象自 report/read_email.py 的 OA 分派规则（`_load_oa_rules`/`_resolve_oa_action`）：
规则外置成嵌套 JSON，按多维键逐层下钻，最后一层支持"通配符 + 有序兜底"命中。

引擎只做通用的"查表+兜底"；具体维度键怎么算（如客户码=案号前5位、第几次OA、条件兜底）
属业务逻辑，由调用方在传入 path/fallbacks 时决定。
"""
import json
import os
import sys

_CACHE = {}


def load_rules(json_path, cache=True):
    """加载规则表 JSON，返回 dict。cache=True 时同一路径只读一次（改文件需重启或 cache=False）。

    输入：json_path: str；cache: bool（可选，默认 True）
    输出：dict（读失败→{}）
    """
    if cache and json_path in _CACHE:
        return _CACHE[json_path]
    try:
        with open(json_path, encoding="utf-8") as f:
            rules = json.load(f)
    except Exception as e:
        print(f"[rule_engine] 加载规则表失败 {json_path}: {e}", file=sys.stderr)
        rules = {}
    if cache:
        _CACHE[json_path] = rules
    return rules


def resolve(rules, path, fallbacks=(), wildcard="*"):
    """在嵌套规则表里按 path 逐层下钻，最后一层按"通配符 → 精确键 → 有序兜底"命中。

    输入：
      rules      嵌套 dict（load_rules 的结果）
      path       逐层键序列，如 ["CN", "审查意见通知书@1", "20849"]
      fallbacks  可选，最后一层未精确命中时依次尝试的兜底键，如 ["5开头", "其他"]
      wildcard   可选，最后一层若含此键表示"全部同规则"，优先返回；默认 "*"
    输出：命中的叶子值；任一中间层缺失或最后层全不命中 → None。

    注："某兜底键只在特定条件下才试"（如 5 开头）这类业务判断，由调用方在拼 fallbacks 时决定。
    """
    if not path:
        return None
    node = rules
    for key in path[:-1]:                       # 中间层：逐层精确下钻
        if not isinstance(node, dict):
            return None
        node = node.get(key)
        if node is None:
            return None
    if not isinstance(node, dict):
        return None
    last = path[-1]
    if wildcard in node:                        # 通配符：全部同规则
        return node[wildcard]
    if node.get(last) is not None:              # 精确键
        return node[last]
    for fb in fallbacks:                        # 有序兜底
        if node.get(fb) is not None:
            return node[fb]
    return None
