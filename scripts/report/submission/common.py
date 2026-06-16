#!/usr/bin/env python3
"""US 递交文档生成：共享常量与字段加工。

输入统一为 submission_tasks.fields_json（schema 见 us_submission/在线审核与文件生成方案.md 2.2），
字段加工函数只读 fields、不做网络/数据库访问；另提供本地 PDF AcroForm 填表工具
fill_pdf_form（仅本地文件 I/O，供 POA/Transmittal 等生成器共用）。
"""
import re
from pathlib import Path

import fitz  # PyMuPDF

# 模板自包含在本包内（部署单元是汇报信流程目录，不依赖仓库其他路径）
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

ASSIGNMENT_TEMPLATE = TEMPLATES_DIR / "Assignment.docx"
DECLARATION_EN_TEMPLATE = TEMPLATES_DIR / "DECLARATION_en.pdf"
DECLARATION_ENCN_TEMPLATE = TEMPLATES_DIR / "DECLARATION_encn.pdf"
ADS_TEMPLATE = TEMPLATES_DIR / "ADS.pdf"  # USPTO ADS 空 XFA 表单
POA_TEMPLATE = TEMPLATES_DIR / "POA.pdf"
TRANSMITTAL_TEMPLATE = TEMPLATES_DIR / "Transmittal.pdf"            # UTL
TRANSMITTAL_DESIGN_TEMPLATE = TEMPLATES_DIR / "Design-Transmittal.pdf"  # DES
TRANSMITTAL_371_TEMPLATE = TEMPLATES_DIR / "371-Transmittal.pdf"    # 其他(371)
# 注：POA / Transmittal 三件空表单模板需放入 submission/templates/（同 ADS，从旧机取回）


def fill_pdf_form(template_pdf, output_pdf, field_updates: dict) -> None:
    """填写 PDF AcroForm 表单字段（PyMuPDF，本地，移植自旧 PDFFormHandler.update_pdf_form_field）。
    checkbox(field_type==2) 命中即勾选 'Yes'，其余按字符串写入；非表单字段名忽略。"""
    template_pdf = Path(template_pdf)
    if not template_pdf.is_file():
        raise FileNotFoundError(f"PDF 模板不存在: {template_pdf}（需放入 submission/templates/）")
    doc = fitz.open(str(template_pdf))
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
    doc.save(str(output_pdf))
    doc.close()

# 特例客户清单（方案 2.3 全局配置）：方案号前缀命中 → Declaration 用英文版模板、
# Assignment 公司转公司时保留受让人签字页
SPECIAL_CLIENT_PREFIXES = ("20618",)

ASSIGNMENT_TYPES = ("个人转公司", "公司转公司")


def is_special_client(case_volume: str) -> bool:
    return bool(case_volume) and case_volume.startswith(SPECIAL_CLIENT_PREFIXES)


def format_inventor_name(inventor: dict) -> str:
    """库著录项发明人 → Assignment/Declaration 用的 "姓大写, 名" 格式。

    姓全部大写；名保持库中规范值（含数字/非纯字母时不动）。
    last/first 拆分缺失时回退 full_name_en。
    """
    last = (inventor.get("last_name_en") or "").strip()
    first = (inventor.get("first_name_en") or "").strip()
    if last and first:
        return f"{last.upper()}, {first}"
    return (inventor.get("full_name_en") or "").strip()


def inventor_names(fields: dict) -> list:
    return [n for n in (format_inventor_name(i) for i in fields.get("inventors") or []) if n]


def clean_priority_no(priority_no: str) -> str:
    """优先权号只留数字和点（对齐旧流程规则：去掉国别字母等）。"""
    return re.sub(r"[^0-9.]", "", priority_no or "")


def split_address(raw: str) -> list:
    """地址按逗号拆两行（与旧 split_assignee_address 行为一致）。"""
    parts = [p.strip() for p in re.split(r"[，,]", raw or "") if p.strip()]
    if parts:
        return [parts[0], ", ".join(parts[1:])]
    return ["", ""]


# 地址1单行不折行的估算字符上限（地址格宽约3.05英寸/12pt）。
# 纯估算（比例字体无法精确），偏长折行就调小此值。
ADDRESS_LINE1_MAX = 50


def rebalance_address(addr1: str, addr2: str, width: int = ADDRESS_LINE1_MAX) -> tuple:
    """地址1超 width 时，从末尾逐段（按逗号）挪到地址2前面，直到地址1不超长。

    仅按标点（逗号）拆；无逗号可拆时保持原样（交单元格自动换行）。
    """
    addr1, addr2 = (addr1 or "").strip(), (addr2 or "").strip()
    if len(addr1) <= width:
        return addr1, addr2
    parts = [p.strip() for p in re.split(r"[，,]", addr1) if p.strip()]
    if len(parts) <= 1:
        return addr1, addr2  # 无标点可拆
    moved = []
    while len(parts) > 1 and len(", ".join(parts)) > width:
        moved.insert(0, parts.pop())
    new_addr1 = ", ".join(parts)
    tail = ", ".join(moved)
    new_addr2 = (tail + ", " + addr2) if (tail and addr2) else (tail or addr2)
    return new_addr1, new_addr2


def address_lines(addr1: str, addr2: str, width: int = ADDRESS_LINE1_MAX) -> list:
    """按 width 把地址拆成多行列表：地址1 溢出挪到地址2，地址2 再溢出挪到地址3…

    尊重已有 addr1/addr2 边界，只把超长行的尾段（按逗号）下移；无逗号不拆。
    返回非空行列表（至少 1 行）。
    """
    a1, a2 = rebalance_address(addr1, addr2, width)
    lines = [a1]
    rest = a2
    while rest and len(rest) > width:
        parts = [p.strip() for p in re.split(r"[，,]", rest) if p.strip()]
        if len(parts) <= 1:
            break  # 无逗号可拆，整段留在当前行
        cur = parts[0]
        idx = 1
        while idx < len(parts) and len(cur + ", " + parts[idx]) <= width:
            cur += ", " + parts[idx]
            idx += 1
        lines.append(cur)
        rest = ", ".join(parts[idx:])
    if rest:
        lines.append(rest)
    return [ln for ln in lines if ln] or [""]


def full_mailing_address_en(applicant: dict) -> str:
    """完整英文通信地址：address1 + address2 + 城市 + 州省 + 邮编 + 国家 拼接。

    与确认函 Mailing Address 的合并口径完全一致，保证 Assignment 与确认函显示同一地址。
    """
    parts = [
        applicant.get("address1", ""), applicant.get("address2", ""),
        applicant.get("city_en", ""), applicant.get("province_city_en_us", ""),
        applicant.get("postcode", ""), applicant.get("country_en_us", ""),
    ]
    return ", ".join([str(p).strip() for p in parts if p and str(p).strip()])


def get_assignee(fields: dict) -> dict:
    """受让人（申请人第一位）：名称 + 完整通信地址（与确认函一致）。

    地址取 full_mailing_address_en（六字段拼接），再按 40 字拆行：
    - address1/address2：两行版（供 _replace_everywhere 路径，如 20618 受让公司）
    - address_lines：多行版（发明人签字表用，超 2 行时克隆地址行）
    """
    applicants = fields.get("applicants") or []
    first = applicants[0] if applicants else {}
    name = (first.get("applicant_name_en") or "").strip()
    full_en = full_mailing_address_en(first)
    if not full_en:
        full_en = (first.get("contact_address_en") or "").strip()
    lines = address_lines(full_en, "")
    bal1, bal2 = rebalance_address(full_en, "")
    return {"name": name, "address1": bal1, "address2": bal2, "address_lines": lines}


def application_type_words(application_type: str) -> tuple:
    """申请类型 → (app_type_eng, confirm_type)；非枚举值返回空（缺失由审核页挡）。"""
    if application_type == "发明":
        return "invention", "an invention"
    if application_type == "外观":
        return "design", "a design"
    return "", ""


def validate_for_confirm(fields: dict) -> list:
    """confirm 前的硬校验（方案 4.3）：返回问题清单，空列表=通过。

    确认函自身的必填字段由其生成器校验（missing_fields），此处补齐
    生成器覆盖不到的：申请类型、转让安排及公司转公司四件套。
    """
    problems = []
    if (fields.get("application_type") or "") not in ("发明", "外观"):
        problems.append("申请类型（application_type）缺失或非法，须为：发明 / 外观")

    assignments = fields.get("assignments") or []
    if not assignments:
        problems.append("转让安排（assignments）为空，至少需要一段转让")
    for idx, item in enumerate(assignments, start=1):
        a_type = item.get("assignment_type") or ""
        if a_type not in ASSIGNMENT_TYPES:
            problems.append(f"转让安排第{idx}段类型非法：{a_type!r}")
            continue
        if a_type == "公司转公司":
            labels = {
                "assigning_company": "转让方公司名称",
                "company_representative": "签字代表姓名",
                "representative_title": "代表职位",
                "company_address": "公司地址",
            }
            for key, label in labels.items():
                if not (item.get(key) or "").strip():
                    problems.append(f"转让安排第{idx}段（公司转公司）缺少{label}（{key}）")

    if not fields.get("inventors"):
        problems.append("发明人列表为空")
    if not fields.get("applicants"):
        problems.append("申请人列表为空")
    return problems


def normalize_parents(fields: dict) -> dict:
    """母案键归一为约定键 "Application No"/"Filing Date"/"Continuity Type"。

    兼容存量任务：早期 finalize 未做 key 转换，库里可能是小写 application_no/filing_date。
    幂等，可重复调用。
    """
    fields["parent_applications"] = [
        {
            "Application No": (p or {}).get("Application No") or (p or {}).get("application_no") or "",
            "Filing Date": (p or {}).get("Filing Date") or (p or {}).get("filing_date") or "",
            "Continuity Type": (p or {}).get("Continuity Type") or (p or {}).get("continuity_type") or "",
        }
        for p in (fields.get("parent_applications") or [])
    ]
    return fields


def infer_subject_matter(fields: dict) -> str:
    """推断 Subject Matter（UTL/DES/371），审核页可改（方案 2.2 来源3）。

    规则：外观 → DES；落地方式/业务类型含 371 或 PCT国家阶段 → 371；其余 → UTL。
    """
    if fields.get("subject_matter"):
        return fields["subject_matter"]
    if (fields.get("application_type") or "") == "外观":
        return "DES"
    route = (fields.get("filing_route") or "") + (fields.get("business_type_zh_cn") or "")
    if "371" in route or "国家阶段" in route:
        return "371"
    return "UTL"


def build_priority_rows(fields: dict) -> list:
    """Assignment 优先权表数据行：优先权 + PCT + 美国直接母案（仅链上第一项）。

    对齐旧流程：旧确认函 "US Patent Application" 栏只记直接母案单值，
    Assignment 表从不列祖辈链；完整延续链只进确认函的母案区。
    每行 (application_number, country, filing_date)，与模板表列序一致。
    """
    rows = []
    for p in fields.get("priorities") or []:
        no = clean_priority_no(p.get("priority_no") or p.get("priority_num") or "")
        if no:
            rows.append((no, p.get("priority_country_id") or "", p.get("priority_date") or ""))

    advance = fields.get("case_advance_info") or {}
    pct_no = (advance.get("pct_app_no") or "").strip()
    if pct_no:
        m = re.search(r"PCT/([A-Z]{2})", pct_no.upper())
        rows.append((pct_no, m.group(1) if m else "PCT", advance.get("pct_app_date") or ""))

    parents = fields.get("parent_applications") or []
    if parents:
        first = parents[0] or {}
        app_no = (first.get("Application No") or first.get("application_no") or "").strip()
        if app_no:
            rows.append((app_no, "US", first.get("Filing Date") or first.get("filing_date") or ""))
    return rows
