"""20618 联影未定稿确认邮件；仅用于确认邮件正文，不影响确认函或签字文件。"""

from datetime import date
from html import escape

from .email_modules import _p


def _s(value):
    return escape(str(value or "").strip())


def _date(value):
    raw = str(value or "").strip()
    try:
        d = date.fromisoformat(raw[:10])
        return f"{d.year}年{d.month}月{d.day}日"
    except ValueError:
        return raw


def _module(mid, title, body, *, checked=True, note="", inputs=None):
    result = {"id": mid, "title": title, "html": body, "checked": checked, "note": note}
    if inputs:
        result["extra_inputs"] = inputs
    return result


def build_20618_email_modules(fields, params):
    params = params or {}
    case_no = _s(fields.get("case_volume"))
    title = _s((fields.get("case_info") or {}).get("case_name_en"))
    client_ref = _s(params.get("client_case_no"))
    handler = _s(params.get("client_handler"))
    deadline = _s(params.get("filing_deadline"))
    language = _s(params.get("filing_language") or "英文")
    invention_country = _s(params.get("invention_country") or "中国")
    salutation = _s(params.get("salutation") or "XXX")
    opening = _s(params.get("opening") or "很高兴与您对接本案的递交事宜。本案尚未定稿，提前与您确认申请信息（高亮部分请重点确认），烦请回邮确认。")
    parents = fields.get("parent_applications") or []
    pct = fields.get("case_advance_info") or {}
    priorities = fields.get("priorities") or []
    priority_rows = []
    for row in parents:
        no = row.get("Prior Application Number") or row.get("Application No") or ""
        if no:
            priority_rows.append((no, row.get("Filing Date") or ""))
    pct_no = pct.get("pct_app_no") or ""
    if pct_no and not any(str(no).strip().upper() == str(pct_no).strip().upper() for no, _ in priority_rows):
        priority_rows.append((pct_no, pct.get("pct_app_date") or ""))
    for row in priorities:
        no = row.get("priority_no") or row.get("priority_num") or ""
        if no and not any(str(prior).strip().upper() == str(no).strip().upper() for prior, _ in priority_rows):
            priority_rows.append((no, row.get("priority_date") or ""))
    priority_html = "".join(_p(f"优先权{i}：{_s(no)}（申请日{_s(_date(day))}）") for i, (no, day) in enumerate(priority_rows, 1))
    if not priority_html:
        priority_html = _p("优先权：无")

    applicants = fields.get("applicants") or []
    applicant_names = "<br>".join(_s(a.get("applicant_name_en")) for a in applicants if a.get("applicant_name_en"))
    applicant_addresses = []
    for a in applicants:
        addr = a.get("contact_address_en") or ", ".join(str(a.get(k) or "").strip() for k in
            ("address1", "address2", "city_en", "province_city_en_us", "postcode", "country_en_us") if a.get(k))
        applicant_addresses.append(_s(addr))
    inventors = []
    for inv in fields.get("inventors") or []:
        full = inv.get("full_name_en") or ", ".join(x for x in (inv.get("last_name_en"), inv.get("first_name_en")) if x)
        line = _s(full)
        if inv.get("name_cn"):
            line += " / " + _s(inv.get("name_cn"))
        if inv.get("employer"):
            line += "【就职于" + _s(inv.get("employer")) + "】"
        inventors.append(line)

    extra_inputs = [
        {"key": "client_case_no", "label": "联影案号", "value": params.get("client_case_no") or "", "type": "text"},
        {"key": "client_handler", "label": "经办人", "value": params.get("client_handler") or "", "type": "text"},
        {"key": "filing_deadline", "label": "递交期限", "value": params.get("filing_deadline") or "", "type": "text"},
        {"key": "filing_language", "label": "申请递交语言", "value": params.get("filing_language") or "英文", "type": "select", "options": ["英文", "中文"]},
        {"key": "invention_country", "label": "发明产生地", "value": params.get("invention_country") or "中国", "type": "select", "options": ["中国", "美国"]},
    ]
    modules = [
        _module("greeting", "机密声明 + 称呼开场",
            _p("<b><i>机密并受律师客户通讯特权保护</i></b>") +
            _p("<b><i>Privileged and Confidential; Attorney-Client Communication</i></b>") +
            _p(f"{salutation}，您好！") + _p(opening)),
        _module("app_info", "联影申请信息",
            _p(f"联影案号：{client_ref}") + _p(f"经办人：{handler}") + _p(f"七星天案号：{case_no}") +
            _p(f"申请题目（英文）：{title}") + _p("递交形式：US") + _p(f"递交期限：{deadline}") +
            _p(f"申请递交语言：{language}") + _p("权利要求书：未定") + _p("说明书：未定") +
            _p("说明书附图：未定") + priority_html +
            _p(f"申请人：{applicant_names}") + _p("申请人地址：" + "<br>".join(applicant_addresses)) +
            _p("发明人：" + "<br>".join(inventors)) + _p(f"发明产生地：{invention_country}"),
            note="联影案号、经办人、递交期限请核对后填写", inputs=extra_inputs),
    ]
    modules[0]["input_value"] = params.get("opening") or "很高兴与您对接本案的递交事宜。本案尚未定稿，提前与您确认申请信息（高亮部分请重点确认），烦请回邮确认。"
    first_parent = parents[0] if parents else {}
    basis = _s(first_parent.get("Prior Application Number") or pct_no or "")
    route = _s(fields.get("filing_route"))
    route_lower = route.lower()
    if "continuation in part" in route_lower or "continuation-in-part" in route_lower or "cip" in route_lower:
        route_zh = "美国部分续案申请"
    elif "division" in route_lower:
        route_zh = "美国分案申请"
    elif "continuation" in route_lower:
        route_zh = "美国续案申请"
    else:
        route_zh = "美国申请"
    if basis:
        route_sentence = f"本案是基于{basis}做的{route_zh}{f'（{route}）' if route else ''}，以上基本信息根据优先权和大为系统的内容进行准备，若本案申请信息有变化，烦请告知。"
    else:
        route_sentence = "以上基本信息根据优先权和大为系统的内容进行准备，若本案申请信息有变化，烦请告知。"
    modules.append(_module("route", "申请信息确认说明", _p("1. " + route_sentence)))
    modules.append(_module("signature_docs", "签字文件（Declaration / Assignment）",
        _p("2. 我方根据上述信息准备了签署文件，烦请发明人签署后返回扫描件。") +
        _p("Declaration（发明人声明）。需要发明人签署，注：日期不需要填写。若Declaration不与申请一起递交，补交则会产生170美元的官费（大实体）。") +
        _p("对于已离职发明人，如经过努力（diligent effort）发明人还是无法联系上或者拒绝签字，可使用替代声明，可保存联系发明人的邮件、电话录音以及挂号信等相关证据。附件是我司准备的发明人替代声明，签署该文件的人员应为能够明确代表公司的管理层（如CEO、总裁、副总裁、部门主管等），烦请代表本案申请公司签署的人员在Signature处手动签名，之后烦请贵司反馈扫描件即可。") +
        _p("Assignment（专利权转让书），是表明发明人将专利权转让的文件。我司根据优先权信息制作了相关转让文件。签名中英文均可，需签署日期。烦请贵司签署后反馈扫描件。") +
        _p("对于已离职发明人，可使用离职发明人的劳动合同以及保密协议代替Assignment。（中英文两版，劳动合同与保密协议中需要有关于知识产权归属的具体内容）。") +
        _p("⚠️温馨提示：关于签字文件的要求") +
        _p("根据美国专利商标局（USPTO）的政策要求，所有提交的文件必须由签字人本人亲自签署，不得代签或使用非本人生成的电子签名。") +
        _p("为确保顺利提交，请提供签字为本人签署的证明材料。建议的证明材料形式：") +
        _p("1）针对手签的文件，贵司除常规提供我司扫描件外，原件可以保留并定期寄送我们。") +
        _p("2）针对电子签的文件，可通过飞书发给签字人员，签字后截图对方名字及返回的签字文件；也可通过系统上传方式截图作为证明。")))
    modules.append(_module("ids", "IDS 披露文献",
        _p("3. IDS：根据美国专利法的规定，在专利申请过程中，发明人、申请人及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以information disclosure statement（IDS）的形式向美国专利商标局提交。如果存在上述文献，请贵司尽快提供给我方，以便我方及时准备并向美国专利商标局提交IDS。")))
    ending = f"本案递交期限为美国时间{deadline}，烦请尽快确认申请信息，谢谢！" if deadline else "烦请尽快确认申请信息，谢谢！"
    modules.append(_module("closing", "结尾", _p(ending) + _p("顺颂商祺！")))
    return modules
