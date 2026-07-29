#!/usr/bin/env python3
"""已结案案件不立项：_drop_closed_cases 过滤逻辑。纯逻辑,注入假 is_closed,不连 DB。
  cd scripts/oa && python3 test_drop_closed.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from read_email import _drop_closed_cases

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def test_drop_closed_kept_open():
    results = [
        {"project": "20618-0001CN00"},   # 未结案 → 留
        {"project": "20615-0002CN00"},   # 已结案 → 去
        {"project": ""},                 # 无案号 → 留(不查)
    ]
    closed = {"20615-0002CN00"}
    kept = _drop_closed_cases(results, lambda p: p in closed)
    projs = [r["project"] for r in kept]
    ok("20618-0001CN00" in projs, "未结案保留")
    ok("20615-0002CN00" not in projs, "已结案剔除")
    ok("" in projs, "无案号条目保留(不查结案)")


def test_cache_query_once_per_project():
    calls = []

    def is_closed(p):
        calls.append(p)
        return False

    results = [{"project": "A"}, {"project": "A"}, {"project": "B"}, {"project": "A"}]
    _drop_closed_cases(results, is_closed)
    ok(calls == ["A", "B"], f"同案号只查一次 (calls={calls})")


if __name__ == "__main__":
    for fn in [test_drop_closed_kept_open, test_cache_query_once_per_project]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
