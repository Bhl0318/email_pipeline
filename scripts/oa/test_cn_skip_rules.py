#!/usr/bin/env python3
"""CN 全局排除规则：保密审查意见通知书 / 含 reminder 的主题 一律不立项。
纯分类，不连网络。
  cd scripts/oa && python3 test_cn_skip_rules.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from filter_oa_email import classify_email

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def test_baomi_shencha_skipped():
    # 含「审查意见通知书」子串，但属保密审查 → 不立项
    ed = {
        "subject": "2026-07-21-向外国申请专利保密审查意见通知书-20618-0001CN00",
        "from": "docketing@metis-ip.com",
        "body": "", "html_body": "",
    }
    res, reason = classify_email(ed)
    ok(res is None, f"保密审查意见通知书不立项 (reason={reason})")


def test_reminder_skipped():
    ed = {
        "subject": "Reminder: 第一次审查意见通知书答复期限临近-20618-0001CN00",
        "from": "docketing@metis-ip.com",
        "body": "", "html_body": "",
    }
    res, reason = classify_email(ed)
    ok(res is None, f"含 reminder 不立项 (reason={reason})")


def test_normal_cn_still_classifies():
    # 正常第一次审查意见通知书仍立项
    ed = {
        "subject": "2026-07-21-第一次审查意见通知书-20618-0001CN00",
        "from": "docketing@metis-ip.com",
        "body": "答复期限：2026-09-21。", "html_body": "",
    }
    res, reason = classify_email(ed)
    ok(res is not None, "正常 CN 审查意见仍立项")
    ok(res.get("region") == "CN" and res.get("project") == "20618-0001CN00",
       f"CN 案号正确 (got {res.get('project') if res else None})")


if __name__ == "__main__":
    for fn in [test_baomi_shencha_skipped, test_reminder_skipped,
               test_normal_cn_still_classifies]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
