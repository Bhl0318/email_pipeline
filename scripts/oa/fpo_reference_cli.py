#!/usr/bin/env python3
"""按审查意见中的对比文件号，从 FPO 下载并核对专利 PDF。

用法：
  python scripts/oa/fpo_reference_cli.py \
    --case 20615-0011US00 --oa /path/to/oa.pdf --application /path/to/spec.docx

审查意见和申请文件支持 PDF、MD、TXT；申请文件另支持 DOCX。
若规则未能从审查意见中提取文献号，可重复传 --ref 手动指定。
结果写入 outputs/qdfx_fpo_test/<案号>/，不会调用外部解析接口。
"""

import argparse
import json
import re
import sys
from pathlib import Path

from qdfx_external import _ep_reference_numbers, _fpo_pdf, _publication_number, _reference_pdf_text


WORKSPACE = Path(__file__).resolve().parents[2]


def _read_text(path):
    suffix = path.suffix.lower()
    if suffix in (".md", ".txt"):
        return path.read_text(encoding="utf-8-sig")
    if suffix == ".docx":
        from oa_report_ai import _docx_text
        return _docx_text(str(path)) or ""
    if suffix == ".pdf":
        import fitz
        with fitz.open(path) as pdf:
            text = "\n".join(page.get_text() for page in pdf)
        if text.strip():
            return text
        from mistral_ocr import pdf_to_markdown
        return pdf_to_markdown(str(path)) or ""
    raise ValueError(f"不支持的文件格式: {path.suffix}")


def _extract_numbers(region, text):
    if region == "CN":
        from parse_cn_pdf import _regex_extract_ref_docs
        docs = _regex_extract_ref_docs(text)
    elif region == "US":
        from parse_us_refs import _regex_extract
        docs = _regex_extract(text)
    else:
        docs = _ep_reference_numbers(text)
    return list(dict.fromkeys(n for doc in docs
                              if (n := _publication_number(doc.get("doc_no")))))


def run(case, oa_path, application_path, manual_refs=(), output_root=None):
    if not re.fullmatch(r"[A-Za-z0-9-]+", case):
        raise ValueError("案号只允许字母、数字和连字符")
    match = re.search(r"(CN|US|EP)\d{2}$", case.upper())
    if not match:
        raise ValueError("案号需以 CN/US/EP 加两位数字结尾")
    for path in (oa_path, application_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    oa_text = _read_text(oa_path)
    app_text = _read_text(application_path)
    if not oa_text.strip():
        raise ValueError("审查意见无法读取为文本；扫描件请检查 Mistral OCR 配置")
    if not app_text.strip():
        raise ValueError("申请文件无法读取为文本")

    if manual_refs:
        numbers = [_publication_number(raw) for raw in manual_refs]
        if not all(numbers):
            raise ValueError("--ref 中有无法识别的专利公开号")
        numbers = list(dict.fromkeys(numbers))
    else:
        numbers = _extract_numbers(match.group(1), oa_text)

    root = output_root or (WORKSPACE / "outputs" / "qdfx_fpo_test")
    out_dir = root / case
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {"case": case, "oa": str(oa_path), "application": str(application_path),
              "reference_numbers": numbers, "documents": []}
    for number in numbers:
        entry = {"number": number}
        try:
            pdf_data, source = _fpo_pdf(number)
            _reference_pdf_text(number, pdf_data)
            target = out_dir / f"{number}.pdf"
            target.write_bytes(pdf_data)
            entry.update(status="downloaded", source=source, pdf=str(target))
        except Exception as exc:
            entry.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        result["documents"].append(entry)

    result["status"] = ("no_references" if not numbers else
                        "downloaded" if all(d["status"] == "downloaded" for d in result["documents"])
                        else "incomplete")
    summary = out_dir / "summary.json"
    summary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result["summary"] = str(summary)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--case", required=True, help="案号，如 20615-0011US00")
    parser.add_argument("--oa", required=True, type=Path, help="审查意见 PDF/MD/TXT")
    parser.add_argument("--application", required=True, type=Path, help="申请文件 DOCX/PDF/MD/TXT")
    parser.add_argument("--ref", action="append", default=[], help="可重复；提供时覆盖自动提取的文献号")
    args = parser.parse_args(argv)
    try:
        result = run(args.case, args.oa, args.application, args.ref)
    except Exception as exc:
        parser.exit(2, f"错误: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "downloaded" else 1


if __name__ == "__main__":
    sys.exit(main())
