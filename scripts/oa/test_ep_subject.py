#!/usr/bin/env python3
"""EP 主题正则 EP_SUBJECT_RE 的复现/回归测试（纯正则，不连网络）。

复现线上 bug：Intention to grant 邮件案号(project)提取为空。
  cd scripts/oa && python3 test_ep_subject.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from filter_oa_email import EP_SUBJECT_RE

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def test_intention_to_grant_space_before_semicolon():
    # 线上这封：Your Ref 与 ; 间有空格，且 Our Ref 在结尾无分隔符
    subj = ('【Intention to grant - R.71(3) EPC】EP Application (EP25200159.9) - '
            'Your Ref.:20608-0112EP01 ; Our Ref: MQVT282EP25D1')
    m = EP_SUBJECT_RE.search(subj)
    ok(m is not None, "能匹配（旧正则此处返回 None）")
    ok(m.group(2) == "EP25200159.9", f"EP号 (got {m.group(2)})")
    ok(m.group(3) == "20608-0112EP01", f"案号 project (got {m.group(3)})")
    ok(m.group(4) == "MQVT282EP25D1", f"代理号 our_ref (got {m.group(4)})")


def test_legacy_format_trailing_semicolon():
    # 老格式：Your/Our Ref 都紧跟分号结尾，回归不能破
    subj = ('【European search report】xxx (EP12345678.9) yyy '
            'Your Ref.: 20618-0001EP00; Our Ref: ABC123;')
    m = EP_SUBJECT_RE.search(subj)
    ok(m is not None, "老格式仍能匹配")
    ok(m.group(3) == "20618-0001EP00", f"老格式案号 (got {m.group(3)})")
    ok(m.group(4) == "ABC123", f"老格式代理号无多余分号 (got {m.group(4)})")


if __name__ == "__main__":
    for fn in [test_intention_to_grant_space_before_semicolon,
               test_legacy_format_trailing_semicolon]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
