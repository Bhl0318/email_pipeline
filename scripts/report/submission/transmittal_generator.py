#!/usr/bin/env python3
"""Transmittal（递交函）生成 —— 本地 AcroForm 填表。

移植自 old_submission/confirm/func_normal_form.py 的 PDFFormHandler.genter_Transmitta_pdf：
- 按 Subject Matter 选模板：UTL→Transmittal / DES→Design-Transmittal / 其他→371-Transmittal；
- 填表用 common.fill_pdf_form（PyMuPDF）；
- 保留旧实现的"显式字段 + 合并 case_info 兜底"行为（case_info 顶层键名命中表单字段也填，
  覆盖各类 checkbox/页数等；Signature 置空避免把 dict 写进同名字段）。

签字人/Customer Number 来自 atw.agent_info；Deposit Account 同源（371/Transmittal 用）。
⚠️ 三件空模板需放入 submission/templates/（Transmittal.pdf / Design-Transmittal.pdf /
371-Transmittal.pdf，同 ADS 从旧机取回）。
"""
import datetime
from pathlib import Path

from .common import (
    TRANSMITTAL_371_TEMPLATE,
    TRANSMITTAL_DESIGN_TEMPLATE,
    TRANSMITTAL_TEMPLATE,
    fill_pdf_form,
)


def _select_template(subject_matter: str):
    if subject_matter == "UTL":
        return TRANSMITTAL_TEMPLATE, "Transmittal"
    if subject_matter == "DES":
        return TRANSMITTAL_DESIGN_TEMPLATE, "Design-Transmittal"
    return TRANSMITTAL_371_TEMPLATE, "371-Transmittal"


def generate_transmittal(case_info: dict, output_dir, template_pdf=None) -> dict:
    """生成 Transmittal PDF。:return: {"file_path", "file_name", "type"}"""
    sig = case_info.get("Signature", {})
    inventors = case_info.get("Inventors") or [{}]
    corr = case_info.get("Correspondence Information", {})
    # Subject Matter：旧 case_info 在顶层，ADS 流在 Application Information 下，两处都兜
    subject = (case_info.get("Subject Matter")
               or case_info.get("Application Information", {}).get("Subject Matter", ""))

    tmpl, ttype = _select_template(subject)
    template_pdf = template_pdf or tmpl

    explicit = {
        "First Named Inventor": inventors[0].get("name", ""),
        "Title": case_info.get("Title", ""),
        "Attorney Docket No": case_info.get("Our Ref.", ""),
        "Date": sig.get("Date", ""),
        "Name PrintType": sig.get("Name", ""),
        "Registration No AttorneyAgent": str(sig.get("Registration Number", "")),
        "The address associated with Customer Number": str(corr.get("Customer Number", "")),
    }
    # 对齐旧实现：合并 case_info 顶层键作兜底（命中表单字段名即填），Signature 置空
    merged = {**explicit, **case_info}
    merged["Signature"] = ""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    ref = case_info.get("Our Ref.", "UNKNOWN")
    file_name = f"{today}-Transmittal-{ref}.pdf"
    file_path = output_dir / file_name
    fill_pdf_form(template_pdf, file_path, merged)
    return {"file_path": str(file_path), "file_name": file_name, "type": ttype}


if __name__ == "__main__":
    sample = {
        "Our Ref.": "64504-H006US00", "Title": "SMART KNEE BRACE",
        "Subject Matter": "UTL",
        "Inventors": [{"name": "Wei LIN"}],
        "Correspondence Information": {"Customer Number": 194498},
        "Signature": {"Name": "Yifei Guan", "Registration Number": 82219, "Date": "2025-11-28"},
    }
    out_dir = Path(__file__).resolve().parent.parent / "ads_test_out"
    try:
        print("生成:", generate_transmittal(sample, out_dir))
    except FileNotFoundError as e:
        print("[跳过真生成]", e)
