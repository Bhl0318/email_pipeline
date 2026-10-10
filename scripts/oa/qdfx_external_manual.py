#!/usr/bin/env python3
"""用手工指定的案件和文件，直接调用正式 OA 前端分析提交流程。

只需修改下方四项配置，然后运行：
  python scripts/oa/qdfx_external_manual.py

流程会提取审查意见中的对比文件号、从 FPO 获取并校验全文，最后调用
POST /assist/qdfx/external/parse。需在环境中配置 QDFX_API_TOKEN；
本脚本不会执行 OA 立项、写入本地数据库或发送邮件。
"""

import json
import re
import sys
from pathlib import Path

from qdfx_external import _ep_reference_numbers, _publication_number, submit_oa_analysis


# 在这里填写真实参数。REFERENCE_NUMBERS 留空时从审查意见自动提取。
CASE_NO = ""
OA_FILE = ""
APPLICATION_FILE = ""
REFERENCE_NUMBERS = []


def _read_text(path):
    if not path.is_file():
        raise FileNotFoundError(path)
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


def _extract_ref_docs(region, oa_path, oa_text):
    if region == "CN":
        from parse_cn_pdf import _regex_extract_ref_docs, extract_cn_ref_docs
        docs = (extract_cn_ref_docs(str(oa_path)).get("ref_docs", []) if oa_path.suffix.lower() == ".pdf"
                else _regex_extract_ref_docs(oa_text))
    elif region == "US":
        from parse_us_refs import _regex_extract, extract_us_ref_docs
        docs = (extract_us_ref_docs(str(oa_path)).get("ref_docs", []) if oa_path.suffix.lower() == ".pdf"
                else _regex_extract(oa_text))
    else:
        docs = _ep_reference_numbers(oa_text)
    return docs


def run_case(case_no, oa_file, application_file, reference_numbers=()):
    project = case_no.strip().upper()
    match = re.fullmatch(r"[A-Z0-9-]+(CN|US|EP)\d{2}", project)
    if not match:
        raise ValueError("请填写以 CN/US/EP 加两位数字结尾的案号")
    oa_path, app_path = Path(oa_file), Path(application_file)
    oa_text, app_text = _read_text(oa_path), _read_text(app_path)
    if not oa_text.strip() or not app_text.strip():
        raise ValueError("审查意见或申请文件未能读取为文本")

    if reference_numbers:
        numbers = [_publication_number(raw) for raw in reference_numbers]
        if not all(numbers):
            raise ValueError("REFERENCE_NUMBERS 中有无法识别的专利公开号")
        ref_docs = [{"doc_no": number} for number in dict.fromkeys(numbers)]
    else:
        ref_docs = _extract_ref_docs(match.group(1), oa_path, oa_text)
    if not ref_docs:
        raise ValueError("未提取到对比文件号；请检查审查意见，或手工填写 REFERENCE_NUMBERS")

    print(f"案号：{project}")
    print("对比文件：" + ", ".join(str(doc.get("doc_no", "")) for doc in ref_docs))
    return submit_oa_analysis(
        {"project": project, "region": match.group(1)},
        oa_text,
        ref_docs,
        application_text=app_text,
    )


def main():
    if not CASE_NO or not OA_FILE or not APPLICATION_FILE:
        print("请先在脚本开头填写 CASE_NO、OA_FILE、APPLICATION_FILE", file=sys.stderr)
        return 2
    try:
        result = run_case(CASE_NO, OA_FILE, APPLICATION_FILE, REFERENCE_NUMBERS)
    except Exception as exc:
        print(f"测试失败：{exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ("submitted", "processing") else 1


if __name__ == "__main__":
    sys.exit(main())
