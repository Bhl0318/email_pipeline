#!/usr/bin/env python3
"""确认邮件正文模块库（模板来源：丁玲《US新申请信息确认邮件》2024-10-31 版
+ 2026 顶层更新：签字要求提醒模块、微实体金额 $251,190）。

build_email_modules(fields, params) 返回模块列表，审核页全部展示、
审阅人勾选适用项，发送时按勾选拼装正文。

年度更新值（如微实体金额）集中在下方常量，便于维护。
"""
import math

# ── 年度更新值 ──
MICRO_ENTITY_INCOME_LIMIT = "$251,190"   # 美国中等家庭收入的3倍，每年9月前后更新
EXCESS_CLAIM_FEE = 50      # 每超1个权要（美元）
EXCESS_PAGE_FEE = 210      # 每超50页（美元）
CLAIM_LIMIT = 20           # 权要免费上限
CAF_FEE_6YR = "2,700"      # 延续申请费：最早受益日后超6年（大实体，美元）
CAF_FEE_9YR = "4,000"      # 延续申请费：最早受益日后超9年（大实体，美元）

# 字体格式对齐汇报信实际邮件：宋体/Times New Roman，12pt，行距150%（内联样式随邮件发出）
_FONT = "font-family:宋体,'SimSun','Times New Roman',serif;font-size:12pt;color:#000000;"
_P = '<p style="margin:0 0 12px 0;line-height:150%;' + _FONT + '">{}</p>'
_H = '<p style="margin:16px 0 8px 0;line-height:150%;' + _FONT + '"><b>{}</b></p>'


def _p(text):
    return _P.format(text)


def _h(text):
    return _H.format(text)


def build_email_modules(fields: dict, params: dict = None) -> list:
    """返回 [{id, title, html, checked, note}]；checked 为推导的默认勾选。
    （自定义正文内容由审核页在模块之间的"插入槽"提供，不在此生成。）"""
    params = params or {}
    case_volume = fields.get("case_volume") or "（案号）"
    filing_route = fields.get("filing_route") or "（落地方式）"
    ae_methods = (fields.get("ae_methods") or "").strip()
    advance = fields.get("case_advance_info") or {}
    pct_no = (advance.get("pct_app_no") or "").strip()
    priorities = fields.get("priorities") or []

    modules = []

    # 1. 机密声明 + 称呼
    salutation = (params.get("salutation") or "").strip() or "XXX"
    modules.append({
        "id": "greeting", "title": "机密声明 + 称呼开场", "checked": True,
        # 机密声明两行加粗斜体（与汇报信模板 ***...*** 一致）
        "html": _p("<b><i>机密并受律师客户通讯特权保护</i></b>") +
                _p("<b><i>Privileged and Confidential; Attorney-Client Communication</i></b>") +
                _p(f"{salutation}，您好！") +
                _p("很高兴与您对接本案的递交事宜。本案已定稿，烦请贵司确认以下信息："),
        "note": "在右侧输入客户称呼",
    })

    # 2. 确认申请信息
    # 落地方式话术片段：默认按 filing_route(+PCT) 自动拼，审阅人可在输入框整体改写
    default_route_phrase = (
        f"本案是基于{pct_no}以{filing_route}的方式进美国" if pct_no
        else f"本案以{filing_route}的方式进美国"
    )
    route_phrase = (params.get("route_phrase") or "").strip() or default_route_phrase
    route_sentence = route_phrase
    if ae_methods and ae_methods.lower() != "none":
        route_sentence += f"，同时要求{ae_methods}加速"
    modules.append({
        "id": "app_info", "title": "确认申请信息", "checked": True,
        "html": _h("确认申请信息") +
                _p(f"附件是{case_volume}的申请信息确认函（application information sheet），"
                   f"{route_sentence}，烦请您确认基本申请信息（高亮部分请重点确认）。"),
        "note": "在右侧编辑落地方式话术（默认按落地方式自动生成）",
        "input": "route_phrase", "input_value": route_phrase, "input_default": default_route_phrase,
    })

    # 3. 签字文件（Declaration + Assignment + USPTO 签署提醒）
    modules.append({
        "id": "signature_docs", "title": "签字文件（Declaration / Assignment / USPTO 签署提醒）", "checked": True,
        "html": _h("签字文件") +
                _p("Declaration（发明人声明）。需要发明人签署，注：日期不需要填写。"
                   "若Declaration不与申请一起递交，补交则会产生170美元的官费（大实体）。") +
                _p("Assignment（专利权转让书），是表明发明人将专利权转让的文件。我司根据优先权信息制作了相关转让文件。"
                   "请注意，日期需要签署，签名中英文均可，烦请贵司签署后反馈扫描件。") +
                _p("⚠️温馨提示：关于签字文件的要求") +
                _p("根据美国专利商标局（USPTO）的政策要求，所有提交的文件必须由签字人本人亲自签署，"
                   "不得代签或使用非本人生成的电子签名。") +
                _p("为确保顺利提交，请提供签字为本人签署的证明材料。建议的证明材料形式："
                   "签字文件由签署人本人公司邮箱发送的邮件记录，且邮件正文带本人落款。") +
                _p("如有疑问欢迎随时与我们联系。"),
        "note": "",
    })

    # 4. 实体确认（首案）
    modules.append({
        "id": "entity_first", "title": "实体确认（适用于首案）", "checked": True,
        "html": _h("烦请贵方确认所属实体（适用于首案）") +
                _p("大实体：不满足小实体与微实体情况下的其他实体；") +
                _p("小实体：个人或者相关规定下的小型企业雇员数（包含关联机构）不超500人或者相关规定下的非盈利组织"
                   "（此条包含大学及高等教育机构），但同时，该实体没有将发明的相关权益转移给非小实体的第三方；") +
                _p("微小实体：1. 符合小实体的标准；2. 此前在美国申请的非临时申请不超过4件"
                   "（不包括PCT申请、临时申请、美国以外其他国家的申请）；"
                   f"3. 发明人/申请人上一年度总收入均不超过美国中等家庭收入的3倍（当前为{MICRO_ENTITY_INCOME_LIMIT}）；"
                   "4. 申请人及发明人都没有也没有义务（例如法律或者合同这种约束下的义务）将所有权益转给不满足上述第三条要求的实体。") +
                _p("美国专利商标局（USPTO）针对小实体和微小实体落实了一系列的费用减免政策。"
                   "不满足小实体或微小实体的标准却按照此标准申请专利的，可能会导致专利无效。"
                   "请允许我司在实体确认上获得贵司的书面正式确认，以便归档供后续查证。"
                   "我司建议申请人如实申报实体情况。对实体确认有任何不清楚的地方，欢迎随时咨询。谢谢！"),
        "note": "与「大实体（非首案）」二选一",
    })

    # 5. 实体确认（非首案）——实体类型可变（大/小/微），默认大实体
    repeat_entity = (params.get("repeat_entity") or "").strip() or "大"
    modules.append({
        "id": "entity_repeat", "title": f"{repeat_entity}实体（适用于非首案）", "checked": False,
        "html": _h(f"{repeat_entity}实体（适用于非首案）") +
                _p(f"贵司之前递交案件时确认实体为{repeat_entity}实体，后续流程中我方将按照贵司所属{repeat_entity}实体进行操作。"
                   "若实体已变，烦请告知。如贵司对此问题有疑问，请随时垂询。"),
        "note": "与「实体确认（首案）」二选一；在右侧选实体类型",
        "select": "repeat_entity", "select_options": ["大", "小", "微小"], "select_value": repeat_entity,
    })

    # 6. POA（首案）
    modules.append({
        "id": "poa_first", "title": "POA 总委（适用于首案）", "checked": True,
        "html": _h("POA（适用于首案）") +
                _p("此案为我司代理贵方在美国递交的第一个案子，需要签署总委（POA），"
                   "表示贵方将处理专利申请等相关事务的权利委托给我司，该文件可重复利用，仅需签署一次。"
                   "签署该文件的人员应为能够明确代表贵方的管理层（如CEO、总裁、副总裁、部门主管等），"
                   "需要代表本案申请公司的人员将英文姓名及英文职称填写在对应位置，先填写Name与Title后，"
                   "再打印出来，请签署人在Signature处手动签名（中英文均可），注：日期不需要填写。"
                   "之后烦请贵司反馈扫描件即可。另附签字模板以便参考。"),
        "note": "",
    })

    # 7. 优先权 DAS（有优先权时默认勾选，自动生成表格）
    _TD = f'style="border:1px solid #999;padding:4px 10px;line-height:150%;{_FONT}"'
    rows_html = ""
    for p in priorities:
        das = (p.get("access_code") or "").strip() or "请提供"
        rows_html += (
            f'<tr><td {_TD}>{p.get("priority_no") or p.get("priority_num") or ""}</td>'
            f'<td {_TD}>{p.get("priority_date") or ""}</td>'
            f'<td {_TD}>{das}</td></tr>'
        )
    priority_table = (
        f'<table style="border-collapse:collapse;margin:6px 0 12px 0;{_FONT}">'
        f'<tr><td {_TD}><b>中国优先申请号</b></td>'
        f'<td {_TD}><b>中国优先申请日</b></td>'
        f'<td {_TD}><b>DAS码</b></td></tr>'
        f"{rows_html}</table>"
    )
    modules.append({
        "id": "priority_das", "title": "优先权 DAS 码", "checked": bool(priorities),
        "html": _h("优先权") +
                _p("对于申请日在2018年9月1日（含）之后的申请，申请人希望获得国家知识产权局或美国专利商标局出具的"
                   "电子优先权文件的，需按照WIPO DAS平台要求履行交存、查询手续，"
                   "具体可见《中美优先权电子交换业务由双边渠道切换的公告》。"
                   "因题述申请的中国优先权（见下表）非我方代理，故烦请贵司提供中国优先权的DAS码，"
                   "以便在递交时可以及时获取优先权信息。若暂无，可后期统一补交，"
                   "期限为申请日起4个月或最早优先权日起16个月（以后到者为准），贵司申请后反馈即可。"
                   "（外观申请的DAS或纸质优先权副本的补交期限为案件授权缴费之前）") +
                (priority_table if priorities else _p("（本案无优先权数据）")),
        "note": "优先权数据来自表单，改完优先权后点「重新生成模块」刷新表格",
    })

    # 8. CN 保密通知书（巴黎公约小客户）
    modules.append({
        "id": "cn_secrecy_notice", "title": "优先权中国保密请求通过的通知书（CN优先权非我方代理）", "checked": False,
        "html": _h("优先权中国保密请求通过的通知书") +
                _p("本案是以巴黎公约方式进美国，烦请贵司提供中国保密请求通过的通知书。"),
        "note": "适用于巴黎公约 + CN 优先权非我方代理的小客户",
    })

    # 9. 保密审查（US 新申请无优先权）
    no_priority_new = (not priorities) and (not pct_no)
    modules.append({
        "id": "secrecy_review", "title": "保密审查（US新申请无优先权）", "checked": no_priority_new,
        "html": _h("保密审查事宜") +
                _p("本案是US新申请递交，没有优先权，事关保密审查事宜。"
                   "烦请贵司确认本案的发明产生地是哪里，中国还是美国？"),
        "note": "",
    })

    # 10. 超权费（需要输入权要数）
    claims_total = params.get("claims_total")
    if claims_total:
        try:
            claims_total = int(claims_total)
        except (TypeError, ValueError):
            claims_total = None
    if claims_total and claims_total > CLAIM_LIMIT:
        excess = claims_total - CLAIM_LIMIT
        fee = excess * EXCESS_CLAIM_FEE
        claims_html = _h("超权费") + _p(
            f"本案总权要数为{claims_total}个，超出了USPTO规定范围，"
            f"需缴纳超权费{fee}美元（每超1个权要{EXCESS_CLAIM_FEE}美元，本案合计超权数量是{excess}个）"
        )
    else:
        claims_html = _h("超权费") + _p("（在模块旁输入总权要数后自动计算；不超过20个权要不适用本模块）")
    modules.append({
        "id": "excess_claims", "title": "超权费", "checked": bool(claims_total and claims_total > CLAIM_LIMIT),
        "html": claims_html, "note": "输入总权要数（>20 才适用）", "input": "claims_total",
        "input_value": params.get("claims_total") or "",
    })

    # 11. 超页费（需要输入总页数与超页数）
    pages_total = params.get("pages_total")
    pages_excess = params.get("pages_excess")
    try:
        pages_total = int(pages_total) if pages_total else None
        pages_excess = int(pages_excess) if pages_excess else None
    except (TypeError, ValueError):
        pages_total = pages_excess = None
    if pages_total and pages_excess:
        fee = math.ceil(pages_excess / 50) * EXCESS_PAGE_FEE
        pages_html = _h("超页费") + _p(
            f"本案申请文件的总页数共计{pages_total}页，超出了USPTO规定范围，"
            f"需缴纳超页费合计{fee}美元（每超50页{EXCESS_PAGE_FEE}美元，本案合计超页数量为{pages_excess}页）"
        ) + _p("USPTO费用官网可以核查：https://www.uspto.gov/learning-and-resources/fees-and-payment/uspto-fee-schedule")
    else:
        pages_html = _h("超页费") + _p("（在模块旁输入总页数和超页数量后自动计算）")
    modules.append({
        "id": "excess_pages", "title": "超页费", "checked": bool(pages_total and pages_excess),
        "html": pages_html, "note": "输入总页数 + 超页数量", "input": "pages",
        "input_value": "",
    })

    # 11b. 延续申请费 CAF（续案在最早受益日期后超 6/9 年；默认不勾，由审核人选档位）
    caf_tier = (params.get("caf_tier") or "").strip() or "6-9"
    if caf_tier == "9+":
        caf_fee, caf_span = CAF_FEE_9YR, "超过9年"
    else:
        caf_fee, caf_span = CAF_FEE_6YR, "超过6年但未超过9年"
    modules.append({
        "id": "continuing_application_fee",
        "title": "延续申请费（Continuing Application Fee, CAF）",
        "checked": False,
        "html": _h("延续申请费（Continuing Application Fee, CAF）") +
                _p(f"根据美国专利商标局的规定，本延续申请的递交日距最早受益日期"
                   f"（即申请人可以主张的最早优先权日期）{caf_span}，需缴纳延续申请费{caf_fee}美元（大实体）。"),
        "note": "续案适用时勾选；在右侧选适用档位",
        "select": "caf_tier", "select_options": ["6-9", "9+"], "select_value": caf_tier,
    })

    # 12. IDS
    modules.append({
        "id": "ids", "title": "IDS 披露文献", "checked": True,
        "html": _h("提供IDS相关披露文献") +
                _p("根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的"
                   "与本案申请的可专利性有重要关联（material to patentability）的文献资料，"
                   "必须以information disclosure statement（IDS）的形式向美国专利商标局提交。"
                   "如果存在上述文献，请贵司尽快提供给我方，以便我方及时准备并向美国专利商标局提交IDS。"),
        "note": "",
    })

    # 13. 结尾
    modules.append({
        "id": "closing", "title": "结尾", "checked": True,
        "html": _p("待贵司回复后，我司会进行后续递交事宜，谢谢。") + _p("顺祝商祺！"),
        "note": "",
    })

    return modules
