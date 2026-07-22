#!/usr/bin/env python3
"""US eGrant 通知跳过 + 正常 US 仍立项 的复现/回归测试（纯分类，不连网络）。

复现线上 bug：eGrant Notification 邮件被错误立项（列错位、[未知类型]）。
  cd scripts/oa && python3 test_us_egrant_skip.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from filter_oa_email import classify_us

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


# eGrant 真实表格：5 列（多一列 Patent），本不该立项
_EGRANT_HTML = (
    '<table><tr><td>Application</td><td>Patent</td><td>Document</td>'
    '<td>Mailroom Date</td><td>Attorney Docket No.</td></tr>'
    '<tr><td>17755973</td><td>12685537</td><td>EGRANT.NTF</td>'
    '<td>07/21/2026</td><td>20753-0003US00</td></tr></table>'
)

# 正常 Correspondence：4 列
_NORMAL_HTML = (
    '<table><tr><td>Application</td><td>Document</td>'
    '<td>Mailroom Date</td><td>Attorney Docket No.</td></tr>'
    '<tr><td>19181318</td><td>CTNF</td><td>07/21/2026</td><td>6A902-H005US00</td></tr></table>'
)


def test_egrant_skipped():
    ed = {
        "subject": "USPTO: Patent Electronic System - eGrant Notification for Customer Number 131839",
        "from": "noreply@uspto.gov",
        "html_body": _EGRANT_HTML,
        "body": "",
    }
    ok(classify_us(ed) is None, "eGrant 通知整封跳过（不立项）")


def test_normal_us_still_classifies():
    ed = {
        "subject": "USPTO: Patent Electronic System - Correspondence Notification for Customer Number 194498",
        "from": "noreply@uspto.gov",
        "html_body": _NORMAL_HTML,
        "body": "",
    }
    res = classify_us(ed)
    ok(res is not None and len(res) == 1, "正常 US 邮件仍立项")
    ok(res[0]["notification_type"] == "CTNF", f"类型 CTNF (got {res[0]['notification_type']})")
    ok(res[0]["project"] == "6A902-H005US00", f"案号正确 (got {res[0]['project']})")


if __name__ == "__main__":
    for fn in [test_egrant_skipped, test_normal_us_still_classifies]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
