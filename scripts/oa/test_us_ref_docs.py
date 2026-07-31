#!/usr/bin/env python3
"""US 同案号 892/1449 文献收集：挂到该案 OA 立项项的 us_ref_docs，供 dispatch 下载。
纯分类，不连网络。
  cd scripts/oa && python3 test_us_ref_docs.py
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
    """rows: [(application, document, mailroom_date, project), ...]"""
    head = ('<tr><td>Application</td><td>Document</td>'
            '<td>Mailroom Date</td><td>Attorney Docket No.</td></tr>')
    trs = "".join(f'<tr><td>{a}</td><td>{d}</td><td>{m}</td><td>{p}</td></tr>' for a, d, m, p in rows)
    return {
        "subject": "USPTO: Patent Electronic System - Correspondence Notification for Customer Number 1",
        "from": "noreply@uspto.gov",
        "html_body": f"<table>{head}{trs}</table>",
        "body": "",
    }


def _find(res, project):
    return next((r for r in (res or []) if r["project"] == project), None)


def test_collects_892_1449():
    res = classify_us(_ed([
        ("18", "CTNF", "07/21/2026", "20618-0001US00"),
        ("18", "892", "07/21/2026", "20618-0001US00"),
        ("18", "1449", "07/21/2026", "20618-0001US00"),
    ]))
    oa = _find(res, "20618-0001US00")
    ok(oa is not None and oa["notification_type"] == "CTNF", "OA(CTNF)立项")
    codes = [r["document_code"] for r in oa.get("us_ref_docs", [])]
    ok(codes == ["892", "1449"], f"挂上 892+1449 (got {codes})")
    ok(all(r["application_no"] == "18" and r["oa_doc_date"] == "07/21/2026"
           for r in oa["us_ref_docs"]), "文献行带 申请号+发文日")


def test_892_only():
    res = classify_us(_ed([
        ("18", "CTFR", "07/21/2026", "20618-0002US00"),
        ("18", "892", "07/21/2026", "20618-0002US00"),
    ]))
    oa = _find(res, "20618-0002US00")
    ok([r["document_code"] for r in oa.get("us_ref_docs", [])] == ["892"], "只有 892")


def test_no_ref_no_key():
    res = classify_us(_ed([("18", "CTNF", "07/21/2026", "20618-0003US00")]))
    oa = _find(res, "20618-0003US00")
    ok("us_ref_docs" not in oa, "无 892/1449 → 不挂 us_ref_docs")


def test_ref_matches_by_project():
    # 892 属于另一个案号 → 不挂到本案
    res = classify_us(_ed([
        ("18", "CTNF", "07/21/2026", "20618-0004US00"),
        ("19", "892", "07/21/2026", "20618-0009US00"),
    ]))
    oa = _find(res, "20618-0004US00")
    ok("us_ref_docs" not in oa, "别案的 892 不挂到本案")


def test_892_not_projected():
    # 892/1449 本身不产生立项项
    res = classify_us(_ed([
        ("18", "CTNF", "07/21/2026", "20618-0005US00"),
        ("18", "892", "07/21/2026", "20618-0005US00"),
    ]))
    ok(all(r["notification_type"] != "892" for r in res), "892 不作为立项项返回")


if __name__ == "__main__":
    for fn in [test_collects_892_1449, test_892_only, test_no_ref_no_key,
               test_ref_matches_by_project, test_892_not_projected]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
