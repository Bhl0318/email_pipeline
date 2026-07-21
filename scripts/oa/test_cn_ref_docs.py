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
    _build_table_row, FOLLOWUP_ROTATION,
    _insert_rows_by_month,
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


def test_followup_row_placement():
    # 跟进人填在第 7 个 <td>，其后 3 列留空
    import re as _re
    row = _build_table_row({"project": "20664-0072CN00"}, "苏雅")
    tds = _re.findall(r'<td>.*?</td>', row)
    ok(len(tds) == 10, f"一行 10 个单元格 (got {len(tds)})")
    ok(tds[6] == "<td>苏雅</td>", f"第7列=跟进人 (got {tds[6]})")
    ok(tds[7:] == ["<td></td>"] * 3, "第8-10列留空")


def test_followup_rotation_order():
    # 苏雅2件、姚涓涓1件，按此顺序循环
    ok(FOLLOWUP_ROTATION == ["苏雅", "苏雅", "姚涓涓"], "轮转顺序 苏雅,苏雅,姚涓涓")
    seq = [FOLLOWUP_ROTATION[i % len(FOLLOWUP_ROTATION)] for i in range(7)]
    ok(seq == ["苏雅", "苏雅", "姚涓涓", "苏雅", "苏雅", "姚涓涓", "苏雅"],
       f"7 条分配序列正确 (got {seq})")


_OA_LIST_SAMPLE = (
    '<p>note</p>'
    '<ac:structured-macro ac:name="expand" ac:schema-version="1">'
    '<ac:parameter ac:name="title">2026年7月</ac:parameter>'
    '<ac:rich-text-body><p><br /></p>'
    '<table class="fixed-table wrapped"><colgroup><col /></colgroup><tbody>'
    '<tr><th>案号</th><th>备注</th><th>OA收到日</th><th>OA发文日</th><th>答复期限</th>'
    '<th>OA类别</th><th>跟进人</th><th>其它备注事项</th><th>人员分配</th><th>是否正式立项</th></tr>'
    '<tr><td>OLD-CASE</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>'
    '</tbody></table></ac:rich-text-body></ac:structured-macro>'
)


def test_insert_top_of_current_month():
    row = _build_table_row({"project": "NEW-CASE"}, "苏雅")
    nb, created = _insert_rows_by_month(_OA_LIST_SAMPLE, row, "2026年7月")
    ok(not created, "当月折叠块已存在，不新建")
    ok(nb.index("NEW-CASE") < nb.index("OLD-CASE"), "新行在旧行之上（置顶）")
    ok(nb.index("<th>案号</th>") < nb.index("NEW-CASE"), "新行在表头之后")


def test_insert_new_month_block():
    row = _build_table_row({"project": "AUG-CASE"}, "姚涓涓")
    nb, created = _insert_rows_by_month(_OA_LIST_SAMPLE, row, "2026年8月")
    ok(created, "当月折叠块不存在→新建")
    ok(nb.index("2026年8月") < nb.index("2026年7月"), "新月份块置于旧月份块之前")
    ok("AUG-CASE" in nb and "OLD-CASE" in nb, "新旧数据都在")
    ok(nb.index("2026年8月") < nb.index("AUG-CASE") < nb.index("2026年7月"),
       "新行落在新建的8月块内")


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
               test_add_row_multi_columns, test_followup_row_placement,
               test_followup_rotation_order, test_insert_top_of_current_month,
               test_insert_new_month_block, test_simple_template_skip]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
