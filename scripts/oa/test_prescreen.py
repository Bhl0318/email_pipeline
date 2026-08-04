#!/usr/bin/env python3
"""预审案件：第一/二次审查意见 + 邮件含「预审案件」→ 备注加注 + 转OA正文加注。
纯逻辑，不连网络。
  cd scripts/oa && python3 test_prescreen.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from filter_oa_email import classify_cn
from forward_oa import build_forward_body

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def _ed(subject, body="", html_body=""):
    return {"subject": subject, "from": "docketing@metis-ip.com",
            "body": body, "html_body": html_body}


PROJ = "20735-0397CN00"


# ---------- 分类器检测 ----------
def test_first_oa_with_prescreen():
    r = classify_cn(_ed(f"2026-07-09-第一次审查意见通知书-{PROJ}", body="本案为预审案件，请注意。"))
    ok(r.get("prescreen_note") == "预审案件", "第一次审查意见 + 预审案件 → 置 prescreen_note")


def test_second_oa_with_prescreen():
    r = classify_cn(_ed(f"2026-07-09-第二次审查意见通知书-{PROJ}", body="预审案件"))
    ok(r.get("prescreen_note") == "预审案件", "第二次审查意见 + 预审案件 → 置")


def test_prescreen_in_html_only():
    r = classify_cn(_ed(f"2026-07-09-第一次审查意见通知书-{PROJ}", html_body="<p>预审案件</p>"))
    ok(r.get("prescreen_note") == "预审案件", "预审案件在 html_body 也识别")


def test_third_oa_no_note():
    r = classify_cn(_ed(f"2026-07-09-第三次审查意见通知书-{PROJ}", body="预审案件"))
    ok("prescreen_note" not in r, "第三次审查意见即使含预审也不加注")


def test_first_oa_without_prescreen():
    r = classify_cn(_ed(f"2026-07-09-第一次审查意见通知书-{PROJ}", body="普通案件"))
    ok("prescreen_note" not in r, "第一次但无预审案件 → 不加注")


def test_buzheng_with_prescreen_no_note():
    r = classify_cn(_ed(f"2026-07-09-补正通知书-{PROJ}", body="预审案件"))
    ok("prescreen_note" not in r, "补正通知书含预审也不加注（仅审查意见）")


# ---------- 转OA 正文 ----------
def test_body_has_prescreen_line():
    body = build_forward_body({"project": PROJ, "notification_type": "审查意见通知书",
                               "oa_doc_date": "2026-07-09", "project_deadline": "2026-11-09",
                               "prescreen_note": "预审案件"})
    ok("注：该案件为预审案件" in body, "预审案件 → 正文含加注行")


def test_body_no_prescreen_line():
    body = build_forward_body({"project": PROJ, "notification_type": "审查意见通知书",
                               "oa_doc_date": "2026-07-09", "project_deadline": "2026-11-09"})
    ok("预审案件" not in body, "非预审 → 正文无加注行")


if __name__ == "__main__":
    for fn in [test_first_oa_with_prescreen, test_second_oa_with_prescreen,
               test_prescreen_in_html_only, test_third_oa_no_note,
               test_first_oa_without_prescreen, test_buzheng_with_prescreen_no_note,
               test_body_has_prescreen_line, test_body_no_prescreen_line]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
