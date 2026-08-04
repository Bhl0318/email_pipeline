#!/usr/bin/env python3
"""转达 OA 人员（转OA）— 把立项后的官文按客户/类型路由转给 OA 处理团队。
规则见 OP02-转达OA人员.md;客户公共邮箱见 P1-客户公共邮箱对照表.md。

本模块按步骤逐步补全,当前已实现:
  - 客户公共邮箱匹配（customer_public_email）
  - 收件人组装（forward_recipients）= 固定人员 + 客户公共邮箱
"""

# 客户案号前缀（案号第一段）→ 客户公共邮箱；未列出的客户用兜底邮箱
CUSTOMER_PUBLIC_EMAIL = {
    "20615": "didi_pa@metis-ip.com",    # 滴滴
    "20608": "shokz@metis-ip.com",      # 韶音
    "20618": "ui_pa@metis-ip.com",      # 联影
    "20633": "patent8@metis-ip.com",    # 大华
}
PUBLIC_EMAIL_FALLBACK = "patents_pa@metis-ip.com"   # 其他/未列出客户兜底

# 转OA 固定收件人（OP02 §3.2.1）：杨姣、薄佳璐
FORWARD_FIXED_TO = [
    "jiao.yang@metis-ip.com",    # 杨姣
    "jialu.bo@metis-ip.com",     # 薄佳璐
]

# 转OA 固定抄送（OP02 §3.3.1）
FORWARD_FIXED_CC = [
    "meixin.wu@metis-ip.com",    # 伍美欣
    "min.zhao@metis-ip.com",     # 赵敏
    "jingjing.li@metis-ip.com",  # 李晶晶
    "oa@metis-ip.com",           # OA立项
    "ya.su@metis-ip.com",        # 苏雅
    "juanjuan.yao@metis-ip.com", # 姚涓涓
    "qin.zhang@metis-ip.com",    # 张琴
]


def customer_public_email(project):
    """按案号前缀（第一段,如 20618）返回客户公共邮箱;未匹配用兜底邮箱。"""
    code = (project or "").split("-")[0].strip()
    return CUSTOMER_PUBLIC_EMAIL.get(code, PUBLIC_EMAIL_FALLBACK)


def forward_recipients(project):
    """转OA 收件人 = 固定人员(杨姣/薄佳璐) + 该客户公共邮箱。去重保序。"""
    to = list(FORWARD_FIXED_TO)
    pub = customer_public_email(project)
    if pub not in to:
        to.append(pub)
    return to


import re as _re


def _split_names(bspeople):
    """把 customer.bspeople 拆成人名列表（支持中英文逗号/顿号/分号分隔，去空白空项）。"""
    return [n.strip() for n in _re.split(r'[,，、;；]', bspeople or '') if n.strip()]


def get_customer_contacts(project, execute=None):
    """客户接口人邮箱列表（转OA 抄送用）:
    atw customer.bspeople(customer_code = 案号前5位) → 拆多个中文名 → 各查 users.usermail。
    查不到 / 异常 → 返回 []（不阻塞抄送）。execute 可注入（测试用），默认用 db_query.execute。"""
    code = (project or "")[:5]
    if not code:
        return []
    if execute is None:
        from db_query import execute as execute
    try:
        safe = code.replace("'", "\\'")
        rows = execute(f"SELECT bspeople FROM customer WHERE customer_code = '{safe}'")
        bspeople = rows[0].get("bspeople") if rows else ""
        mails = []
        for name in _split_names(bspeople):
            sn = name.replace("'", "\\'")
            r2 = execute(f"SELECT usermail FROM users WHERE username_zn = '{sn}'")
            mail = (r2[0].get("usermail") if r2 else "") or ""
            if mail and mail not in mails:
                mails.append(mail)
        return mails
    except Exception as e:
        import sys
        print(f"[转OA] 查客户接口人失败 {code}: {e}", file=sys.stderr)
        return []


def forward_cc(project, execute=None):
    """转OA 抄送 = 固定7人(OP02) + 客户接口人。去重保序。execute 可注入(测试用)。"""
    cc = list(FORWARD_FIXED_CC)
    for mail in get_customer_contacts(project, execute=execute):
        if mail not in cc:
            cc.append(mail)
    return cc


# 转OA 邮件正文模板（OP02 §3.4.2）；落款固定"系统"
FORWARD_BODY_TEMPLATE = (
    "诸位好，\n\n"
    "题述申请收到了{oa_type}，详情请见附件。{period_sentence}\n\n"
    "案号：{project}\n"
    "发文日：{issue_date}\n"
    "截止日期：{deadline}\n\n"
    "@OA 分析师值班人，请重启项目，生产管理安排人员处理。\n\n"
    "--\n"
    "发送人：系统\n"
)


def build_forward_body(item):
    """按 OP02 模板生成转OA 邮件正文。[官文类型]取 notification_type，日期取立项字段。"""
    project = item.get("project", "") or ""
    oa_type = item.get("notification_type", "") or item.get("project_name", "") or ""
    issue_date = item.get("oa_doc_date", "") or item.get("issue_date", "") or ""
    deadline = item.get("project_deadline", "") or ""
    period_sentence = (f"该官文的答复期限为 {deadline}。" if deadline
                       else "该官文的答复期限待确认。")
    return FORWARD_BODY_TEMPLATE.format(
        oa_type=oa_type, period_sentence=period_sentence,
        project=project, issue_date=issue_date, deadline=deadline,
    )


# 转OA 主题前缀
FORWARD_SUBJECT_PREFIX = "【OA自动立项通知】"

# US Document Type 代码 → 官文可读名（无官文文件名时的兜底用）
US_DOC_NAME = {
    "CTNF": "Non-Final Rejection", "CTFR": "Final Rejection", "CTAV": "Advisory Action",
    "NOA": "Notice of Allowance", "CTRS": "Requirement for Restriction Election",
    "EXIN": "Examiner Interview Summary Record", "CTEQ": "Ex Parte Quayle Action",
    "PPH.DECISION": "PPH Decision", "NT.CR.APP.PA": "Notice to file corrected application papers",
    "NTC.MISS.PRT": "Notice to file missing parts", "PETDEC": "Petition Decision Dismissed",
}


def official_doc_name(item):
    """官文可读名：US 代码转可读名（查不到用原代码）；CN/EP 用 notification_type。"""
    ntype = item.get("notification_type", "") or ""
    return US_DOC_NAME.get(ntype, ntype) if item.get("region") == "US" else ntype


def build_forward_subject(item, attachments=None):
    """转OA 主题 = 【OA自动立项通知】+ 官文文件名(去扩展名，本身即 发文日-官文名-案号)。
    无官文附件时兜底用 发文日-官文名-案号；再不行用原邮件主题。"""
    import os
    if attachments:
        base = os.path.splitext(os.path.basename(attachments[0]))[0].strip()
        if base:
            return FORWARD_SUBJECT_PREFIX + base
    date = item.get("oa_doc_date", "") or item.get("issue_date", "") or ""
    core = "-".join(p for p in (date, official_doc_name(item), item.get("project", "")) if p)
    return FORWARD_SUBJECT_PREFIX + (core or item.get("email_subject", "") or "OA转达")


def forward_attachments(item, msgid_to_pdfs=None, check_exists=True):
    """收集该立项项要附的官文 PDF 路径:
    CN/EP 取邮件附件(按 message_id 从 _inbox),US 优先取盖章副本(us_stamped_pdf_path),
    无盖章版则取原下载官文(us_pdf_path);再加同案号 892/1449 文献(us_ref_pdf_paths)。
    去重;check_exists=True 时过滤掉不存在的文件。"""
    import os
    paths = []
    if msgid_to_pdfs:
        paths.extend(msgid_to_pdfs.get(item.get("message_id", ""), []) or [])
    # US：优先附盖章副本（DOCKETED 邮戳），无盖章版则附原官文
    if item.get("us_stamped_pdf_path"):
        paths.append(item["us_stamped_pdf_path"])
    elif item.get("us_pdf_path"):
        paths.append(item["us_pdf_path"])
    # 同案号 892/1449 文献（原文件，不盖章）
    paths.extend(item.get("us_ref_pdf_paths") or [])
    seen, out = set(), []
    for p in paths:
        if not p or p in seen:
            continue
        if check_exists and not os.path.exists(p):
            continue
        seen.add(p)
        out.append(p)
    return out
