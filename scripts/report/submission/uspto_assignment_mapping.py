#!/usr/bin/env python3
"""fields_json → USPTO Assignment Center 提交数据（环节7 转让登记自动化的确定性数据层）。

把一条案子的 fields_json 映射成 Assignment Center「新建转让」向导所需的数据结构。
**纯确定性映射（严禁 AI）**，不碰浏览器、不连 USPTO，可离线单测；浏览器驱动脚本
（us_submission/seleTest 的 Playwright 流程）消费本模块产出的 dict 逐字段填表。

数据来源划分：
- **可靠·取自 fields_json**：转让方(个人转公司=发明人 / 公司转公司=转让公司)、
  受让方(assignee，地址匹配申请人)、conveyance 段结构（复用 effective_assignments，
  与 Assignment docx 同一套 employer 分组）。
- **运行期补入·不在确认阶段 fields_json 内**（递交后 / 客户签回件 / 代理所档案才有）：
  - application_numbers：本案 US 申请序列号列表（properties，递交后才有）
  - documents：待上传的签署版 Assignment PDF 路径列表
  - correspondent：代理所联系人档（姓名/地址/电话/邮箱，相对固定）
  - execution_date：转让签署日期（客户签回件上的日期）

一段有效转让 = 一份 Assignment Center submission。缺失的必填项进 `needs` 清单（不编造）。
"""
from .common import effective_assignments, split_address
from .fields_mapping import _norm

# Assignment Center receiving-country 下拉用「国家英文名（大写）」作 label（非 ISO 码），
# 如 CHINA / UNITED STATES；此处只做规范化大写，未知名原样。
_CONVEYANCE_DEFAULT = "Assignment"


def _country_label(v):
    """国家值 → Assignment Center 下拉 label（英文国名大写）。"""
    return (v or "").strip().upper()


def _split_name(full, first="", last=""):
    """取（first, last）：优先用著录项 first/last；否则按空格拆全名（末段为姓）。"""
    first = (first or "").strip()
    last = (last or "").strip()
    if first or last:
        return first, last
    parts = (full or "").strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return " ".join(parts[:-1]), parts[-1]


def _applicant_by_name(fields, name):
    """按名字在 applicants 里匹配（归一化：去空格/大小写/标点），取结构化地址字段。"""
    key = _norm(name)
    for ap in fields.get("applicants") or []:
        if _norm(ap.get("applicant_name_en")) == key:
            return ap
    return {}


def _inventor_by_name(fields, name):
    """按名字在 inventors 里匹配，取 first/last（拿不到时回退全名拆分）。"""
    key = _norm(name)
    for inv in fields.get("inventors") or []:
        full = (inv.get("full_name_en") or "").strip() or \
            f"{(inv.get('first_name_en') or '').strip()} {(inv.get('last_name_en') or '').strip()}".strip()
        if _norm(full) == key or _norm(inv.get("full_name_en")) == key:
            return inv
    return {}


def _entity_address(ap, company_address=""):
    """受让/转让 entity 的结构化地址：优先申请人结构化字段，否则拆 company_address。"""
    if ap:
        return {
            "street": (ap.get("address1") or "").strip(),
            "street2": (ap.get("address2") or "").strip(),
            "city": (ap.get("city_en") or "").strip(),
            "province": (ap.get("province_city_en_us") or "").strip(),
            "postal_code": (ap.get("postcode") or "").strip(),
            "country_label": _country_label(ap.get("country_en_us")),
        }
    a1, a2 = split_address(company_address or "")
    return {"street": a1, "street2": a2, "city": "", "province": "",
            "postal_code": "", "country_label": ""}


def _conveying_parties(fields, seg, execution_date, needs, seg_no):
    """一段转让的转让方列表。个人转公司=发明人逐个(individual)；公司转公司=转让公司(entity)。"""
    a_type = seg.get("assignment_type") or ""
    parties = []
    if a_type == "个人转公司":
        for nm in seg.get("assignor_inventors") or []:
            inv = _inventor_by_name(fields, nm)
            first, last = _split_name(nm, inv.get("first_name_en"), inv.get("last_name_en"))
            if not (first or last):
                needs.append(f"第{seg_no}段：转让人「{nm}」姓名无法拆分")
            parties.append({
                "type": "individual", "firstname": first, "lastname": last,
                "execution_date": execution_date or "",
            })
    else:  # 公司转公司
        company = (seg.get("assigning_company") or "").strip()
        if not company:
            needs.append(f"第{seg_no}段：公司转公司缺转让公司名（assigning_company）")
        ap = _applicant_by_name(fields, company)
        addr = _entity_address(ap, seg.get("company_address") or "")
        parties.append({
            "type": "entity", "entity_name": company,
            "execution_date": execution_date or "", **addr,
        })
    return parties


def _receiving_parties(fields, seg, needs, seg_no):
    """一段转让的受让方（entity）：按 assignee 名匹配申请人取结构化地址。"""
    name = (seg.get("assignee") or "").strip()
    if not name:
        needs.append(f"第{seg_no}段：缺受让人名（assignee）")
    ap = _applicant_by_name(fields, name)
    addr = _entity_address(ap, "")
    if name and not ap:
        needs.append(f"第{seg_no}段：受让人「{name}」未匹配到申请人，地址需人工补")
    return [{"type": "entity", "entity_name": name, **addr}]


def fields_to_assignment_center(fields, *, correspondent=None, application_numbers=None,
                                documents=None, execution_date=None):
    """fields_json → Assignment Center 提交数据（多方/多件/多段）。

    :param fields: submission_tasks.fields_json
    :param correspondent: 代理所联系人档 dict（firstname/lastname/street/city/state_value/
        country_value/zip/phone_type/phone/email）——相对固定，运行期传入
    :param application_numbers: 本案 US 申请序列号列表（properties；递交后才有）
    :param documents: 待上传的签署版 Assignment PDF 路径列表（取自环节3 客户签回件）
    :param execution_date: 转让签署日期（MM/DD/YYYY；客户签回件上的日期）
    :return: {"submissions": [每段一份提交...], "needs": [缺失项...], "warnings": [...]}
    """
    fields = fields or {}
    needs = []
    segments, warnings = effective_assignments(fields)
    if not segments:
        needs.append("无有效转让段（assignments 为空）")

    case_volume = (fields.get("case_volume") or "").strip()
    corr = dict(correspondent or {})
    corr.setdefault("docket_number", case_volume)
    if not correspondent:
        needs.append("缺 correspondent 代理所联系人档（运行期传入）")

    app_nums = [str(a).strip() for a in (application_numbers or []) if str(a).strip()]
    if not app_nums:
        needs.append("缺本案 US 申请序列号（properties；递交后才有，运行期传入）")
    properties = [{"search_by": "applicationNumber", "value": n} for n in app_nums]

    docs = [str(d).strip() for d in (documents or []) if str(d).strip()]
    if not docs:
        needs.append("缺待上传的签署版 Assignment PDF 路径（运行期传入）")

    if not execution_date:
        needs.append("缺转让签署日期 execution_date（客户签回件上的日期）")

    submissions = []
    for i, seg in enumerate(segments, start=1):
        submissions.append({
            "conveyance_type": _CONVEYANCE_DEFAULT,
            "correspondent": corr,
            "conveying_parties": _conveying_parties(fields, seg, execution_date, needs, i),
            "receiving_parties": _receiving_parties(fields, seg, needs, i),
            "properties": properties,
            "documents": docs,
        })

    return {"submissions": submissions, "needs": needs, "warnings": warnings}
