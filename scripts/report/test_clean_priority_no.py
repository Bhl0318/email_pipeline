#!/usr/bin/env python3
"""clean_priority_no 保留 CN 末位校验位 X 的回归测试（案例 64009-H017US00：CN 202511948961.X）。

  cd scripts/report && python3 test_clean_priority_no.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from submission.common import clean_priority_no

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def test():
    ok(clean_priority_no("CN 202511948961.X") == "202511948961.X", "CN 带校验位 X：去国别码保留 .X")
    ok(clean_priority_no("CN202511948961.X") == "202511948961.X", "无空格同样保留 X")
    ok(clean_priority_no("CN 202411284993") == "202411284993", "无 X 的号不变")
    ok(clean_priority_no("US 63/123,456") == "63123456", "去掉 /、,（US 式不受影响）")


if __name__ == "__main__":
    test()
    print(f"\nAll {_passed} checks passed.")
