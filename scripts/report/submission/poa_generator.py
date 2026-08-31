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
import re
from pathlib import Path

import fitz  # PyMuPDF

from .common import POA_TEMPLATE, fill_pdf_form


def _append_scan_page(poa_pdf: Path, scan_pdf: Path) -> None:
    """把扫描件 PDF 追加到 POA 之后（作为第二页起），本地完成、数据不出本机。
    保留 POA 表单页已填字段（整份重存一次）。"""
    tmp = poa_pdf.with_suffix(poa_pdf.suffix + ".tmp")
    doc = fitz.open(str(poa_pdf))
    scan = fitz.open(str(scan_pdf))
    try:
        doc.insert_pdf(scan)
        doc.save(str(tmp))
    finally:
        doc.close()
        scan.close()
    tmp.replace(poa_pdf)


def generate_poa(case_info: dict, output_dir, template_pdf=None, scan_pdf=None) -> dict:
    """生成 POA PDF。scan_pdf 给定则追加为第二页（人工上传的扫描件）。
    :return: {"file_path", "file_name", "type"}"""
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
        "Name": sig.get("Name", ""),
        "Registration Number": str(sig.get("Registration Number", "")),
        "Title if Applicant is a juristic entity": sig.get("title", ""),
        "Applicant Name if Applicant is a juristic entity": applicants[0].get("Name", ""),
        # "*Total of ___ forms are submitted." 默认勾选、份数填 1
        "Number of forms being submitted": True,   # checkbox：出现即勾选（fill_pdf_form 置 Yes）
        "Number of forms": "1",
    }

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    ref = case_info.get("Our Ref.", "UNKNOWN")
    file_name = f"{today}-POA-{ref}.pdf"
    file_path = output_dir / file_name
    fill_pdf_form(template_pdf, file_path, field_updates)
    if scan_pdf and Path(scan_pdf).is_file():
        _append_scan_page(file_path, Path(scan_pdf))
    return {"file_path": str(file_path), "file_name": file_name, "type": "POA"}


def _safe_appname(name, idx):
    """申请人名清洗成安全文件名片段；空则用 applicantN。"""
    s = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", (name or "").strip())
    s = re.sub(r"\s+", " ", s).strip().strip(".")[:40]
    return s or f"applicant{idx + 1}"


def generate_poas(case_info: dict, output_dir, template_pdf=None, scan_paths=None) -> list:
    """每个申请人各生成一份 POA（各填各的申请人名、各附各的扫描页）。
    scan_paths: {申请人下标: 扫描件路径}（缺则该份不附扫描页）。
    文件名：单申请人 {日期}-POA-{案号}.pdf（兼容原命名）；多申请人 {日期}-POA-{案号}-{申请人名}.pdf。
    :return: [{"file_path","file_name","type","applicant","index"} ...]（至少一份）。"""
    template_pdf = template_pdf or POA_TEMPLATE
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sig = case_info.get("Signature", {})
    inventors = case_info.get("Inventors") or [{}]
    applicants = case_info.get("Applicants") or [{}]
    scan_paths = scan_paths or {}
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    ref = case_info.get("Our Ref.", "UNKNOWN")
    multi = len(applicants) > 1
    out = []
    for i, app in enumerate(applicants):
        field_updates = {
            "First Named Inventor": inventors[0].get("name", ""),
            "Title": case_info.get("Title", ""),
            "Attorney Docket Number": case_info.get("Our Ref.", ""),
            "Name": sig.get("Name", ""),
            "Registration Number": str(sig.get("Registration Number", "")),
            "Title if Applicant is a juristic entity": sig.get("title", ""),
            "Applicant Name if Applicant is a juristic entity": app.get("Name", ""),  # 各填各的申请人
            "Number of forms being submitted": True,
            "Number of forms": "1",
        }
        suffix = f"-{_safe_appname(app.get('Name'), i)}" if multi else ""   # 单申请人保持原名
        file_name = f"{today}-POA-{ref}{suffix}.pdf"
        file_path = output_dir / file_name
        fill_pdf_form(template_pdf, file_path, field_updates)
        scan = scan_paths.get(i)
        if scan and Path(scan).is_file():
            _append_scan_page(file_path, Path(scan))   # 该申请人各自的扫描页
        out.append({"file_path": str(file_path), "file_name": file_name, "type": "POA",
                    "applicant": app.get("Name", ""), "index": i})
    return out


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
