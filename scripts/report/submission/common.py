#!/usr/bin/env python3
"""US 递交文档生成：共享常量与字段加工。

输入统一为 submission_tasks.fields_json（schema 见 us_submission/在线审核与文件生成方案.md 2.2），
字段加工函数只读 fields、不做网络/数据库访问；另提供本地 PDF AcroForm 填表工具
fill_pdf_form（仅本地文件 I/O，供 POA/Transmittal 等生成器共用）。
"""
import os
import re
from pathlib import Path

import fitz  # PyMuPDF

# 模板自包含在本包内（部署单元是汇报信流程目录，不依赖仓库其他路径）
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# pdfRest 表单扁平化（仅用于把动态 XFA 渲染成静态 PDF 供在线浏览；可被环境变量覆盖）
PDFREST_FLATTEN_URL = os.environ.get("PDFREST_FLATTEN_URL", "https://api.pdfrest.com/flattened-forms-pdf")
PDFREST_API_KEY = os.environ.get("PDFREST_API_KEY", "4b177438-f97c-4a4f-b0d1-ee91bea77b80")

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


def flatten_pdf(input_pdf, output_pdf, timeout: int = 60) -> str:
    """把含表单/动态 XFA 的 PDF 扁平化成静态 PDF（pdfRest flattened-forms-pdf 云端）。

    ⚠️ 会把文件上传到 pdfRest 服务器——仅用于在线浏览版（动态 XFA 浏览器/LibreOffice
    渲染不出，必须靠带 XFA 排版引擎的服务扁平化）；正式递交/发送仍用本地注入的 XFA 版。
    需要 requests + requests_toolbelt（见 requirements.txt）。
    成功返回 output_pdf 路径字符串；失败抛异常由调用方决定回退。"""
    import requests
    from requests_toolbelt import MultipartEncoder

    input_pdf = Path(input_pdf)
    if not input_pdf.is_file():
        raise FileNotFoundError(f"待扁平化文件不存在: {input_pdf}")
    with open(input_pdf, "rb") as f:
        enc = MultipartEncoder(fields={
            "file": (input_pdf.name, f, "application/pdf"),
            "output": "flattened",
        })
        resp = requests.post(
            PDFREST_FLATTEN_URL, data=enc,
            headers={"Accept": "application/json", "Api-Key": PDFREST_API_KEY,
                     "Content-Type": enc.content_type},
            timeout=timeout)
    if not resp.ok:
        raise RuntimeError(f"pdfRest 扁平化失败 HTTP {resp.status_code}: {resp.text[:200]}")
    out_url = (resp.json() or {}).get("outputUrl")
    if not out_url:
        raise RuntimeError("pdfRest 响应缺 outputUrl")
    dl = requests.get(out_url, timeout=timeout)
    if not dl.ok:
        raise RuntimeError(f"pdfRest 结果下载失败 HTTP {dl.status_code}")
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    output_pdf.write_bytes(dl.content)
    return str(output_pdf)


# 特例客户清单（方案 2.3 全局配置）：方案号前缀命中 → Declaration 用英文版模板、
# Assignment 公司转公司时保留受让人签字页
SPECIAL_CLIENT_PREFIXES = ("20618",)

ASSIGNMENT_TYPES = ("个人转公司", "公司转公司")


def is_special_client(case_volume: str) -> bool:
    return bool(case_volume) and case_volume.startswith(SPECIAL_CLIENT_PREFIXES)


def blank_none(obj):
    """深度把 None 转成 ''（dict/list 递归），避免生成文档里出现字面 'None'
    （某字段值为 null 被 f-string/替换/cell.text 渲染成 'None'）。非 None 标量原样返回。"""
    if obj is None:
        return ""
    if isinstance(obj, dict):
        return {k: blank_none(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [blank_none(v) for v in obj]
    return obj


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
    """优先权号只留数字、点和校验位 X（去掉国别字母/空格等）。
    CN 申请号末位校验位可能是 X（如 202511948961.X），不能当国别字母删掉。"""
    return re.sub(r"[^0-9.Xx]", "", priority_no or "")


def split_address(raw: str) -> list:
    """地址按逗号拆两行（与旧 split_assignee_address 行为一致）。"""
    parts = [p.strip() for p in re.split(r"[，,]", raw or "") if p.strip()]
    if parts:
        return [parts[0], ", ".join(parts[1:])]
    return ["", ""]


def parse_address_en(raw: str) -> dict:
    """把一整串英文地址启发式拆成结构化字段（供前端「粘贴完整地址→识别填充」，结果需人工复核）。
    规则：逗号拆段 → 末段=国家；剩余末段含 5-6 位数字则拆出邮编（与城市同段如 'Beijing 100142'
    则城市取余下，否则邮编独立成段、城市取前一段）；其余前段拼成地址按 50 拆 address1/address2。
    省/州与中文字段留空（歧义大，交人工）。返回 {address1,address2,city_en,province_city_en_us,postcode,country_en_us}。"""
    res = {"address1": "", "address2": "", "city_en": "", "province_city_en_us": "",
           "postcode": "", "country_en_us": ""}
    parts = [p.strip() for p in re.split(r"[，,]", raw or "") if p.strip()]
    if not parts:
        return res
    res["country_en_us"] = parts.pop()
    if parts:
        m = re.search(r"\d{5,6}", parts[-1])
        if m:
            res["postcode"] = m.group(0)
            rest = (parts[-1][:m.start()] + parts[-1][m.end():]).strip(" ,")
            parts.pop()
            if rest:                     # 城市与邮编同段，如 "Beijing 100142"
                res["city_en"] = rest
            elif parts:                  # 邮编独立成段，城市取前一段
                res["city_en"] = parts.pop()
        else:                            # 无邮编：末段当城市
            res["city_en"] = parts.pop()
    a1, a2 = rebalance_address(", ".join(parts), "")
    res["address1"], res["address2"] = a1, a2
    return res


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


def _assignee_from_applicant(applicant: dict) -> dict:
    """由一个申请人 dict 构造受让人结构：名称 + 完整通信地址。

    地址取 full_mailing_address_en（六字段拼接），再拆行：
    - address1/address2：两行版（供 _replace_everywhere 路径，如 20618 受让公司）
    - address_lines：多行版（发明人签字表用，超 2 行时克隆地址行）
    """
    applicant = applicant or {}
    name = (applicant.get("applicant_name_en") or "").strip()
    full_en = full_mailing_address_en(applicant)
    if not full_en:
        full_en = (applicant.get("contact_address_en") or "").strip()
    lines = address_lines(full_en, "")
    bal1, bal2 = rebalance_address(full_en, "")
    return {"name": name, "address1": bal1, "address2": bal2, "address_lines": lines}


def _assignee_from_company_address(name: str, company_address: str) -> dict:
    """由公司名 + company_address（逗号分隔的整串地址）构造受让人结构。
    供转让链中间公司（不在 applicants 里、地址只在 公司转公司 段的 company_address）取地址用。"""
    full = (company_address or "").strip()
    lines = address_lines(full, "")
    bal1, bal2 = rebalance_address(full, "")
    return {"name": (name or "").strip(), "address1": bal1, "address2": bal2, "address_lines": lines}


# 转让方公司地址结构化字段（前端 company_* 键）→ 申请人式 dict 的键映射
_COMPANY_ADDR_MAP = {
    "company_address1": "address1", "company_address2": "address2",
    "company_address_cn": "contact_address_cn",
    "company_city_en": "city_en", "company_city_cn": "city_cn",
    "company_province_en": "province_city_en_us", "company_province_cn": "province_city_zh_cn",
    "company_postcode": "postcode",
    "company_country_en": "country_en_us", "company_country_cn": "country_zh_cn",
}


def company_addr_dict(a: dict) -> dict:
    """转让方公司地址 → 申请人式 dict（供 _assignee_from_applicant / 确认函 _app_for_employer 直接复用）。
    结构化 company_* 字段优先（中英+邮编+国家）；缺省回退旧单串 company_address（逗号拆到 address1/2）。
    名称放 applicant_name_en。"""
    a = a or {}
    name = (a.get("assigning_company") or "").strip()
    if any((a.get(k) or "").strip() for k in _COMPANY_ADDR_MAP):
        d = {dst: (a.get(src) or "").strip() for src, dst in _COMPANY_ADDR_MAP.items()}
        d["applicant_name_en"] = name
        return d
    # 回退：旧单串
    full = (a.get("company_address") or "").strip()
    a1, a2 = split_address(full)
    return {"applicant_name_en": name, "address1": a1, "address2": a2,
            "contact_address_en": full, "contact_address_cn": "", "city_en": "", "city_cn": "",
            "province_city_en_us": "", "province_city_zh_cn": "", "postcode": "",
            "country_en_us": "", "country_zh_cn": ""}


def get_assignee(fields: dict) -> dict:
    """受让人（申请人第一位）——兼容旧调用。"""
    applicants = fields.get("applicants") or []
    return _assignee_from_applicant(applicants[0] if applicants else {})


def _norm_company(s: str) -> str:
    """公司名归一：小写 + 去掉所有非字母数字（空格/逗号/点/括号等），用于宽松匹配。
    这样 "ABC Co., Ltd." 与 "ABC Co.,Ltd" / "abc co ltd" 视为同名。"""
    return re.sub(r"[^0-9a-z]+", "", (s or "").lower())


def resolve_assignee(fields: dict, name: str) -> dict:
    """按受让人名字在 applicants 里匹配取地址（归一化：去空格/大小写/标点）。

    匹配优先级：①applicants 里同名申请人取其地址；②转让链中间公司——applicants 里没有、
    但有 公司转公司 段的 assigning_company == 该名字，则用该段 company_address 取地址
    （发明人先转给自己公司 B、B 再转申请人时，X→B 这份的受让人 B 地址来源）；
    ③都没有，名称仍用传入名（多公司各段名字保持各异）、地址回退首位申请人并标 matched=False。
    返回结构同 get_assignee，附 matched 标记。"""
    applicants = fields.get("applicants") or []
    key = _norm_company(name)
    if key:
        for a in applicants:
            if _norm_company(a.get("applicant_name_en")) == key:
                res = _assignee_from_applicant(a)
                res["matched"] = True
                return res
        # 转让链中间公司：地址在 公司转公司 段（结构化 company_* 或旧单串 company_address）
        for asg in fields.get("assignments") or []:
            if asg.get("assignment_type") != "公司转公司" or _norm_company(asg.get("assigning_company")) != key:
                continue
            cd = company_addr_dict(asg)
            if any(cd.get(k) for k in ("address1", "city_en", "postcode", "country_en_us", "contact_address_en")):
                res = _assignee_from_applicant(cd)   # 结构化→六字段拼全址拆行；旧串→逗号拆
                res["name"] = name
                res["matched"] = True
                return res
    res = _assignee_from_applicant(applicants[0] if applicants else {})
    if (name or "").strip():
        res["name"] = name.strip()   # 名称不被首位申请人覆盖（多公司各段名字保持各异）
    res["matched"] = False
    return res


def application_type_words(application_type: str) -> tuple:
    """申请类型 → (app_type_eng, confirm_type)；非枚举值返回空（缺失由审核页挡）。"""
    if application_type == "发明":
        return "invention", "an invention"
    if application_type == "外观":
        return "design", "a design"
    return "", ""


def _employer_groups(fields: dict) -> list:
    """按 inventors[].employer 分组，返回 [(employer, [inventor,...]), ...]，保持出现顺序。
    employer 归一化（去空格/大小写）判同组；空 employer 单独成 '' 组（归属由调用方决定）。"""
    groups, index = [], {}
    for inv in fields.get("inventors") or []:
        emp = (inv.get("employer") or "").strip()
        key = emp.lower()
        if key not in index:
            index[key] = len(groups)
            groups.append((emp, []))
        groups[index[key]][1].append(inv)
    return groups


def effective_assignments(fields: dict):
    """生成/校验实际使用的转让段（让 Assignment 与确认函按同一套 employer 分组）。

    规则（详见 us_submission/在线审核与文件生成方案.md §2.3.1）：
    - 公司转公司段：永远保留（转让链无法自动派生，只能上游给）；
    - 个人转公司段：发明人有可用 employer → 按 employer 分组重新派生并覆盖上游个人转公司段；
      无任何 employer → 原样沿用上游 assignments（保持单公司老案行为不变）；
    - 不擅改数据，边界只告警：employer 不在申请人列表（前雇主，地址回退首位申请人）、
      多申请人但发明人缺 employer（暂归首位申请人）。
    :return: (assignments:list, warnings:list)
    """
    explicit = fields.get("assignments") or []
    warnings = []
    groups = _employer_groups(fields)
    if not any(emp for emp, _ in groups):
        return explicit, warnings  # 无 employer：完全保持现行为

    applicants = fields.get("applicants") or []
    # 与 resolve_assignee 同一套归一化匹配，避免"能解析到地址却仍误报告警"
    applicant_keys = {_norm_company(a.get("applicant_name_en")) for a in applicants}
    # 转让链中间公司：有 公司转公司 段从它转出（B→申请人），则 employer=B 不算断链
    bridge_keys = {_norm_company(a.get("assigning_company")) for a in explicit
                   if (a.get("assignment_type") or "") == "公司转公司" and (a.get("assigning_company") or "").strip()}
    first_applicant = (applicants[0].get("applicant_name_en") or "").strip() if applicants else ""

    derived = []
    for emp, invs in groups:
        names = [n for n in (format_inventor_name(i) for i in invs) if n]
        if not names:
            continue
        if not emp:
            assignee = first_applicant
            if len(applicants) != 1:
                warnings.append(f"发明人 {', '.join(names)} 未填归属公司（employer），已暂归首位申请人"
                                f"「{assignee}」，请核对")
        else:
            assignee = emp
            if _norm_company(emp) not in applicant_keys:
                if _norm_company(emp) in bridge_keys:
                    pass  # 转让链完整：X→B(本段) + B→申请人(公司转公司段)；B 地址由 resolve_assignee 从 company_address 取
                else:
                    warnings.append(f"转让链断裂：发明人归属公司「{emp}」不在申请人中，且无「公司转公司」段将其转给申请人。"
                                    f"请补一段公司转公司（{emp}→申请人），或确认该发明人可直接转让给申请人。")
        derived.append({"assignment_type": "个人转公司", "assignee": assignee,
                        "assignor_inventors": names})

    explicit_p2c = [a for a in explicit if (a.get("assignment_type") or "") == "个人转公司"]
    company2company = [a for a in explicit if (a.get("assignment_type") or "") == "公司转公司"]
    if explicit_p2c and len(explicit_p2c) != len(derived):
        warnings.append(f"按归属公司派生出 {len(derived)} 段个人转公司，与上游给的 {len(explicit_p2c)} 段不一致，"
                        f"已以归属公司分组为准")
    return derived + company2company, warnings


def validate_for_confirm(fields: dict) -> list:
    """confirm 前的硬校验（方案 4.3）：返回问题清单，空列表=通过。

    确认函自身的必填字段由其生成器校验（missing_fields），此处补齐
    生成器覆盖不到的：申请类型、转让安排及公司转公司四件套。
    转让段以 effective_assignments 为准（与实际生成的份数一致）。
    """
    problems = []
    if (fields.get("application_type") or "") not in ("发明", "外观"):
        problems.append("申请类型（application_type）缺失或非法，须为：发明 / 外观")

    assignments, _w = effective_assignments(fields)
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
            }
            for key, label in labels.items():
                if not (item.get(key) or "").strip():
                    problems.append(f"转让安排第{idx}段（公司转公司）缺少{label}（{key}）")
            # 公司地址：页面填的是结构化字段(company_address1/城市/邮编/国家)，company_address 是旧单串。
            # 生成时 company_addr_dict 结构化优先，故任一有值即算已填（避免只填结构化仍误报缺失）。
            if not ((item.get("company_address") or "").strip()
                    or (item.get("company_address1") or "").strip()):
                problems.append(f"转让安排第{idx}段（公司转公司）缺少公司地址（company_address / 地址1）")

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
    out = []
    for p in (fields.get("parent_applications") or []):
        p = p or {}
        appno = p.get("Application No") or p.get("application_no") or ""
        out.append({
            "Application No": appno,   # 本段申请号(This App，子案)；首段=本申请→空
            # 在先号(Prior，父案) 只取 Prior，不再回落 appno —— appno 现为 This App，
            # 混填会把子案号错当父案（分叉家族/新增空白行 Prior 未填时尤甚）。
            "Prior Application Number": p.get("Prior Application Number") or "",
            "Filing Date": p.get("Filing Date") or p.get("filing_date") or "",
            "Continuity Type": p.get("Continuity Type") or p.get("continuity_type") or "",
            "Prior Application Status": p.get("Prior Application Status") or "",
            "Patent Number": p.get("Patent Number") or "",   # Patented 时的专利号/授权日
            "Issue Date": p.get("Issue Date") or "",
        })
    fields["parent_applications"] = out
    return fields


def norm_subject_matter(sm: str) -> str:
    """归一申请类型到 Utility/Plant/Design（与 ADS us_submission_type 一致）。
    兼容旧值 UTL/DES/PLT 及中文；371 是落地方式(国家阶段)不是申请类型 → 归 Utility。"""
    s = (sm or "").strip().lower()
    if s in ("des", "design", "外观"):
        return "Design"
    if s in ("plt", "plant", "植物"):
        return "Plant"
    return "Utility"   # utl / utility / 371 / 空 / 其余 → Utility


def is_371(fields: dict) -> bool:
    """是否 371 国家阶段（落地方式判定，不看 subject_matter）。
    兼容旧数据 subject_matter=='371'。"""
    route = (fields.get("filing_route") or "") + (fields.get("business_type_zh_cn") or "")
    if "371" in route or "国家阶段" in route:
        return True
    return (fields.get("subject_matter") or "").strip() == "371"


def infer_subject_matter(fields: dict) -> str:
    """推断申请类型 Utility/Plant/Design（371 属落地方式，见 is_371，不在此）。审核页可改。"""
    if fields.get("subject_matter"):
        return norm_subject_matter(fields["subject_matter"])
    at = (fields.get("application_type") or "")
    if at == "外观":
        return "Design"
    if at in ("植物", "Plant", "plant"):
        return "Plant"
    return "Utility"


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
