#!/usr/bin/env python3
"""POA（Power of Attorney 委托书）生成 —— 本地 AcroForm 填表。

移植自 old_submission/confirm/func_normal_form.py 的 PDFFormHandler.genter_POA_pdf：
- 填表逻辑改用 common.fill_pdf_form（PyMuPDF），数据不出本机；
- 字段取值对齐旧实现。

签字人信息（Name/执业号/title）来自 atw.agent_info（环节4 由 fields_json→case_info
映射阶段查库填入 Signature 节点）。
⚠️ 空 POA.pdf 模板需放入 submission/templates/POA.pdf（同 ADS，从旧机取回）。
"""
import datetime
from pathlib import Path

from .common import POA_TEMPLATE, fill_pdf_form


def generate_poa(case_info: dict, output_dir, template_pdf=None) -> dict:
    """生成 POA PDF。:return: {"file_path", "file_name", "type"}"""
    template_pdf = template_pdf or POA_TEMPLATE
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sig = case_info.get("Signature", {})
    inventors = case_info.get("Inventors") or [{}]
    applicants = case_info.get("Applicants") or [{}]
    field_updates = {
        "First Named Inventor": inventors[0].get("name", ""),
        "Title": case_info.get("Title", ""),
        "Attorney Docket Number": case_info.get("Our Ref.", ""),
        "Date Optional": sig.get("Date", ""),
        "Name": sig.get("Name", ""),
        "Registration Number": str(sig.get("Registration Number", "")),
        "Title if Applicant is a juristic entity": sig.get("title", ""),
        "Applicant Name if Applicant is a juristic entity": applicants[0].get("Name", ""),
    }

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    ref = case_info.get("Our Ref.", "UNKNOWN")
    file_name = f"{today}-POA-{ref}.pdf"
    file_path = output_dir / file_name
    fill_pdf_form(template_pdf, file_path, field_updates)
    return {"file_path": str(file_path), "file_name": file_name, "type": "POA"}


if __name__ == "__main__":
    sample = {
        "Our Ref.": "64504-H006US00", "Title": "SMART KNEE BRACE",
        "Inventors": [{"name": "Wei LIN"}],
        "Applicants": [{"Name": "Mebotx Intelligent Technology (Suzhou) Co., Ltd."}],
        "Signature": {"Name": "Yifei Guan", "Registration Number": 82219,
                      "title": "Patent Agent", "Date": "2025-11-28"},
    }
    out_dir = Path(__file__).resolve().parent.parent / "ads_test_out"
    try:
        print("生成:", generate_poa(sample, out_dir))
    except FileNotFoundError as e:
        print("[跳过真生成]", e)
