#!/usr/bin/env python3
"""Examiner Interview Summary：官文含 'It is not necessary for applicant' → 不立项。
用 PyMuPDF 造文字层 PDF 验证文字路径（OCR 路径需联网，不在此测）。
  cd scripts/oa && python3 test_interview_summary.py
"""
import os
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from parse_us_pdf import interview_no_action_needed

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def _make_pdf(text):
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), text, fontsize=11)
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc.save(path)
    doc.close()
    return path


def main():
    with_phrase = _make_pdf("Examiner Interview Summary Record\n"
                            "It is not necessary for applicant to provide a separate record.")
    without = _make_pdf("Examiner Interview Summary Record\n"
                        "Applicant is required to respond to the outstanding rejection.")
    upper = _make_pdf("IT IS NOT NECESSARY FOR APPLICANT to provide a separate record.")
    try:
        ok(interview_no_action_needed(with_phrase) is True, "含该句 → True(不立项)")
        ok(interview_no_action_needed(without) is False, "不含该句 → False(仍立项)")
        ok(interview_no_action_needed(upper) is True, "大小写不敏感 → True")
        ok(interview_no_action_needed("/no/such/file.pdf") is False, "文件不存在 → False")
        ok(interview_no_action_needed("") is False, "空路径 → False")
    finally:
        for p in (with_phrase, without, upper):
            os.remove(p)


if __name__ == "__main__":
    main()
    print(f"\n全部通过：{_passed} 项断言")
