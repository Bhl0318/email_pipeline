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

from .common import clean_priority_no, infer_subject_matter


def _today():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def fields_to_case_info(fields: dict, agent_info: dict = None) -> dict:
    """把一条 fields_json 映射成 case_info。agent_info 可选（签字人/Customer Number/Deposit）。"""
    fields = fields or {}
    ai = agent_info or {}
    case_meta = fields.get("case_info") or {}

    # ── 发明人：fields_json 只有姓名，地址/居住地是缺口（留空）──
    inventors = []
    for inv in fields.get("inventors") or []:
        first = (inv.get("first_name_en") or "").strip()
        last = (inv.get("last_name_en") or "").strip()
        full = (inv.get("full_name_en") or "").strip() or f"{first} {last}".strip()
        inventors.append({
            "name": full, "firstName": first, "middleName": "", "lastName": last,
            "Residence Information": "", "City": "", "Country of Residence": "",
            "Mailing Address of Inventor address_1": "", "Mailing Address of Inventor address_2": "",
            "Mailing Address of Inventor Country": "", "Mailing Address of Inventor city": "",
            "Mailing Address of Inventor State": "", "Mailing Address of Inventor Postal Code": "",
        })

    # ── 申请人 / 受让人（受让人通常=申请人，镜像）──
    applicants, assignees = [], []
    for ap in fields.get("applicants") or []:
        nm = (ap.get("applicant_name_en") or "").strip()
        applicants.append({
            "Name": nm, "Organization Name": nm, "chkOrg": 1, "Assigneebtn": "assignee",
            "Address": ap.get("address1", ""), "Applicant address2": ap.get("address2", ""),
            "Applicant city": ap.get("city_en", ""), "Applicant Postal Code": ap.get("postcode", ""),
            "Nationality": ap.get("country_en_us", ""), "Entity": ap.get("entity_en", ""),
        })
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
            "Small Entity Status Claimed": "",          # 缺口：entity_en→small 规则待定
            "Total Number of Drawing Sheets": "",       # 缺口：来自定稿文件
            "Suggested Figure for Publication": "",
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
