#!/usr/bin/env python3
"""确认函生成包装。

confirmation_sheet_generator.py 为本包内副本（复制自
projects/set_skill/skill-catalog/skills/confirmation-sheet-generator/scripts/，
server 部署不依赖 set_skill 目录树）。
⚠ 修改确认函模板逻辑时需同步两份：本副本 + skill 原件。
"""
import datetime
from pathlib import Path

from .confirmation_sheet_generator import PatentApplicationFormGenerator
from .common import blank_none

# 生成器对第一申请人有硬取键访问，页面编辑/新增的申请人可能缺键 → 统一补默认空值
_APPLICANT_KEYS = (
    "applicant_name_en", "applicant_name_cn", "contact_address_en", "contact_address_cn",
    "contact_address_cn2",
    "address1", "address2", "postcode", "country_en_us", "country_zh_cn",
    "entity_en", "entity_cn", "city_en", "city_cn", "province_city_en_us", "province_city_zh_cn",
)


def _normalize_fields(fields: dict) -> dict:
    fields = blank_none(fields or {})   # 先深度 None→''，任何 null 字段不渲染成 'None'
    normalized = dict(fields)
    normalized["applicants"] = [
        {**{k: "" for k in _APPLICANT_KEYS}, **(a or {})}
        for a in (fields.get("applicants") or [])
    ]
    return normalized


def list_confirmation_rows(fields: dict) -> list:
    """只算确认函各行的 key/标签/值（不产 PDF，仅生成一次性 docx 到临时目录取 row_meta），
    供审核页「标黄设置」面板列出可勾选行。返回 [{key,label,value}]。"""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        gen = PatentApplicationFormGenerator(_normalize_fields(fields), str(Path(td) / "_rows.docx"))
        gen.generate()
        return getattr(gen, "row_meta", [])


def generate_confirmation_sheet(fields: dict, output_dir) -> dict:
    """fields_json → 确认函 docx。

    :return: {"file_path", "file_name", "missing_fields", "missing_optional_fields"}
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    case_volume = fields.get("case_volume") or "UNKNOWN"
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"{date_str}-Application Information Sheet-{case_volume}.docx"
    file_path = output_dir / file_name

    gen = PatentApplicationFormGenerator(_normalize_fields(fields), str(file_path))
    missing_fields, missing_optional_fields = gen.generate()

    return {
        "file_path": str(file_path),
        "file_name": file_name,
        "missing_fields": missing_fields,
        "missing_optional_fields": missing_optional_fields,
        # 各行的 key/标签/值，供审核页「标黄设置」勾选（key=None 的表头行已在生成器里排除）
        "rows": getattr(gen, "row_meta", []),
    }
