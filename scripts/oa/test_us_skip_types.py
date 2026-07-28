#!/usr/bin/env python3
"""US 跳过类型：M327 / PREDOCK.NTF 不立项。纯分类,不连网络。
  cd scripts/oa && python3 test_us_skip_types.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from filter_oa_email import classify_us, US_TYPES_SKIP, US_TYPES_NEED_PROJECT

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def _ed(doc_type, project="20618-0001US00"):
    head = ('<tr><td>Application</td><td>Document</td>'
            '<td>Mailroom Date</td><td>Attorney Docket No.</td></tr>')
    row = f'<tr><td>18</td><td>{doc_type}</td><td>07/21/2026</td><td>{project}</td></tr>'
    return {
        "subject": "USPTO: Patent Electronic System - Correspondence Notification for Customer Number 1",
        "from": "noreply@uspto.gov",
        "html_body": f"<table>{head}{row}</table>",
        "body": "",
    }


def test_config():
    ok("M327" in US_TYPES_SKIP, "M327 在跳过表")
    ok("PREDOCK.NTF" in US_TYPES_SKIP, "PREDOCK.NTF 在跳过表")
    ok("M327" not in US_TYPES_NEED_PROJECT, "M327 已从立项表移除")


def test_m327_skipped():
    ok(classify_us(_ed("M327")) is None, "M327 不立项")


def test_predock_skipped():
    ok(classify_us(_ed("PREDOCK.NTF")) is None, "PREDOCK.NTF 不立项")


def test_normal_still_classifies():
    res = classify_us(_ed("CTNF"))
    ok(res is not None and res[0]["notification_type"] == "CTNF", "CTNF 仍立项")


if __name__ == "__main__":
    for fn in [test_config, test_m327_skipped, test_predock_skipped, test_normal_still_classifies]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
