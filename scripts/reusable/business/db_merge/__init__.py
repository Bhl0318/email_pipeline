"""db_merge —— 跨库按键合并（业务支撑层）。

同一个键分别查多个数据源，在应用层合并成一个 dict；不跨库 JOIN、逐源兜底。
"""
from .merge import merge_by_key

__all__ = ["merge_by_key"]
