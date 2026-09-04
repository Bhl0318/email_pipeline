"""doc_utils 用法示例：对现成样本跑文本抽取/切分，打印输入→输出。

样本：email_pipeline/申请文件/（真实案件 docx + PDF）。
PDF/A 需 Ghostscript，缺则只示范写法。

运行：python3 scripts/examples/doc_utils_demo.py
"""
import os
import sys

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "services"))
from doc_utils import (  # noqa: E402
    docx_text, pdf_text, split_spec, pick_latest_docx, gs_bin, to_pdfa, fill_pdf_form,
)

# 申请文件/ 在 email_pipeline 根（scripts/reusable 上溯两级）
_SAMPLE_DIR = os.path.join(_LIB, "..", "..", "申请文件")


def demo():
    print("== pick_latest_docx ==")
    spec = pick_latest_docx(_SAMPLE_DIR, keywords=["spec"])
    print("  最新含'spec'的docx:", os.path.basename(spec) if spec else None)

    print("\n== docx_text（前 200 字）==")
    text = docx_text(spec) if spec else ""
    print(" ", repr(text[:200]))

    print("\n== split_spec ==")
    desc, claims = split_spec(text)
    print("  说明部分长度:", len(desc), "| 权要部分长度:", len(claims))
    print("  权要开头:", repr(claims[:120]))

    print("\n== pdf_text（前 200 字）==")
    pdf = next((os.path.join(_SAMPLE_DIR, f) for f in sorted(os.listdir(_SAMPLE_DIR))
                if f.lower().endswith(".pdf")), None)
    print("  PDF:", os.path.basename(pdf) if pdf else None)
    print(" ", repr(pdf_text(pdf)[:200]) if pdf else "  (无样本 PDF)")

    print("\n== split_spec（纯字符串，可离线验证边界）==")
    d, c = split_spec("说明书正文……\nWHAT IS CLAIMED IS:\n1. A device...\nABSTRACT\n摘要……")
    print("  desc:", repr(d), "| claims:", repr(c))

    print("\n== to_pdfa ==")
    print("  Ghostscript:", gs_bin() or "未安装（跳过实跑）")
    print("  用法: to_pdfa(src_pdf, out_dir) -> 输出 PDF/A 路径")

    print("\n== fill_pdf_form ==")
    print("  用法: fill_pdf_form('POA.pdf', 'out.pdf', {'字段名': '值', '勾选框': True})")


if __name__ == "__main__":
    demo()
