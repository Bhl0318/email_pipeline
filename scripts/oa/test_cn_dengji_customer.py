#!/usr/bin/env python3
"""CN 办理登记手续通知书客户白名单：只有 20618/20735 才立项做分案评估。
纯分类，不连网络。
  cd scripts/oa && python3 test_cn_dengji_customer.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from filter_oa_email import classify_cn

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def _ed(project):
    return {
        "subject": f"2026-07-21-办理登记手续通知书-{project}",
        "from": "docketing@metis-ip.com",
        "body": "", "html_body": "",
    }


def test_dengji_allowlisted_kept():
    for cust, proj in [("20618", "20618-1200CN00"), ("20735", "20735-0430CN00")]:
        r = classify_cn(_ed(proj))
        ok(r is not None and r["project"] == proj, f"{cust} 办登立项")
        ok(r["project_name"] == "分案评估", "立项名=分案评估")


def test_dengji_other_customer_skipped():
    for proj in ["20608-0962CN00", "20849-0001CN00"]:
        r = classify_cn(_ed(proj))
        ok(r is None, f"{proj[:5]} 办登不立项")


def test_other_cn_type_unaffected():
    # 非办登类型不受此白名单限制：20608 的第一次审查意见仍立项
    ed = {
        "subject": "2026-07-21-第一次审查意见通知书-20608-0001CN00",
        "from": "docketing@metis-ip.com",
        "body": "", "html_body": "",
    }
    r = classify_cn(ed)
    ok(r is not None and r["project"] == "20608-0001CN00", "审查意见不受办登白名单限制")


if __name__ == "__main__":
    for fn in [test_dengji_allowlisted_kept, test_dengji_other_customer_skipped,
               test_other_cn_type_unaffected]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
