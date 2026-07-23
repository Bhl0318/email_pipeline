#!/usr/bin/env python3
"""US NOA 客户白名单：只有指定客户的 NOA 才立项。纯分类，不连网络。
  cd scripts/oa && python3 test_us_noa_customer.py
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


def _ed(rows):
    head = ('<tr><td>Application</td><td>Document</td>'
            '<td>Mailroom Date</td><td>Attorney Docket No.</td></tr>')
    body = ''.join(f'<tr><td>{a}</td><td>{d}</td><td>{m}</td><td>{p}</td></tr>'
                   for a, d, m, p in rows)
    return {
        "subject": "USPTO: Patent Electronic System - Correspondence Notification for Customer Number 1",
        "from": "noreply@uspto.gov",
        "html_body": f"<table>{head}{body}</table>",
        "body": "",
    }


def test_noa_allowlisted_customer_kept():
    res = classify_us(_ed([("18", "NOA", "07/21/2026", "20608-0320US00")]))
    ok(res is not None and len(res) == 1, "20608 的 NOA 立项")
    ok(res[0]["project"] == "20608-0320US00", "案号正确")


def test_noa_other_customer_skipped():
    res = classify_us(_ed([("18", "NOA", "07/21/2026", "20909-0002US00")]))
    ok(res is None, "20909 的 NOA 不立项（整表只此一条→None）")


def test_mixed_noa_and_ctnf():
    res = classify_us(_ed([
        ("1", "NOA", "07/21/2026", "20618-0001US00"),   # 在册 → 留
        ("2", "NOA", "07/21/2026", "20909-0002US00"),   # 不在册 → 去
        ("3", "CTNF", "07/21/2026", "70000-0003US00"),  # 非 NOA → 不受客户限制
    ]))
    projs = {r["project"] for r in (res or [])}
    ok("20618-0001US00" in projs, "在册客户 NOA 保留")
    ok("20909-0002US00" not in projs, "不在册客户 NOA 剔除")
    ok("70000-0003US00" in projs, "CTNF 不受 NOA 客户白名单限制")


if __name__ == "__main__":
    for fn in [test_noa_allowlisted_customer_kept,
               test_noa_other_customer_skipped,
               test_mixed_noa_and_ctnf]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
