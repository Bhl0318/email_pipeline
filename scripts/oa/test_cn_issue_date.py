#!/usr/bin/env python3
"""CN 发文日提取：主题 日期-案号-类型 顺序也能抓到发文日。纯分类,不连网络。
  cd scripts/oa && python3 test_cn_issue_date.py
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


def _ed(subject):
    return {"subject": subject, "from": "docketing@metis-ip.com", "body": "", "html_body": ""}


def test_date_docket_type_order():
    # 日期-案号-类型 顺序（CN_SUBJECT_RE 不匹配）→ 兜底仍抓到发文日
    r = classify_cn(_ed("2026-07-09-20735-0397CN00-第一次审查意见通知书"))
    ok(r is not None, "仍识别为 CN 立项")
    ok(r.get("issue_date") == "2026-07-09", f"发文日兜底抓到 (got {r.get('issue_date')})")
    ok(r.get("project") == "20735-0397CN00", "案号仍提取")


def test_standard_order_unaffected():
    # 日期-类型-案号 标准顺序不受影响
    r = classify_cn(_ed("2026-07-09-第一次审查意见通知书-20735-0397CN00"))
    ok(r.get("issue_date") == "2026-07-09", "标准顺序发文日正常")
    ok(r.get("project") == "20735-0397CN00", "标准顺序案号正常")


if __name__ == "__main__":
    for fn in [test_date_docket_type_order, test_standard_order_unaffected]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
