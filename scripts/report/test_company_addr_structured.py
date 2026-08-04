#!/usr/bin/env python3
"""转让方公司地址结构化（中英+城市/省/邮编/国家）的回归测试 + 旧单串兼容。

  cd scripts/report && python3 test_company_addr_structured.py
"""
import os
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from submission.common import company_addr_dict, _assignee_from_applicant, parse_address_en
from submission.confirmation_sheet import generate_confirmation_sheet
from docx import Document

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def test_structured_dict():
    a = {"assignment_type": "公司转公司", "assigning_company": "BMC（TIANJIN）MEDICAL CO., LTD.",
         "company_address1": "3/F, Building No.4, No.1 Xinxing Road", "company_address2": "Wuqing District",
         "company_city_en": "Tianjin", "company_postcode": "301799", "company_country_en": "China"}
    cd = company_addr_dict(a)
    ok(cd["city_en"] == "Tianjin" and cd["postcode"] == "301799" and cd["country_en_us"] == "China",
       "结构化字段映射到 city/postcode/country")
    ca = _assignee_from_applicant(cd)
    ok(ca["address1"] and "Tianjin" in (ca["address1"] + ca["address2"]),
       "Assignment 拼全址（含城市）拆 2 行")


def test_fallback_old_string():
    a = {"assignment_type": "公司转公司", "assigning_company": "X",
         "company_address": "3/F, Xinxing Road, Tianjin, 301799, China"}
    cd = company_addr_dict(a)
    ok(cd["address1"] == "3/F" and not cd.get("city_en"),
       "旧单串回退：逗号拆 address1/2，无城市细分（不破坏存量）")


def test_confirmation_shows_structured():
    f = {"case_volume": "X-001US00", "application_type": "发明", "ae_methods": "无",
         "case_info": {"case_name_en": "T"},
         "applicants": [{"applicant_name_en": "BMC MEDICAL CO., LTD.", "address1": "Room 110",
                         "city_en": "Beijing", "postcode": "100142", "country_en_us": "China", "entity_en": "Large"}],
         "inventors": [{"last_name_en": "CHEN", "first_name_en": "Xi", "full_name_en": "CHEN, Xi",
                        "employer": "BMC(TIANJIN)MEDICAL CO., LTD."}],
         "priorities": [], "parent_applications": [], "filing_route": "Bypass Continuation",
         "assignments": [{"assignment_type": "个人转公司", "assignor_inventors": ["CHEN, Xi"], "assignee": "BMC MEDICAL CO., LTD."},
                         {"assignment_type": "公司转公司", "assigning_company": "BMC（TIANJIN）MEDICAL CO., LTD.",
                          "company_representative": "XU", "representative_title": "Mgr",
                          "company_address1": "3/F, Building No.4, No.1 Xinxing Road", "company_address2": "Wuqing District",
                          "company_city_en": "Tianjin", "company_postcode": "301799", "company_country_en": "China"}]}
    out = tempfile.mkdtemp(prefix="cas_")
    r = generate_confirmation_sheet(f, out)
    d = Document(r["file_path"])
    txt = "\n".join(c.text for t in d.tables for row in t.rows for c in row.cells)
    ok("Tianjin" in txt and "301799" in txt, "确认函归属公司组显示城市/邮编（结构化生效）")


def test_parse_address():
    r = parse_address_en("3/F, Building No.4, No.1 Xinxing Road, Wuqing District, Tianjin, 301799, China")
    ok(r["city_en"] == "Tianjin" and r["postcode"] == "301799" and r["country_en_us"] == "China",
       "粘贴地址识别：城市/邮编/国家（邮编独立成段）")
    r2 = parse_address_en("Room 110, Fengyu Tower, Haidian District, Beijing 100142, China")
    ok(r2["city_en"] == "Beijing" and r2["postcode"] == "100142",
       "粘贴地址识别：城市与邮编同段 'Beijing 100142'")


if __name__ == "__main__":
    test_structured_dict()
    test_fallback_old_string()
    test_confirmation_shows_structured()
    test_parse_address()
    print(f"\nAll {_passed} checks passed.")
