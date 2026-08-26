#!/usr/bin/env python3
"""转达 OA 人员（转OA）— 把立项后的官文按客户/类型路由转给 OA 处理团队。
规则见 OP02-转达OA人员.md;客户公共邮箱见 P1-客户公共邮箱对照表.md。

本模块按步骤逐步补全,当前已实现:
  - 客户公共邮箱匹配（customer_public_email）
  - 收件人组装（forward_recipients）= 固定人员 + 客户公共邮箱
"""
import os

# OA 分配页对外基址（如 http://10.10.70.88:8501）：由 pipeline_config.json 的 oa_assign_base_url
# 经 main.py 注入环境变量 OA_ASSIGN_BASE_URL；为空则转OA邮件不带分配链接。运行时读取（避免导入时机问题）。

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
    "ling.ding@metis-ip.com",    # 丁玲
    "yuan.wang@metis-ip.com",    # 王圆
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


# 特殊抄送规则：(客户码, 官文类型) → 额外抄送邮箱。当前为空
# （原 (20608, NOA)→丁晓龙 已移除：NOA 不再立项，转OA 不会发出，规则永不触发）。
EXTRA_CC_RULES = {}


def forward_cc(project, item=None, execute=None):
    """转OA 抄送 = 固定7人(OP02) + 客户接口人 + 特殊规则额外抄送。去重保序。
    item 提供 notification_type，用于匹配 EXTRA_CC_RULES；execute 可注入(测试用)。"""
    cc = list(FORWARD_FIXED_CC)
    for mail in get_customer_contacts(project, execute=execute):
        if mail not in cc:
            cc.append(mail)
    # (客户码, 官文类型) 特殊规则
    code = (project or "").split("-")[0].strip()
    ntype = (item or {}).get("notification_type", "")
    for mail in EXTRA_CC_RULES.get((code, ntype), []):
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
    "{unpublished_line}"
    "{prescreen_line}"
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
    # 预审案件加注一行（第一/二次审查意见 + 邮件含预审案件时由分类器置 prescreen_note）
    prescreen_line = "注：该案件为预审案件\n\n" if item.get("prescreen_note") else ""
    # 未公开/受限申请：公开 API 403，官文未能自动下载/无附件 → 正文明确标注 + 明细，便于人工去 Patent Center 取
    if item.get("us_unpublished"):
        _app = item.get("application_no", "") or item.get("application", "") or ""
        _doc = item.get("notification_type", "") or item.get("document_code", "") or ""
        unpublished_line = (
            "注：该官文对应【未公开/受限申请】，系统无法自动下载官文，请手动从 Patent Center 获取官文。\n"
            f"    案号：{project}    申请号：{_app}    官文代码：{_doc}    发文日：{issue_date}\n\n")
    else:
        unpublished_line = ""
    return FORWARD_BODY_TEMPLATE.format(
        oa_type=oa_type, period_sentence=period_sentence,
        project=project, issue_date=issue_date, deadline=deadline,
        unpublished_line=unpublished_line,
        prescreen_line=prescreen_line,
    )


# OA 分配链接不进转OA邮件（不发流程人员），单独发给薛虹，抄送海灵
OA_ASSIGN_NOTIFY_TO = "hxue@metis-ip.com"        # 薛虹
OA_ASSIGN_NOTIFY_CC = ["hailing.bi@metis-ip.com"]  # 海灵


# 这些案号不发 OA 分配链接：20849 / 20608 开头，或 6 / 8 开头
def _skip_assign_link(project):
    p = (project or "").strip()
    return p.startswith(("20849", "20608")) or p[:1] in ("6", "8")


def build_assign_notify(plans):
    """汇总本轮各立项案件的 OA 分配链接，生成发给薛虹的 (subject, body)。
    基址(env OA_ASSIGN_BASE_URL)为空或无可发案件时返回 None（不发）。
    20849/20608/6*/8* 开头的案号不发分配链接。"""
    base = os.environ.get("OA_ASSIGN_BASE_URL", "").rstrip("/")
    if not base:
        return None
    rows = []
    for p in plans:
        it = p.get("item", {})
        oa_id = it.get("oa_id", "") or ""
        if not oa_id:
            continue
        proj = it.get("project", "")
        if _skip_assign_link(proj):
            continue
        name = it.get("project_name", "") or it.get("notification_type", "")
        rows.append(f"{proj} {name}\n  {base}/oa-assign/{oa_id}")
    if not rows:
        return None
    subject = f"【OA分配链接】本轮 {len(rows)} 件待分配"
    body = "薛虹：\n\n以下为本轮新立项、待人员分配的案件及分配页链接：\n\n" + "\n\n".join(rows) + "\n\n--\n发送人：系统\n"
    return subject, body


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
