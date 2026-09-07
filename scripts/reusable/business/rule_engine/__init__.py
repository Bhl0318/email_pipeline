"""rule_engine —— 分级规则解析引擎（业务支撑层）。

规则外置成嵌套 JSON，按多维键逐层查表，最后一层"通配符 → 精确 → 有序兜底"命中。
load_rules 读表（带缓存），resolve 查表。
"""
from .engine import load_rules, resolve

__all__ = ["load_rules", "resolve"]
