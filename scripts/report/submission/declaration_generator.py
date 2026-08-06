#!/usr/bin/env python3
"""Declaration PDF 生成（消费 fields_json，移植自 old_submission/assignment/func_normal_form.py）。

每位发明人一页，合并为一份多页 PDF；模板按特例客户清单选择：
- 特例客户（20618 类）→ DECLARATION_en.pdf（英文版，含 PCT 勾选与申请号/日期栏）
- 其余 → DECLARATION_encn.pdf（中英对照版，Text16-28 + Check Box17/18）
"""
from datetime import datetime
from pathlib import Path

import fitz  # PyMuPDF

from .common import (
    DECLARATION_EN_TEMPLATE,
    DECLARATION_ENCN_TEMPLATE,
    inventor_names,
    is_special_client,
)


def _fill_pdf_form(template_path: Path, output_path: Path, field_updates: dict) -> None:
    """填写 PDF 表单字段（行为对齐旧 PDFFormHandler.update_pdf_form_field）。"""
    doc = fitz.open(str(template_path))
    doc.need_appearances(False)
    for page in doc:
        widgets = page.widgets()
        if not widgets:
            continue
        for field in widgets:
            if field.field_name in field_updates:
                if field.field_type == 2:  # checkbox
                    field.field_value = "Yes"
                else:
                    field.field_value = str(field_updates[field.field_name])
                field.update()
    doc.save(str(output_path))
    doc.close()


def _build_field_dict(special: bool, title: str, inventor: str,
                      pct_app_no: str, pct_app_date: str,
                      force_attached: bool = False) -> tuple:
    """按模板版本组装字段字典，返回 (模板路径, 字段字典)。

    force_attached=True（Paris / CIP 落地）时，"This declaration is directed to:" 勾第一项
    "随附的申请（the attached application）"；否则勾第二项，引用在先 PCT/美国申请号。
    """
    is_pct = not force_attached
    if special:
        check_box = (
            {"undefined": "On",
             "United States application or PCT international application number": pct_app_no,
             "filed on": pct_app_date}
            if is_pct else {"This declaration": "On"}
        )
        fields = {
            "Title of Invention": title,
            "Date Optional": "",
            "Inventor": inventor,
            "Text1": "",
            **check_box,
        }
        return DECLARATION_EN_TEMPLATE, fields

    check_box = (
        {"Check Box18": "Yes", "Text19": pct_app_no, "Text20": pct_app_date}
        if is_pct else {"Check Box17": "Yes"}
    )
    fields = {
        "Text16": title,
        "Text21": "", "Text22": "",
        "Text23": inventor,
        "Text24": "", "Text25": "", "Text26": "", "Text27": "", "Text28": "",
        **check_box,
    }
    return DECLARATION_ENCN_TEMPLATE, fields


def generate_declarations(fields: dict, output_dir) -> list:
    """生成 Declaration：每位发明人一页，合并为一份多页 PDF（USPTO 每人各签一页）。

    :param fields: submission_tasks.fields_json
    :param output_dir: 输出目录
    :return: [{"file_path", "file_name", "inventors": [...]}]（单元素列表，调用方按列表处理）
    """
    case_volume = fields.get("case_volume") or ""
    title = ((fields.get("case_info") or {}).get("case_name_en") or "").upper()  # 申请名称全部大写
    advance = fields.get("case_advance_info") or {}
    pct_app_no = (advance.get("pct_app_no") or "").strip()
    pct_app_date = (advance.get("pct_app_date") or "").strip()
    # Declaration "This declaration is directed to:"：
    #   落地方式为 Paris（巴黎公约）或 CIP（Continuation in part of）→ 勾第一项"随附的申请"；
    #   其余（371 / bypass / Continuation of / Division 等）→ 勾第二项，引用在先 PCT/美国申请号。
    _route = (fields.get("filing_route") or "").strip().lower()
    force_attached = ("paris" in _route) or ("continuation in part" in _route) or ("cip" in _route)
    names = inventor_names(fields)
    if not names:
        raise ValueError("发明人列表为空，无法生成 Declaration")

    special = is_special_client(case_volume)
    template_path, _ = _build_field_dict(special, title, "", pct_app_no, pct_app_date, force_attached)
    if not template_path.exists():
        raise RuntimeError(f"缺少模板 {template_path}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 逐位发明人填一页 → 合并为一份多页 PDF（每页一位）
    merged = fitz.open()
    try:
        for idx, inventor in enumerate(names):
            template_path, field_dict = _build_field_dict(special, title, inventor, pct_app_no, pct_app_date, force_attached)
            tmp_path = output_dir / f".decl_tmp_{idx}.pdf"
            _fill_pdf_form(template_path, tmp_path, field_dict)
            with fitz.open(str(tmp_path)) as one:
                merged.insert_pdf(one)
            tmp_path.unlink()
        file_name = f"{today_str}-Declaration-{case_volume}.pdf"
        file_path = output_dir / file_name
        merged.save(str(file_path))
    finally:
        merged.close()
    return [{"file_path": str(file_path), "file_name": file_name, "inventors": names}]
