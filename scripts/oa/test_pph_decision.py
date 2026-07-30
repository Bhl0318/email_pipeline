#!/usr/bin/env python3
"""PPH 决定判定：parse_pph_decision 用真实样本 PDF 回归（文字层命中,不连网络）。
  cd scripts/oa && python3 test_pph_decision.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from parse_us_pdf import parse_pph_decision

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


SAMPLE = os.path.join(SCRIPT_DIR, "2026-07-09-PPH decision dismissed-68401-H017US00.PDF")


def test_dismissed_sample():
    if not os.path.exists(SAMPLE):
        print("  skip - 样本 PDF 不在")
        return
    ok(parse_pph_decision(SAMPLE) == "dismissed", "样本 PPH 判为 dismissed")


def test_missing_file():
    ok(parse_pph_decision("") == "", "空路径→空")
    ok(parse_pph_decision("/no/such.pdf") == "", "文件不存在→空")


if __name__ == "__main__":
    for fn in [test_dismissed_sample, test_missing_file]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
