"""common 纯函数工具集用法示例：每个函数打印「输入 → 输出」。

运行：python3 scripts/examples/common_utils_demo.py
"""
import os
import sys
from datetime import datetime

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "foundation"))
from common import (  # noqa: E402
    parse_date, add_months, move_to_workday,
    normalize_pub_no, get_by_path, set_by_path,
    strip_tags, split_cells,
)


def show(expr, value):
    print(f"{expr:<52} -> {value!r}")


if __name__ == "__main__":
    print("== dates ==")
    show('parse_date("2026-02-14")', parse_date("2026-02-14"))
    show('parse_date("02/14/2026")', parse_date("02/14/2026"))
    show('parse_date("February 12, 2026")', parse_date("February 12, 2026"))
    show('parse_date("")', parse_date(""))
    show('add_months(datetime(2026,1,31), 1)', add_months(datetime(2026, 1, 31), 1))
    show('add_months(datetime(2025,12,15), 3)', add_months(datetime(2025, 12, 15), 3))
    show('move_to_workday(datetime(2026,2,14))', move_to_workday(datetime(2026, 2, 14)))  # 周六

    print("\n== patents ==")
    show('normalize_pub_no("US 9,123,456 B2")', normalize_pub_no("US 9,123,456 B2"))
    show('normalize_pub_no("US-2015/0123456-A1")', normalize_pub_no("US-2015/0123456-A1"))
    show('normalize_pub_no("CN 216192880 U")', normalize_pub_no("CN 216192880 U"))
    show('normalize_pub_no("2015/0123456 A1")', normalize_pub_no("2015/0123456 A1"))

    print("\n== jsonpath ==")
    d = {"inventors": [{"name": "张三"}, {"name": "李四"}]}
    show('get_by_path(d, "inventors.1.name")', get_by_path(d, "inventors.1.name"))
    show('get_by_path(d, "inventors.9.name")', get_by_path(d, "inventors.9.name"))
    set_by_path(d, "inventors.0.name", "王五")
    show('set_by_path(d,"inventors.0.name","王五"); d', d)

    print("\n== html_text ==")
    show('strip_tags("<td>  张三&nbsp;</td>")', strip_tags("<td>  张三&nbsp;</td>"))
    show('split_cells("<tr><td>a</td><td>b</td></tr>")',
         split_cells("<tr><td>a</td><td>b</td></tr>"))
