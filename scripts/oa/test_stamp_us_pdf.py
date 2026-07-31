#!/usr/bin/env python3
"""DOCKETED 邮戳日期行逻辑测试（纯逻辑，不生成 PDF）。
  cd scripts/oa && python3 test_stamp_us_pdf.py
"""
import datetime
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from stamp_us_pdf import build_stamp_lines, US_STAMP_CONFIG

MAILING = datetime.datetime(2026, 7, 29)   # 发文日（邮戳日）
_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def _dates(rows):
    return [d for _, d, _ in rows if d]


def _reds(rows):
    return [(l, d) for l, d, r in rows if r]


def test_ctnf_matches_sample():
    """CTNF 必须逐字复现实样（2026-07-29 官文）。"""
    rows, _ = build_stamp_lines("CTNF", MAILING)
    got = [(l, d) for l, d, _ in rows]
    expect = [
        ("Non Final-OA", ""),
        ("2 mon from 3-mon due date:", "2026-08-29"),
        ("1 mon from 3-mon due date:", "2026-09-29"),
        ("3-mon due date:", "2026-10-29"),
        ("Due date w/1-mon EOT:", "2026-11-29"),
        ("Due date w/2-mon EOT:", "2026-12-29"),
        ("Final due date w/3-mon EOT (non-extendable):", "2027-01-29"),
        ("Check IDS when filing response", ""),
        ("Input by: 系统", ""),
        ("Reviewed by:", ""),
    ]
    ok(got == expect, "CTNF 逐行逐字匹配实样")


def test_ctnf_red_lines():
    rows, _ = build_stamp_lines("CTNF", MAILING)
    ok(_reds(rows) == [("3-mon due date:", "2026-10-29"),
                       ("Final due date w/3-mon EOT (non-extendable):", "2027-01-29")],
       "CTNF 仅 SSP 绝限行 + 最终绝限行标红")


def test_ctfr_label():
    rows, _ = build_stamp_lines("CTFR", MAILING)
    ok(rows[0][0] == "Final-OA", "CTFR 首行=Final-OA")
    ok(_dates(rows) == ["2026-08-29", "2026-09-29", "2026-10-29",
                        "2026-11-29", "2026-12-29", "2027-01-29"], "CTFR 同 3 月结构")


def test_ctrs_2month():
    rows, _ = build_stamp_lines("CTRS", MAILING)
    labels = [l for l, _, _ in rows]
    ok("1 mon from 2-mon due date:" in labels, "CTRS 提醒行=1 mon from 2-mon")
    ok("2-mon due date:" in labels, "CTRS SSP=2-mon due date")
    ok("Final due date w/4-mon EOT (non-extendable):" in labels, "CTRS 最终=4-mon EOT")
    ok(("2-mon due date:", "2026-09-29") in _reds(rows), "CTRS 2-mon due 标红(发文+2月)")


def test_buzheng_like_restriction():
    """补正类按 2 月可延期结构，且不画 Check IDS 行。"""
    for nt in ("NT.CR.APP.PA", "NTC.MISS.PRT"):
        rows, _ = build_stamp_lines(nt, MAILING)
        labels = [l for l, _, _ in rows]
        ok("2-mon due date:" in labels, f"{nt} 2-mon due date")
        ok("Final due date w/4-mon EOT (non-extendable):" in labels, f"{nt} 最终 4-mon EOT")
        ok("Check IDS when filing response" not in labels, f"{nt} 不画 Check IDS")
        ok(_dates(rows)[-1] == "2027-01-29", f"{nt} 末期=发文+6月")


def test_not_stamped_types_return_none():
    """不在盖章范围的类型返回 None（不生成盖章副本）。"""
    for nt in ("NOA", "CTAV", "CTEQ", "PPH.DECISION", "PETDEC", "EXIN", "", "未知"):
        rows, cfg = build_stamp_lines(nt, MAILING)
        ok(rows is None, f"{nt or '空'} 不盖章→None")


def test_no_mailing_date_returns_none():
    rows, _ = build_stamp_lines("CTNF", None)
    ok(rows is None, "无发文日→None")


def test_config_scope():
    ok(set(US_STAMP_CONFIG) == {"CTNF", "CTFR", "CTRS", "NT.CR.APP.PA", "NTC.MISS.PRT"},
       "盖章配置恰好=主OA答复类+补正类(不含 NOA)")


if __name__ == "__main__":
    for fn in [test_ctnf_matches_sample, test_ctnf_red_lines, test_ctfr_label,
               test_ctrs_2month, test_buzheng_like_restriction,
               test_not_stamped_types_return_none, test_no_mailing_date_returns_none,
               test_config_scope]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
