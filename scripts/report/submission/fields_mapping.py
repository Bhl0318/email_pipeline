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
import re
from pathlib import Path

from .common import clean_priority_no, infer_subject_matter, norm_subject_matter, is_371, blank_none

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


# 国家名 → ISO-2 代码（ADS 国家为下拉，需 CN/US 等代码，而非 "China"）
_COUNTRY_CODES = {
    "cn": "CN", "china": "CN", "prchina": "CN", "peoplesrepublicofchina": "CN", "中国": "CN",
    "us": "US", "usa": "US", "unitedstates": "US", "unitedstatesofamerica": "US", "美国": "US",
    "jp": "JP", "japan": "JP", "日本": "JP",
    "kr": "KR", "korea": "KR", "southkorea": "KR", "republicofkorea": "KR",
    "de": "DE", "germany": "DE",
    "gb": "GB", "uk": "GB", "unitedkingdom": "GB",
    "fr": "FR", "france": "FR",
}


_PAREN_CODE_RE = re.compile(r"\(([A-Za-z]{2})\)")


def _country_code(v):
    """国家值规范成 ISO-2 代码（已是两位字母则大写；形如 "…China (CN)" 取括号内代码；
    已知国名转代码；未知原样返回）。"""
    s = (v or "").strip()
    if not s:
        return ""
    if len(s) == 2 and s.isalpha():
        return s.upper()
    # 提取器统一输出「全名 (XX)」，优先取括号内 2 字母代码（如 People's Republic of China (CN) → CN）
    m = _PAREN_CODE_RE.search(s)
    if m:
        return m.group(1).upper()
    key = "".join(ch for ch in s.lower() if ch.isalnum())
    return _COUNTRY_CODES.get(key, s)


# ADS domesContList：对齐旧版(fill_xfa_form)——填下拉的**显示文本**，非代码
_CONTINUITY_DISPLAY = {
    "con": "Continuation of", "continuation": "Continuation of", "continuation of": "Continuation of",
    "div": "Division of", "division": "Division of", "division of": "Division of",
    "divisional": "Division of", "divisional of": "Division of",
    "cip": "Continuation in part of", "continuation in part": "Continuation in part of",
    "continuation in part of": "Continuation in part of",
    "nst": "a 371 of international", "371": "a 371 of international", "371 route": "a 371 of international",
    "a 371 of international": "a 371 of international", "national stage": "a 371 of international",
    "bypass": "Continuation of", "bypass continuation": "Continuation of",  # bypass=365(c) 国际申请的 continuation
    "pro": "Claims benefit of provisional", "provisional": "Claims benefit of provisional",
    "claims benefit of provisional": "Claims benefit of provisional",
    "sub": "substitution of", "substitution": "substitution of", "substitution of": "substitution of",
    "rei": "reissue of", "reissue": "reissue of", "reissue of": "reissue of",
}


def _continuity_display(v):
    """续案关系规范成 ADS domesContList 显示文本（对齐旧版；已知代码/长文转文本；未知原样）。"""
    s = (v or "").strip()
    if not s:
        return ""
    key = " ".join(s.lower().replace("-", " ").split())
    return _CONTINUITY_DISPLAY.get(key, s)


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
        res_ctry = _country_code(pick("residence_country", "country_en_us"))
        _is_us = res_ctry.upper() in ("US", "USA", "UNITED STATES")
        # ResidencyRadio（对齐 ADS 排他组两取值 us-residency / non-us-residency）：
        # 美国居住地→"us-residency"，其他国家→"non-us-residency"，居住国留空则不选。
        residency = "us-residency" if _is_us else ("non-us-residency" if res_ctry else "")
        _res_city = pick("residence_city", "city_en")            # Residence：纯城市
        # 通信地址 City 放「城市, 省份」；State/Province 外国地址留空（该栏是美国州下拉）
        _prov = (app.get("province_city_en_us") or "").strip()
        _mail_city = (manual.get("mail_city") or "").strip() or ", ".join(
            [x for x in [(app.get("city_en") or "").strip(), _prov] if x])
        _mail_state = (manual.get("mail_state") or "").strip()   # 默认留空，不自动填省
        inventors.append({
            "name": full, "firstName": first, "middleName": (inv.get("middle_name") or "").strip(), "lastName": last,
            "Residence Information": residency,
            # 非美国居住块（sfNonUSRes）：仅非美国居住时填，美国居住时留空
            "City": "" if _is_us else _res_city,
            "Country of Residence": "" if _is_us else res_ctry,
            # 美国居住块（sfUSres）：美国居住时填 城市/州/国家（rsCtryTxt 在模板中必填）
            "US Residence City": _res_city if _is_us else "",
            "US Residence State": (_mail_state or _prov) if _is_us else "",
            "US Residence Country": res_ctry if _is_us else "",
            "Mailing Address of Inventor address_1": pick("mail_address1", "address1"),
            "Mailing Address of Inventor address_2": pick("mail_address2", "address2"),
            "Mailing Address of Inventor Country": _country_code(pick("mail_country", "country_en_us")),
            "Mailing Address of Inventor city": _mail_city,       # 城市, 省份
            "Mailing Address of Inventor State": _mail_state,     # 外国留空
            "Mailing Address of Inventor Postal Code": pick("mail_postcode", "postcode"),
        })

    # ── 申请人块（ADS sfAssigneeInformation；以 assignee 身份列出）──
    applicants = []
    for ap in fields.get("applicants") or []:
        nm = (ap.get("applicant_name_en") or "").strip()
        _ap_city = ", ".join([x for x in [(ap.get("city_en") or "").strip(),
                                          (ap.get("province_city_en_us") or "").strip()] if x])
        applicants.append({
            "Name": nm, "Organization Name": nm, "chkOrg": 1, "Assigneebtn": "assignee",
            "Address": ap.get("address1", ""), "Applicant address2": ap.get("address2", ""),
            "Applicant city": _ap_city,   # 城市, 省（外国地址 State 留空）
            "Applicant Postal Code": ap.get("postcode", ""),
            "Nationality": _country_code(ap.get("country_en_us", "")), "Entity": ap.get("entity_en", ""),
        })

    # ── 受让人块（ADS sfNonApplicantInfo：Assignee Information incl Non-Applicant）──
    # 对齐旧版：列出所有转让的受让人公司（受让人=申请人也列出，用于公开署名）；地址取同名申请人，
    # 否则 assignments.company_address 兜底。无 assignments 的存量任务→镜像申请人。City 放「城市, 省份」。
    def _assignee_entry(nm, ap, company_address=""):
        prov = (ap.get("province_city_en_us") or "").strip()
        city = ", ".join([x for x in [(ap.get("city_en") or "").strip(), prov] if x])
        ca_parts = [p.strip() for p in company_address.split(",", 1)] if company_address else []
        return {
            "Organization Name": nm, "chkOrg": 1,
            "Address 1": ap.get("address1", "") or (ca_parts[0] if ca_parts else ""),
            "Address 2": ap.get("address2", "") or (ca_parts[1] if len(ca_parts) > 1 else ""),
            "City": city,
            "Country": _country_code(ap.get("country_en_us", "")),
            "Postal Code": ap.get("postcode", ""),
        }

    assignees = []
    _assignments = fields.get("assignments") or []
    _raw_apps = fields.get("applicants") or []

    def _nkey(s):
        return "".join(ch for ch in (s or "").lower() if ch.isalnum())
    _app_by_name = {(ap.get("applicant_name_en") or "").strip().lower(): ap for ap in _raw_apps}
    _app_by_nkey = {_nkey(ap.get("applicant_name_en")): ap for ap in _raw_apps}

    def _app_for_assignee(nm):
        """受让人取对应申请人地址：先精确名、再去标点/大小写归一名匹配；
        仍不中（含中英译名差异，如 Cytoderm/Cell Wall）时——**单一申请人**→用其地址兜底。"""
        ap = _app_by_name.get((nm or "").strip().lower()) or _app_by_nkey.get(_nkey(nm))
        if ap:
            return ap
        return _raw_apps[0] if len(_raw_apps) == 1 else {}

    def _assignee_is_applicant(nm):
        """受让人是否即申请人：名字匹配任一申请人，或单一申请人（个人/公司转公司受让人即该申请人）。
        与确认函(AIS 只列 Applicant、不单列受让人)一致——是申请人就不在 ADS Non-Applicant Assignee 重复列。"""
        if _app_by_name.get((nm or "").strip().lower()) or _app_by_nkey.get(_nkey(nm)):
            return True
        return len(_raw_apps) == 1

    # ADS「Assignee Information Including Non-Applicant Assignee Information」段(sfNonApplicantInfo)：
    # 主要登【申请人作为受让人】——用**申请人自己的名字+地址**（不用 assignments 里可能异名的受让人名，
    # 如 Cytoderm/Cell Wall）；若有**确实非申请人**的受让人再追加（多申请人场景）。
    _seen = set()
    for ap in _raw_apps:                                    # 1) 申请人作为受让人（申请人名+地址）
        nm = (ap.get("applicant_name_en") or "").strip()
        if nm and nm.lower() not in _seen:
            _seen.add(nm.lower())
            assignees.append(_assignee_entry(nm, ap))
    for asg in _assignments:                                # 2) 真·非申请人受让人才追加
        nm = (asg.get("assignee") or "").strip()
        if not nm or nm.lower() in _seen:
            continue
        if _assignee_is_applicant(nm):                      # 是申请人 → 已按申请人名登过，跳过其异名
            continue
        _seen.add(nm.lower())
        assignees.append(_assignee_entry(nm, _app_for_assignee(nm), asg.get("company_address", "")))

    # ── 优先权 ──
    priorities = []
    for p in fields.get("priorities") or []:
        priorities.append({
            "Priority": clean_priority_no(p.get("priority_no") or p.get("priority_num") or ""),
            "DAS code": p.get("access_code", ""),
            "Country": p.get("priority_country_id", ""),
            "Priority date": p.get("priority_date", ""),
        })

    # 申请类型归一到 Utility/Plant/Design（与 ADS 一致）；371 单独作落地方式标记供 Transmittal 选模板
    subject = norm_subject_matter(fields.get("subject_matter") or infer_subject_matter(fields))
    subject_is_371 = is_371(fields)

    # 图纸页数复用递交清单的附图页数；Small Entity 由实体派生（small/micro→Yes）
    _opts = fields.get("transmittal_options") or {}
    _entity = (_opts.get("entity") or "").lower()
    # ADS chkSmallEntity 是 XFA 整数复选框（items 1/0/2，1=已声明小实体），须填整数 "1"/"0"，非 "Yes"
    small_entity = "1" if _entity in ("small", "micro") else "0"
    drawing_sheets = _opts.get("drawing_sheets", "") or ""

    # Domestic Benefit / National Stage：parent_applications 的 Continuity Type 规范成代码。
    #   每段一行「本段申请号(This App) 是 在先号(Prior) 的 [续案类型]」：
    #     Application No(This App) = 该行「较晚一件」的号（子案）；首段=本申请→空。
    #     Prior Application Number = 该行在先号（父案）。
    #   本段申请号优先取源行自带的 Application No（filing.html 可编辑）；
    #   源行未填时才回落线性链推 = 上一段的在先号（单链家族适用，分叉家族会错→需人工在页面上填）。
    parents = []
    _prev_no = ""   # 链推游标：上一段的在先号（首段=空）
    for p in fields.get("parent_applications") or []:
        prior_no = (p.get("Prior Application Number") or "").strip()
        this_app = (p.get("Application No") or "").strip() or _prev_no  # 源行自带优先，否则链推
        parents.append({
            "Application No": this_app,                   # 本段申请号(This App)：源行自带优先
            "Prior Application Number": prior_no,        # 本段在先号(父案) → Prior Application Number
            "Filing Date": p.get("Filing Date", ""),
            "Continuity Type": _continuity_display(p.get("Continuity Type")),
            "Prior Application Status": (p.get("Prior Application Status") or "").strip() or "Pending",
            "Patent Number": (p.get("Patent Number") or "").strip(),   # Patented 时用（专利块）
            "Issue Date": (p.get("Issue Date") or "").strip(),
        })
        _prev_no = prior_no                              # 下一段 Application Number = 本段母案号
    _route = _norm(fields.get("filing_route"))
    _pct = fields.get("case_advance_info") or {}
    _pct_no = (_pct.get("pct_app_no") or "").strip()
    if _pct_no:
        # PCT 作为域内优先权链的“最后一段”接上（不再与美国母案互斥）：
        #   Application No = 链上一段（最后一个美国母案）的在先号；无母案时=空(本申请)；Prior=PCT 号。
        # 续案类型：有美国母案链时，底层美国案基本就是 PCT 的 371 国家阶段 → 固定 "a 371 of international"；
        #   无母案时按 filing_route 推（含 371→371 国际阶段；否则续案词/bypass→Continuation of）。
        _pct_date = (_pct.get("pct_app_date") or "").strip()
        if parents:
            _ct = "a 371 of international"
        else:
            _ct = "a 371 of international" if "371" in _route else (_continuity_display(_route) or "Continuation of")
        parents.append({"Application No": _prev_no, "Prior Application Number": _pct_no,
                        "Filing Date": _pct_date, "Continuity Type": _ct,
                        "Prior Application Status": "Pending",
                        "Patent Number": "", "Issue Date": ""})
        _prev_no = _pct_no

    case_info = {
        "Our Ref.": fields.get("case_volume", ""),
        # 申请名称（invention-title）US 递交要求全部大写（ADS/Transmittal 用此 Title）
        "Title": (case_meta.get("case_name_en") or "").upper(),
        "Inventors": inventors,
        "Applicants": applicants,
        "Assignees": assignees,
        "Parent Applications": parents,
        "Priorities": priorities,
        # 顶层 Subject Matter（Utility/Plant/Design）+ 371 标记：Transmittal 选模板用
        "Subject Matter": subject,
        "Is 371": subject_is_371,
        "Application Information": {
            "Application Type": "REGULAR",
            # ADS us_submission_type 要模板枚举代码(UTL/DES/PLT)，对齐老流程(fill_xfa_form 喂 "UTL")；
            # 写全称 "Utility" 会被 Patent Center 判"subject matter 不符"拒收(371 utility 也是 UTL)。
            "Subject Matter": {"Utility": "UTL", "Design": "DES", "Plant": "PLT"}.get(subject, "UTL"),
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
    return blank_none(case_info)   # 深度 None→''，ADS/POA/Transmittal 不出现字面 'None'


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
