#!/usr/bin/env python3
"""CN 对比文件解析 + 写回「对比文件链接」列 的复现/回归测试。

只跑纯解析(PyMuPDF)和纯字符串拼接，不连邮箱/DB/Wiki/网络。
  cd scripts/oa && python3 test_cn_ref_docs.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from parse_cn_pdf import extract_cn_ref_docs, _cn2int, parse_oa_seq
from oainfo_cli import (
    build_full_template, build_simple_template,
    _splice_ref_docs_into_body, _splice_oa_row, _ref_docs_cell_html,
)

# 拉取到的真实样本
SAMPLE_PDF = os.path.join(SCRIPT_DIR, "..",
                          "2026-07-09-第二次审查意见通知书-20664-0072CN00.pdf")

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def test_cn2int():
    ok(_cn2int("二") == 2, "中文数字 二→2")
    ok(_cn2int("十") == 10, "中文数字 十→10")
    ok(_cn2int("十一") == 11, "中文数字 十一→11")
    ok(_cn2int("二十") == 20, "中文数字 二十→20")


def test_extract_real_pdf():
    if not os.path.exists(SAMPLE_PDF):
        print("  skip - 样本 PDF 不在，跳过真实解析用例")
        return
    r = extract_cn_ref_docs(SAMPLE_PDF)
    ok(r["oa_seq"] == 2, f"OA 次数=2 (got {r['oa_seq']})")
    ok(r["ref_docs"] == [
        {"no": "3", "doc_no": "CN216192880U", "pub_date": "2022-04-05"},
        {"no": "4", "doc_no": "CN209890759U", "pub_date": "2020-01-03"},
    ], f"对比文件表两条 (got {r['ref_docs']})")


def test_cell_html():
    html = _ref_docs_cell_html([{"no": "3", "doc_no": "CN216192880U", "pub_date": "2022-04-05"}])
    ok('patents.google.com/patent/CN216192880U' in html, "单元格含 Google Patent 链接")
    ok('（2022-04-05）' in html, "单元格含公开日")


DOCS = [
    {"no": "3", "doc_no": "CN216192880U", "pub_date": "2022-04-05"},
    {"no": "4", "doc_no": "CN209890759U", "pub_date": "2020-01-03"},
]


def _full_body():
    p1, p2, p3, p4 = build_full_template("20664-0072CN00", "某标题", "CN12345", "", "", "")
    return p4  # OA过程表所在片段


def test_fill_existing_row():
    cell = _ref_docs_cell_html(DOCS)
    body, status = _splice_ref_docs_into_body(_full_body(), 2, cell)
    ok(status == "filled", f"OA2 行填入 (status={status})")
    ok("CN216192880U" in body and "CN209890759U" in body, "填入后正文含两文件号")
    # 只改了 OA2 行的对比文件列，OA1 行的该列仍空
    ok(body.count("patents.google.com") == 2, "只在一处填入两条链接")


def test_idempotent():
    cell = _ref_docs_cell_html(DOCS)
    body1, s1 = _splice_ref_docs_into_body(_full_body(), 2, cell)
    body2, s2 = _splice_ref_docs_into_body(body1, 2, cell)
    ok(s2 == "skip_nonempty", f"重复写回幂等跳过 (status={s2})")
    ok(body2 == body1, "幂等：正文不再变化")


def test_auto_add_row():
    cell = _ref_docs_cell_html(DOCS)
    body, status = _splice_ref_docs_into_body(_full_body(), 4, cell)
    ok(status == "added_row", f"OA4 无行→自动补行 (status={status})")
    ok("<td>OA4</td>" in body, "补出的行首列为 OA4")
    ok("CN216192880U" in body, "补行里填入了对比文件")


def test_fill_multi_columns():
    cells = {
        "对比文件链接": _ref_docs_cell_html(DOCS),
        "OA收文日": "2026-07-09",
        "期限": "2026-09-09",
    }
    body, status = _splice_oa_row(_full_body(), 2, cells)
    ok(status == "filled", f"多列同行填入 (status={status})")
    # 定位 OA2 行，确认三列都进去了
    import re as _re
    row = _re.search(r'<tr\b[^>]*>(?:(?!</tr>).)*?<td>OA2</td>.*?</tr>', body, _re.DOTALL).group(0)
    ok("2026-07-09" in row, "OA2 行含 OA收文日")
    ok("2026-09-09" in row, "OA2 行含 期限")
    ok("CN216192880U" in row, "OA2 行含 对比文件")
    # 简版「期限」不被误命中：期限只填在 OA2 行的「期限」列（正文出现1次）
    ok(body.count("2026-09-09") == 1, "期限只填一处")


def test_add_row_multi_columns():
    cells = {
        "对比文件链接": _ref_docs_cell_html(DOCS),
        "OA收文日": "2026-07-09",
        "期限": "2026-09-09",
    }
    body, status = _splice_oa_row(_full_body(), 4, cells)
    ok(status == "added_row", f"OA4 补行(多列) (status={status})")
    import re as _re
    row = _re.search(r'<tr\b[^>]*>(?:(?!</tr>).)*?<td>OA4</td>.*?</tr>', body, _re.DOTALL).group(0)
    ok("2026-07-09" in row and "2026-09-09" in row and "CN216192880U" in row,
       "补出的 OA4 行三列齐全")


def test_simple_template_skip():
    _p1, p2, _p3, p4 = build_simple_template("20664-0072CN00", "", "", "")
    cell = _ref_docs_cell_html(DOCS)
    body, status = _splice_ref_docs_into_body(p4, 2, cell)
    ok(status == "skip_no_column", f"简版模板无该列→跳过 (status={status})")
    ok(body == p4, "简版：正文不变")


if __name__ == "__main__":
    for fn in [test_cn2int, test_extract_real_pdf, test_cell_html,
               test_fill_existing_row, test_idempotent,
               test_auto_add_row, test_fill_multi_columns,
               test_add_row_multi_columns, test_simple_template_skip]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
