"""doc_utils 测试用例。

纯函数(split_spec)与错误路径离线；docx/pdf 抽取用 email_pipeline/申请文件/ 真实样本，
样本缺失时自动跳过。to_pdfa 需 Ghostscript，缺则跳过实跑只验报错。

运行：python3 scripts/doc_utils/test_doc_utils.py   或   pytest scripts/doc_utils/test_doc_utils.py
"""
import os
import sys

_SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPTS)
from doc_utils import (  # noqa: E402
    fill_pdf_form, gs_bin, to_pdfa, others_to_pdfa,
    pdf_text, docx_text, split_spec, pick_latest_docx,
)

_SAMPLE_DIR = os.path.join(os.path.dirname(_SCRIPTS), "申请文件")


def test_split_spec_with_claims():
    text = "说明书正文……\nWHAT IS CLAIMED IS:\n1. A device...\nABSTRACT\n摘要……"
    desc, claims = split_spec(text)
    assert desc == "说明书正文……"
    assert claims.startswith("WHAT IS CLAIMED IS")
    assert "ABSTRACT" not in claims          # 摘要止，不含摘要


def test_split_spec_no_claims():
    desc, claims = split_spec("只有说明没有权要标记")
    assert desc == "只有说明没有权要标记"
    assert claims == ""                      # 切不出→空


def test_fill_pdf_form_missing_template():
    try:
        fill_pdf_form("__no_such__.pdf", "out.pdf", {})
    except FileNotFoundError:
        return
    raise AssertionError("模板不存在应抛 FileNotFoundError")


def test_gs_bin_type():
    assert gs_bin() is None or isinstance(gs_bin(), str)


def test_to_pdfa_without_gs():
    if gs_bin():
        return  # 装了 gs，跳过"缺 gs 报错"这条
    try:
        to_pdfa("whatever.pdf", ".")
    except RuntimeError:
        return
    raise AssertionError("无 Ghostscript 时应抛 RuntimeError")


def test_others_to_pdfa_passthrough_nonpdf():
    # 非 PDF 原样返回（不碰 gs）
    assert others_to_pdfa(["a.docx", "b.txt"], ".") == ["a.docx", "b.txt"]


def test_pick_and_docx_text():
    if not os.path.isdir(_SAMPLE_DIR):
        print("  (跳过 docx 测试：无样本目录)", file=sys.stderr)
        return
    spec = pick_latest_docx(_SAMPLE_DIR, keywords=["spec"])
    assert spec and spec.lower().endswith(".docx")
    text = docx_text(spec)
    assert isinstance(text, str) and len(text) > 100
    assert docx_text("__no_such__.docx") == ""    # 缺文件→空


def test_pdf_text_type():
    if not os.path.isdir(_SAMPLE_DIR):
        return
    pdf = next((os.path.join(_SAMPLE_DIR, f) for f in os.listdir(_SAMPLE_DIR)
                if f.lower().endswith(".pdf")), None)
    if pdf:
        assert isinstance(pdf_text(pdf), str)     # 有文本层→文本，扫描件→""，都是 str


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("ok", fn.__name__)
    print(f"all passed ({len(fns)})")
