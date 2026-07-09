#!/usr/bin/env python3
"""submission_tasks.fields_json → 递交文件生成器(ADS/POA/Transmittal)消费的 case_info。

fields_json schema 见 us_submission/在线审核与文件生成方案.md §2.2（task_type=filing_confirmation）。
case_info 结构对齐三个生成器（ads_generator/poa_generator/transmittal_generator）。

签字代理人 / Customer Number / Deposit Account 不在 fields_json 里（方案 §2.3 列为全局配置），
本函数通过参数 agent_info 注入（来源=全局配置或查 atw.agent_info，由调用方决定），
缺省则 Signature/Correspondence/Representative/Deposit 留空待补。

缺口（fields_json 暂无，留空待后续补）：
- 发明人通信地址 / Residence（schema inventors 只有姓名）
- 图纸页数 Total Number of Drawing Sheets、建议公开图（来自定稿文件）
- Small Entity（可由 applicants.entity_en 推，规则待定）
"""
import datetime
import json
from pathlib import Path

from .common import clean_priority_no, infer_subject_matter

# 签字代理人/Customer Number/Deposit 全局配置（gitignore，本地维护；模板见 agent_config.example.json）
AGENT_CONFIG_PATH = Path(__file__).resolve().parent / "agent_config.json"


def _today():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def load_agent_info(case_volume: str, config_path=None) -> dict:
    """从全局配置 agent_config.json 取签字代理人信息（方案 §2.3）。
    取值：default 为基底，若 by_client 下有该客户代码(案号前5位)条目则覆盖。
    无配置文件时返回 {}（签字块留空，不阻塞生成）。过滤 _ 开头的注释键。"""
    path = Path(config_path or AGENT_CONFIG_PATH)
    if not path.is_file():
        return {}
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[agent_config] 解析失败 {path}: {e}")
        return {}
    base = {k: v for k, v in (cfg.get("default") or {}).items() if not k.startswith("_")}
    code = (case_volume or "")[:5]
    override = (cfg.get("by_client") or {}).get(code)
    if isinstance(override, dict):
        base.update({k: v for k, v in override.items() if not k.startswith("_")})
    return base


def _norm(s):
    return (s or "").strip().lower()


def _inventor_applicant_addr(inv: dict, applicants: list, assignments: list) -> dict:
    """按发明人 employer 取对应申请人的地址（对齐确认函 confirmation_sheet_generator._app_for_employer）。

    无 employer / 单申请人 → applicants[0]；employer 命中申请人英文名 → 该申请人；
    否则前雇主 → assignments.assigning_company 的 company_address（逗号拆 address1/2）。
    :return: 含 address1/address2/city_en/country_en_us/postcode/province_city_en_us 的申请人 dict（或子集）。
    """
    emp = _norm(inv.get("employer"))
    if not emp:
        return applicants[0] if applicants else {}
    for a in applicants:
        if _norm(a.get("applicant_name_en")) == emp:
            return a
    for asg in assignments:
        if _norm(asg.get("assigning_company")) == emp and (asg.get("company_address") or "").strip():
            parts = [p.strip() for p in asg["company_address"].strip().split(",", 1)]
            return {"address1": parts[0], "address2": parts[1] if len(parts) > 1 else ""}
    return applicants[0] if applicants else {}


def fields_to_case_info(fields: dict, agent_info: dict = None) -> dict:
    """把一条 fields_json 映射成 case_info。agent_info 可选（签字人/Customer Number/Deposit）。"""
    fields = fields or {}
    ai = agent_info or {}
    case_meta = fields.get("case_info") or {}
    # 递交特有的可编辑字段（审核页 filing.html 填，存 fields_json.filing_extra）
    extra = fields.get("filing_extra") or {}
    inv_addrs = extra.get("inventor_addresses") or []

    # ── 发明人：姓名来自著录项；居住地/通信地址默认按 employer 取对应申请人地址（同确认函），
    #    filing_extra.inventor_addresses 手填则覆盖 ──
    raw_applicants = fields.get("applicants") or []
    raw_assignments = fields.get("assignments") or []
    inventors = []
    for idx, inv in enumerate(fields.get("inventors") or []):
        first = (inv.get("first_name_en") or "").strip()
        last = (inv.get("last_name_en") or "").strip()
        full = (inv.get("full_name_en") or "").strip() or f"{first} {last}".strip()
        manual = inv_addrs[idx] if idx < len(inv_addrs) else {}
        app = _inventor_applicant_addr(inv, raw_applicants, raw_assignments)
        # 每项：手填优先，否则取该发明人 employer 对应申请人的地址
        def pick(mk, ak):
            return (manual.get(mk) or "").strip() or (app.get(ak) or "").strip()
        res_ctry = pick("residence_country", "country_en_us")
        # ResidencyRadio：参照旧实现——非美国居住地→"non-us-residency"（美国/留空则不选）
        residency = "non-us-residency" if res_ctry and res_ctry.upper() not in ("US", "USA", "UNITED STATES") else ""
        inventors.append({
            "name": full, "firstName": first, "middleName": "", "lastName": last,
            "Residence Information": residency,
            "City": pick("residence_city", "city_en"),
            "Country of Residence": res_ctry,
            "Mailing Address of Inventor address_1": pick("mail_address1", "address1"),
            "Mailing Address of Inventor address_2": pick("mail_address2", "address2"),
            "Mailing Address of Inventor Country": pick("mail_country", "country_en_us"),
            "Mailing Address of Inventor city": pick("mail_city", "city_en"),
            "Mailing Address of Inventor State": pick("mail_state", "province_city_en_us"),
            "Mailing Address of Inventor Postal Code": pick("mail_postcode", "postcode"),
        })

    # ── 申请人块（ADS sfAssigneeInformation；以 assignee 身份列出）──
    applicants = []
    for ap in fields.get("applicants") or []:
        nm = (ap.get("applicant_name_en") or "").strip()
        applicants.append({
            "Name": nm, "Organization Name": nm, "chkOrg": 1, "Assigneebtn": "assignee",
            "Address": ap.get("address1", ""), "Applicant address2": ap.get("address2", ""),
            "Applicant city": ap.get("city_en", ""), "Applicant Postal Code": ap.get("postcode", ""),
            "Nationality": ap.get("country_en_us", ""), "Entity": ap.get("entity_en", ""),
        })

    # ── 非申请人受让人块（ADS sfNonApplicantInfo）──
    # 语义：仅列“不是申请人”的受让人。新 schema 受让人来自 assignments[].assignee，通常 = 某个申请人
    # （已在上面的申请人块以 assignee 身份列出），此时本块应为空——不再镜像 applicants（旧行为会把每个
    # 申请人重复列成非申请人受让人）。仅当某段转让的 assignee 不在申请人名单里（真·非申请人受让人）才列入，
    # 使 ADS 受让人与 Assignment 文件对齐。无 assignments 的存量任务回退旧镜像行为。
    assignees = []
    _assignments = fields.get("assignments") or []
    if _assignments:
        _applicant_keys = {(ap.get("applicant_name_en") or "").strip().lower()
                           for ap in fields.get("applicants") or []}
        _seen = set()
        for asg in _assignments:
            nm = (asg.get("assignee") or "").strip()
            key = nm.lower()
            if not nm or key in _applicant_keys or key in _seen:
                continue
            _seen.add(key)
            # 真·非申请人受让人：schema 无独立地址来源，仅填名称，地址留空待人工补
            assignees.append({
                "Organization Name": nm, "chkOrg": 1,
                "Address 1": "", "Address 2": "", "City": "", "Country": "", "Postal Code": "",
            })
    else:
        for ap in fields.get("applicants") or []:
            nm = (ap.get("applicant_name_en") or "").strip()
            assignees.append({
                "Organization Name": nm, "chkOrg": 1,
                "Address 1": ap.get("address1", ""), "Address 2": ap.get("address2", ""),
                "City": ap.get("city_en", ""), "Country": ap.get("country_en_us", ""),
                "Postal Code": ap.get("postcode", ""),
            })

    # ── 优先权 ──
    priorities = []
    for p in fields.get("priorities") or []:
        priorities.append({
            "Priority": clean_priority_no(p.get("priority_no") or p.get("priority_num") or ""),
            "DAS code": p.get("access_code", ""),
            "Country": p.get("priority_country_id", ""),
            "Priority date": p.get("priority_date", ""),
        })

    subject = fields.get("subject_matter") or infer_subject_matter(fields) or ""

    # 图纸页数复用递交清单的附图页数；Small Entity 由实体派生（small/micro→Yes）
    _opts = fields.get("transmittal_options") or {}
    _entity = (_opts.get("entity") or "").lower()
    small_entity = "Yes" if _entity in ("small", "micro") else ""
    drawing_sheets = _opts.get("drawing_sheets", "") or ""

    case_info = {
        "Our Ref.": fields.get("case_volume", ""),
        "Title": case_meta.get("case_name_en", ""),
        "Inventors": inventors,
        "Applicants": applicants,
        "Assignees": assignees,
        "Parent Applications": fields.get("parent_applications") or [],
        "Priorities": priorities,
        # 顶层 Subject Matter：Transmittal 选模板用
        "Subject Matter": subject,
        "Application Information": {
            "Application Type": "REGULAR",
            "Subject Matter": subject,
            "Small Entity Status Claimed": small_entity,       # 由递交清单实体派生
            "Total Number of Drawing Sheets": drawing_sheets,  # 复用递交清单附图页数
            "Suggested Figure for Publication": "",            # ADS 生成器暂不消费
        },
        "Filing_By_Reference": {"app": "", "date": "", "intellectual": ""},
        # ── agent_info 注入（缺省留空）──
        "Signature": {
            "Name": ai.get("Name", ""), "First Name": ai.get("First Name", ""),
            "Last Name": ai.get("Last Name", ""),
            "Registration Number": ai.get("Registration Number", ""),
            "title": ai.get("title", ""), "Signature": "",
            "Date": ai.get("Date") or _today(),
        },
        "Correspondence Information": {
            "Customer Number": ai.get("Customer Number", ""),
            "Email Address": ai.get("Email Address", []) or [],
        },
        "Representative Information": {"Customer Number": ai.get("Customer Number", "")},
        "Deposit Account No": ai.get("Deposit Account No", ""),
    }
    return case_info


if __name__ == "__main__":
    import json
    sample_fields = {
        "case_volume": "64504-H006US00",
        "case_info": {"case_name_en": "SMART KNEE BRACE"},
        "subject_matter": "UTL",
        "applicants": [{"applicant_name_en": "Mebotx Co.", "address1": "9F Bldg 1B",
                        "address2": "Qinglonggang Rd", "city_en": "Suzhou",
                        "postcode": "215100", "country_en_us": "CN", "entity_en": "Small"}],
        "inventors": [{"full_name_en": "Wei LIN", "first_name_en": "Wei", "last_name_en": "LIN"},
                      {"full_name_en": "Peigen ZHAN", "first_name_en": "Peigen", "last_name_en": "ZHAN"}],
        "priorities": [{"priority_no": "202411284993.X", "access_code": "2951",
                        "priority_country_id": "CN", "priority_date": "2024-09-13"}],
        "parent_applications": [{"Application No": "202411284993", "Filing Date": "September 13, 2024",
                                 "Continuity Type": "Continuation in part of"}],
        "application_type": "发明",
    }
    agent = {"Name": "Yifei Guan", "First Name": "Yifei", "Last Name": "Guan",
             "Registration Number": 82219, "title": "Patent Agent",
             "Customer Number": 194498, "Deposit Account No": "606245",
             "Email Address": ["docketing@x.com"]}
    ci = fields_to_case_info(sample_fields, agent)
    print(json.dumps(ci, ensure_ascii=False, indent=2))
