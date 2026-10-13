#!/usr/bin/env python3
"""调用 OA 前端分析正在使用的 FPO 下载流程，验证对比文件能否下载并读取。

用法：
    python scripts/oa/check_fpo_download.py US20250150762A1
    python scripts/oa/check_fpo_download.py CN110693604A --output outputs/fpo_check/CN110693604A.pdf

成功时将 PDF 保存到 outputs/fpo_check/（或 --output 指定的位置）；失败时返回非零退出码。
不需要 QDFX_API_TOKEN，也不会调用前端分析提交接口。
"""

import argparse
import sys
from pathlib import Path

import fitz

from download_patent_pdf import _new_session
from qdfx_external import _fpo_pdf, _publication_number, _reference_pdf_text


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "fpo_check"


def check_download(raw_number, output_path=None):
    """下载并核对 PDF；成功返回保存路径，失败抛出异常。"""
    number = _publication_number(raw_number)
    if not number:
        raise ValueError("请输入带国别和文献种类代码的公开号，例如 US20250150762A1")

    session, _ = _new_session()
    try:
        pdf_data, source = _fpo_pdf(number, session=session)
    finally:
        session.close()

    if not pdf_data.startswith(b"%PDF-") or len(pdf_data) > 32_000_000:
        raise ValueError("FPO 返回的内容不是有效大小的 PDF")
    with fitz.open(stream=pdf_data, filetype="pdf") as pdf:
        page_count = pdf.page_count
    if page_count < 1:
        raise ValueError("PDF 没有可读取的页面")

    target = Path(output_path) if output_path else DEFAULT_OUTPUT_DIR / f"{number}.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(pdf_data)
    print(f"下载成功：{number}")
    print(f"来源：{source}")
    print(f"PDF：{target.resolve()}")
    print(f"页数：{page_count}；大小：{len(pdf_data)} 字节")
    # 下载成功与是否满足前端分析的全文要求分别报告，便于定位问题。
    try:
        description, claims = _reference_pdf_text(number, pdf_data)
        print(f"全文校验通过：说明书 {len(description)} 字符；权利要求 {len(claims)} 字符")
    except Exception as exc:
        print(f"全文校验未通过（自动前端分析会跳过）：{exc}")
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description="测试 OA 前端分析所用的 FPO 对比文件下载流程")
    parser.add_argument("publication_number", help="专利公开号，如 US20250150762A1")
    parser.add_argument("--output", help="保存 PDF 的路径，默认 outputs/fpo_check/<公开号>.pdf")
    args = parser.parse_args(argv)
    try:
        check_download(args.publication_number, args.output)
    except Exception as exc:
        print(f"FPO 下载失败：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
