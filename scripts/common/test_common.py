"""common 测试用例（离线，纯函数）。

运行：python3 scripts/common/test_common.py   或   pytest scripts/common/test_common.py
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import (  # noqa: E402
    parse_date, add_months, move_to_workday, normalize_pub_no,
    get_by_path, set_by_path, strip_tags, split_cells,
)


def test_parse_date():
    assert parse_date("2026-02-14") == datetime(2026, 2, 14)
    assert parse_date("02/14/2026") == datetime(2026, 2, 14)
    assert parse_date("February 12, 2026") == datetime(2026, 2, 12)
    assert parse_date("February 12 2026") == datetime(2026, 2, 12)
    assert parse_date("2026-02-14T10:00:00+08:00") == datetime(2026, 2, 14)
    assert parse_date("") is None
    assert parse_date(None) is None
    assert parse_date("不是日期") is None


def test_add_months():
    assert add_months(datetime(2026, 1, 31), 1) == datetime(2026, 2, 28)   # 落月末
    assert add_months(datetime(2024, 1, 31), 1) == datetime(2024, 2, 29)   # 闰年
    assert add_months(datetime(2025, 12, 15), 3) == datetime(2026, 3, 15)  # 跨年
    assert add_months(datetime(2026, 3, 15), -2) == datetime(2026, 1, 15)  # 负数


def test_move_to_workday():
    assert move_to_workday(datetime(2026, 2, 14)) == datetime(2026, 2, 13)  # 周六→周五
    assert move_to_workday(datetime(2026, 2, 15)) == datetime(2026, 2, 13)  # 周日→周五
    assert move_to_workday(datetime(2026, 2, 12)) == datetime(2026, 2, 12)  # 周四原样


def test_normalize_pub_no():
    assert normalize_pub_no("US 9,123,456 B2") == "US9123456B2"
    assert normalize_pub_no("US 2015/0123456 A1") == "US20150123456A1"
    assert normalize_pub_no("US-2015/0123456-A1") == "US20150123456A1"
    assert normalize_pub_no("CN 216192880 U") == "CN216192880U"
    assert normalize_pub_no("2015/0123456 A1") == "US20150123456A1"       # 无前缀补美
    assert normalize_pub_no("2015/0123456 A1", default_country="CN") == "CN20150123456A1"
    assert normalize_pub_no("") == ""
    assert normalize_pub_no(None) == ""


def test_get_by_path():
    d = {"inventors": [{"name": "张三"}, {"name": "李四"}]}
    assert get_by_path(d, "inventors.1.name") == "李四"
    assert get_by_path(d, "inventors.9.name") is None   # 越界
    assert get_by_path(d, "nope") is None               # 缺键
    assert get_by_path(d, "inventors.0.age") is None    # 类型不符


def test_set_by_path():
    d = {"inventors": [{"name": "张三"}]}
    set_by_path(d, "inventors.0.name", "王五")
    assert d["inventors"][0]["name"] == "王五"


def test_strip_tags():
    assert strip_tags("<td>  张三&nbsp;</td>") == "张三"
    assert strip_tags("<p>a<b>b</b></p>") == "ab"
    assert strip_tags(None) == ""


def test_split_cells():
    assert split_cells("<tr><td>a</td><td>b</td></tr>") == ["<td>a</td>", "<td>b</td>"]
    assert split_cells("<tr></tr>") == []


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("ok", fn.__name__)
    print(f"all passed ({len(fns)})")
