#!/usr/bin/env python3
"""Transmittal（递交函/递交清单）生成 —— 本地 AcroForm 填表。

移植自 old_submission/confirm/func_normal_form.py 的 genter_Transmitta_pdf，并补全
"递交清单"输入（实体/页数/POA·IDS·序列表·PA·Assignment·ADS·备注 等本次实际递交内容）。

- 按 Subject Matter 选模板：UTL→Transmittal / DES→Design-Transmittal / 其他→371-Transmittal；
- 表头字段(发明人/Title/案号/签字人/Customer Number)来自 case_info；
- 清单字段来自 options（transmittal_options，操作员在审核页填，fields_json 无）；
- 三模板复选框字段名不同，本模块各自映射（UTL 的 Check Box54-80 已按表单实物对号）。

options（transmittal_options）schema（全部可选，缺省不勾/不填）：
  { "entity": "large|small|micro", "spec_pages": "", "drawing_sheets": "",
    "declaration_pages": "", "has_declaration": bool, "has_poa": bool, "has_ids": bool,
    "has_preliminary_amendment": bool, "has_sequence_listing": bool,
    "has_assignment": bool, "has_ads": bool, "remark": "" }
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


def _options_fields(ttype: str, opts: dict) -> dict:
    """把递交清单 options 映射成该模板的表单字段（复选框命中即勾，文本填值）。"""
    if not opts:
        return {}
    o = opts
    entity = (o.get("entity") or "").lower()
    f = {}

    if ttype == "Transmittal":  # UTL，Check Box54-80 已按表单实物对号
        if entity == "small":
            f["Check Box55"] = "Yes"
        elif entity == "micro":
            f["Check Box56"] = "Yes"
        if o.get("spec_pages"):
            f["Check Box57"] = "Yes"; f["Total Pages"] = o["spec_pages"]
        if o.get("drawing_sheets"):
            f["Check Box58"] = "Yes"; f["Total Sheets"] = o["drawing_sheets"]
        if o.get("has_declaration"):
            f["Check Box59"] = "Yes"  # Newly executed（原始声明）
            if o.get("declaration_pages"):
                f["Total Pages_2"] = o["declaration_pages"]
        if o.get("has_assignment"):
            f["Check Box68"] = "Yes"
        if o.get("has_poa"):
            f["Check Box70"] = "Yes"
        if o.get("has_ids"):
            f["Check Box72"] = "Yes"
        if o.get("has_preliminary_amendment"):
            f["Check Box74"] = "Yes"
        if o.get("has_ads"):
            f["Check Box61"] = "Yes"
        if o.get("has_sequence_listing"):
            f["Check Box64"] = "Yes"; f["Check Box66"] = "Yes"  # 序列表 + Paper
        if o.get("remark"):
            f["Check Box78"] = "Yes"; f["Other 1"] = o["remark"]

    elif ttype == "Design-Transmittal":  # 字段名自描述
        if entity == "small":
            f["Applicant asserts small entity status"] = "Yes"
        elif entity == "micro":
            f["Applicant certifies micro entity status"] = "Yes"
        if o.get("spec_pages"):
            f["Specification"] = "Yes"; f["Total Pages"] = o["spec_pages"]
        if o.get("drawing_sheets"):
            f["Drawings"] = "Yes"; f["Total Sheets"] = o["drawing_sheets"]
        if o.get("declaration_pages"):
            f["Total Pages_2"] = o["declaration_pages"]
        if o.get("has_assignment"):
            f["Assignment Papers"] = "Yes"
        if o.get("has_poa"):
            f["Power of Attorney"] = "Yes"
        if o.get("has_ids"):
            f["Information Disclosure Statement (IDS)"] = "Yes"
        if o.get("has_preliminary_amendment"):
            f["Preliminary Amendment"] = "Yes"
        if o.get("has_ads"):
            f["Application Data Sheet"] = "Yes"
        if o.get("remark"):
            f["Other"] = "Yes"; f["Other 1"] = o["remark"]

    else:  # 371-Transmittal：字段以费用为主，先映射实体/序列表，其余（IDS/检索报告/费用）待补
        if entity == "small":
            f["small entity"] = "Yes"
        elif entity == "micro":
            f["micro entity"] = "Yes"
        if o.get("has_sequence_listing"):
            f["6a SL part of IA"] = "Yes"
        if o.get("remark"):
            f["Other items / information"] = o["remark"]
    return f


def generate_transmittal(case_info: dict, output_dir, template_pdf=None, options: dict = None) -> dict:
    """生成 Transmittal PDF。
    :param options: 递交清单 transmittal_options（实体/页数/各文件有无/备注），见模块 docstring
    :return: {"file_path", "file_name", "type", "warnings"}
    """
    sig = case_info.get("Signature", {})
    inventors = case_info.get("Inventors") or [{}]
    corr = case_info.get("Correspondence Information", {})
    subject = (case_info.get("Subject Matter")
               or case_info.get("Application Information", {}).get("Subject Matter", ""))

    tmpl, ttype = _select_template(subject)
    template_pdf = template_pdf or tmpl
    warnings = []
    if ttype == "371-Transmittal" and options:
        warnings.append("371-Transmittal 仅映射实体/序列表/备注，IDS/检索报告/费用项待补")

    explicit = {
        "First Named Inventor": inventors[0].get("name", ""),
        "Title": case_info.get("Title", ""),
        "Attorney Docket No": case_info.get("Our Ref.", ""),
        "Date": sig.get("Date", ""),
        "Name PrintType": sig.get("Name", ""),
        "Registration No AttorneyAgent": str(sig.get("Registration Number", "")),
        "The address associated with Customer Number": str(corr.get("Customer Number", "")),
    }
    # 对齐旧实现：合并 case_info 顶层键作兜底；再叠加递交清单 options 映射；Signature 置空
    merged = {**explicit, **case_info, **_options_fields(ttype, options)}
    merged["Signature"] = ""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    ref = case_info.get("Our Ref.", "UNKNOWN")
    file_name = f"{today}-Transmittal-{ref}.pdf"
    file_path = output_dir / file_name
    fill_pdf_form(template_pdf, file_path, merged)
    return {"file_path": str(file_path), "file_name": file_name, "type": ttype, "warnings": warnings}


if __name__ == "__main__":
    sample = {
        "Our Ref.": "64504-H006US00", "Title": "SMART KNEE BRACE", "Subject Matter": "UTL",
        "Inventors": [{"name": "Wei LIN"}],
        "Correspondence Information": {"Customer Number": 194498},
        "Signature": {"Name": "Yifei Guan", "Registration Number": 82219, "Date": "2025-11-28"},
    }
    opts = {"entity": "small", "spec_pages": "20", "drawing_sheets": "7", "has_poa": True,
            "has_ids": True, "has_ads": True, "has_declaration": True, "declaration_pages": "3",
            "remark": "PPH 加速"}
    out = Path(__file__).resolve().parent.parent / "ads_test_out"
    try:
        print("生成:", generate_transmittal(sample, out, options=opts))
    except FileNotFoundError as e:
        print("[跳过真生成]", e)
