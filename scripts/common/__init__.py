"""common —— 可复用纯函数工具集（零依赖、零业务耦合）。

各子模块抽自现有业务文件，逻辑不变，作为独立可复用资产供各项目直接引用。
目前为纯新增资产，未迁移原调用方（原文件仍保留各自的私有实现）。

用法：
    from common import parse_date, normalize_pub_no, get_by_path, strip_tags
    # 或按域引入
    from common import dates, patents, jsonpath, html_text
"""
from . import dates, patents, jsonpath, html_text
from .dates import parse_date, add_months, move_to_workday
from .patents import normalize_pub_no
from .jsonpath import get_by_path, set_by_path
from .html_text import strip_tags, split_cells

__all__ = [
    "dates", "patents", "jsonpath", "html_text",
    "parse_date", "add_months", "move_to_workday",
    "normalize_pub_no",
    "get_by_path", "set_by_path",
    "strip_tags", "split_cells",
]
