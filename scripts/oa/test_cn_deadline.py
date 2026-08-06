#!/usr/bin/env python3
"""CN 答复期限确定性计算 compute_cn_deadline（跳周末+法定节假日；预审含发文日当天）。
纯逻辑，不连网络（不测 LLM 归一化）。
  cd scripts/oa && python3 test_cn_deadline.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from filter_oa_email import compute_cn_deadline, _parse_date

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def D(s):
    return _parse_date(s)


def test_preexam_workdays_this_email():
    # 复现本封：2026-08-04(周二) 预审 五个工作日 → 08-10(周一)
    ok(compute_cn_deadline({"type": "working_days", "n": 5}, D("2026-08-04"), True) == "2026-08-10",
       "预审5工作日: 08-04→08-10(含当天,跳周末)")


def test_non_preexam_workdays():
    ok(compute_cn_deadline({"type": "working_days", "n": 5}, D("2026-08-04"), False) == "2026-08-11",
       "非预审5工作日: 从次日起算 → 08-11")


def test_workday_skips_holiday():
    # 发文 2026-09-30(周三) 预审5工作日：跳国庆(10-01~07)+周末 → 10-13
    ok(compute_cn_deadline({"type": "working_days", "n": 5}, D("2026-09-30"), True) == "2026-10-13",
       "跨国庆: 09-30预审5工作日 → 10-13")


def test_one_workday_preexam_on_workday():
    ok(compute_cn_deadline({"type": "working_days", "n": 1}, D("2026-08-04"), True) == "2026-08-04",
       "预审1工作日且发文日是工作日 → 当天")


def test_workday_base_on_weekend():
    # 发文落在周六(2026-08-08) 预审1工作日 → 顺到下一个工作日 08-10(周一)
    ok(compute_cn_deadline({"type": "working_days", "n": 1}, D("2026-08-08"), True) == "2026-08-10",
       "发文落周末,预审1工作日 → 下一个工作日")


def test_months():
    ok(compute_cn_deadline({"type": "months", "n": 2}, D("2026-08-04"), True) == "2026-10-04",
       "2个月: 08-04 → 10-04(日历)")


def test_calendar_days():
    ok(compute_cn_deadline({"type": "calendar_days", "n": 30}, D("2026-08-04"), True) == "2026-09-03",
       "30自然日: 08-04 → 09-03")


def test_absolute():
    ok(compute_cn_deadline({"type": "absolute", "date": "2026-09-10"}, D("2026-08-04"), True) == "2026-09-10",
       "绝对日期直接用")
    ok(compute_cn_deadline({"type": "absolute", "date": "乱码"}, D("2026-08-04"), True) is None,
       "绝对日期无法解析 → None")


def test_bad_intent():
    ok(compute_cn_deadline({"type": "working_days", "n": 0}, D("2026-08-04"), True) is None, "n=0 → None")
    ok(compute_cn_deadline({"type": "working_days"}, D("2026-08-04"), True) is None, "缺 n → None")
    ok(compute_cn_deadline({"type": "unknown", "n": 3}, D("2026-08-04"), True) is None, "未知type → None")
    ok(compute_cn_deadline(None, D("2026-08-04"), True) is None, "intent=None → None")
    ok(compute_cn_deadline({"type": "months", "n": 2}, None, True) is None, "无发文日 → None")


if __name__ == "__main__":
    for fn in [test_preexam_workdays_this_email, test_non_preexam_workdays, test_workday_skips_holiday,
               test_one_workday_preexam_on_workday, test_workday_base_on_weekend,
               test_months, test_calendar_days, test_absolute, test_bad_intent]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
