#!/usr/bin/env python3
"""Assignment WHEREAS 开头 让与人(I/WE) 与 am/is/are 动态解析的回归测试。

规则（仅这两处动态；其余斜杠形式保持不动，按需求）：
  个人转公司：1 名发明人 → "I" + "am"；多名 → "WE" + "are"
  公司转公司：让与人 = 公司名；am/is/are → "is"（单数法人）

  cd scripts/report && python3 test_assignment_whereas.py
"""
import os
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from submission.assignment_generator import generate_assignment
from docx import Document

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


_BASE = {
    "case_volume": "X-001US00", "application_type": "发明",
    "case_info": {"case_name_en": "A TEST INVENTION"},
    "applicants": [{"applicant_name_en": "ACME CO., LTD.", "address1": "1 Rd", "city_en": "C"}],
    "inventors": [{"last_name_en": "WANG", "first_name_en": "Hui", "full_name_en": "WANG, Hui"},
                  {"last_name_en": "LI", "first_name_en": "Ming", "full_name_en": "LI, Ming"}],
}


def _whereas(fields, assignment):
    out = tempfile.mkdtemp(prefix="asg_")
    r = generate_assignment(fields, assignment, out)
    d = Document(r["file_path"])
    for p in d.paragraphs:
        if p.text.startswith("WHEREAS") and "entitled" in p.text:
            return p.text
    return ""


def test_single_inventor():
    t = _whereas(_BASE, {"assignment_type": "个人转公司",
                         "assignor_inventors": ["WANG, Hui"], "assignee": "ACME CO., LTD."})
    ok("WHEREAS, I," in t, "单发明人 → 让与人 = I")
    ok(" am the owner" in t, "单发明人 → am")
    ok("am/is/are" not in t and "I/WE" not in t, "单发明人 → 无未解析斜杠")


def test_multi_inventor():
    t = _whereas(_BASE, {"assignment_type": "个人转公司",
                         "assignor_inventors": ["WANG, Hui", "LI, Ming"], "assignee": "ACME CO., LTD."})
    ok("WHEREAS, WE," in t, "多发明人 → 让与人 = WE")
    ok(" are the owner" in t, "多发明人 → are")


def test_company():
    t = _whereas(_BASE, {"assignment_type": "公司转公司", "assigning_company": "BETA LLC",
                         "assignee": "ACME CO., LTD.", "company_address": "2 Rd, City"})
    ok("WHEREAS, BETA LLC," in t, "公司 → 让与人 = 公司名")
    ok(" is the owner" in t, "公司 → is（单数法人）")


def test_others_unchanged():
    # 其余斜杠形式（owner(s)/inventor(s)）按需求保持不动
    t = _whereas(_BASE, {"assignment_type": "个人转公司",
                         "assignor_inventors": ["WANG, Hui"], "assignee": "ACME CO., LTD."})
    ok("owner(s) and/or inventor(s)" in t, "其余斜杠形式(owner(s)/inventor(s))保持不动")


if __name__ == "__main__":
    test_single_inventor()
    test_multi_inventor()
    test_company()
    test_others_unchanged()
    print(f"\nAll {_passed} checks passed.")
