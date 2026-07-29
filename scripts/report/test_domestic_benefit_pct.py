#!/usr/bin/env python3
"""ADS Domestic Benefit/National Stage 栏 PCT 合成的复现/回归测试。

复现 bug：经 PCT bypass 入美、filing_route 存的是续案关系词（如 "Continuation in part of"）、
parent_applications 为空时，旧逻辑只认字面 "bypass"/"371"，导致该栏被漏填（空）。
案例：6M101-H003US00。

  cd scripts/report && python3 test_domestic_benefit_pct.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from submission.fields_mapping import fields_to_case_info

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def _base(route, pct=True):
    f = {
        "case_volume": "X", "case_info": {"case_name_en": "X"},
        "applicants": [{"applicant_name_en": "A", "entity_en": "Small"}],
        "inventors": [{"last_name_en": "W", "first_name_en": "H", "employer": "A"}],
        "priorities": [], "parent_applications": [], "filing_route": route,
    }
    if pct:
        f["case_advance_info"] = {"pct_app_no": "PCT/CN2025/127767", "pct_app_date": "2025-10-15"}
    return f


def _pa(route, pct=True):
    return fields_to_case_info(_base(route, pct)).get("Parent Applications", [])


def test_bypass_cip_repro():
    # 复现：6M101-H003US00，bypass CIP，filing_route="Continuation in part of"，无美国母案
    pa = _pa("Continuation in part of")
    ok(len(pa) == 1, "bypass CIP 应合成 1 行 Domestic Benefit（修前为空）")
    row = pa[0]
    ok(row["Prior Application Number"] == "PCT/CN2025/127767", "Prior Application Number = PCT 号")
    ok(row["Filing Date"] == "2025-10-15", "Filing Date = PCT 申请日")
    ok(row["Continuity Type"] == "Continuation in part of", "关系 = Continuation in part of")
    ok(row["Prior Application Status"] == "Pending", "状态默认 Pending")


def test_371_and_national_stage():
    for route in ("371", "national stage"):
        pa = _pa(route)
        ok(len(pa) == 1 and pa[0]["Continuity Type"] == "a 371 of international",
           f"route={route!r} → a 371 of international")


def test_bypass_variants():
    ok(_pa("bypass")[0]["Continuity Type"] == "Continuation of", "bypass 字面 → Continuation of")
    ok(_pa("Continuation of")[0]["Continuity Type"] == "Continuation of", "CON → Continuation of")
    ok(_pa("Division of")[0]["Continuity Type"] == "Division of", "DIV → Division of")
    ok(_pa("")[0]["Continuity Type"] == "Continuation of", "空 route + PCT → 兜底 Continuation of")


def test_no_pct_no_row():
    # 纯巴黎、无 PCT：该栏应为空，不得误填
    ok(_pa("Paris", pct=False) == [], "无 PCT（纯巴黎）→ Domestic Benefit 为空")


if __name__ == "__main__":
    test_bypass_cip_repro()
    test_371_and_national_stage()
    test_bypass_variants()
    test_no_pct_no_row()
    print(f"\nAll {_passed} checks passed.")
