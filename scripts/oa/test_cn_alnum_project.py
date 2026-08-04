#!/usr/bin/env python3
"""CN 抽案号：客户码可含字母（如 6C301-H002CS00），不能只认 5 位纯数字。
复现 bug：主题 2026-08-04-第一次补正通知书-6C301-H002CS00 抽不到 project → 不发立项。
纯分类，不连网络。
  cd scripts/oa && python3 test_cn_alnum_project.py
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


def test_alnum_customer_code_cs():
    # 复现：6C301 客户码带字母、国别 CS
    r = classify_cn(_ed("2026-08-04-第一次补正通知书-6C301-H002CS00"))
    ok(r is not None, "命中 CN 补正通知书")
    ok(r.get("project") == "6C301-H002CS00", f"抽到案号 6C301-H002CS00 (got {r.get('project')})")
    ok(r.get("notification_type") == "补正通知书", "类型=补正通知书")
    ok(r.get("issue_date") == "2026-08-04", "发文日=2026-08-04")


def test_alnum_customer_code_6a():
    r = classify_cn(_ed("2026-08-04-第一次审查意见通知书-6A902-H005CN00"))
    ok(r.get("project") == "6A902-H005CN00", "6A902 审查意见抽到案号")


def test_pure_digit_still_works():
    r = classify_cn(_ed("2026-07-09-第一次审查意见通知书-20735-0397CN00"))
    ok(r.get("project") == "20735-0397CN00", "纯数字客户码仍正常")


def test_docket_fallback_order():
    # 日期-案号-类型 顺序（CN_SUBJECT_RE 不匹配，走 docket 兜底）
    r = classify_cn(_ed("2026-08-04-6C301-H002CS00-第一次补正通知书"))
    ok(r.get("project") == "6C301-H002CS00", "日期-案号-类型 顺序也抽到带字母案号")


if __name__ == "__main__":
    for fn in [test_alnum_customer_code_cs, test_alnum_customer_code_6a,
               test_pure_digit_still_works, test_docket_fallback_order]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
