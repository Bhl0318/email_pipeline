#!/usr/bin/env python3
"""
OA 立项邮件筛选脚本 — 从邮件中识别需要 OA 立项的邮件并提取关键字段。

用法:
  # 从 read_email.py 输出的 JSON 筛选
  python3 filter_oa_email.py --input emails.json --output oa_results.json

  # 从本地 .msg 文件目录筛选（测试用）
  python3 filter_oa_email.py --msg-dir ../OA转达原始邮件示例/ --output oa_results.json

  # 从 stdin 管道输入
  python3 read_email.py --account docketing | python3 filter_oa_email.py --output oa_results.json
"""
import sys
import os
import json
import re
import argparse
from html.parser import HTMLParser

# 添加脚本目录到 path，以便导入 db_query
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ─── 申请类型推导 ─────────────────────────────────────────

COUNTRY_CODE_TO_APPLY_TYPE = {
    "US": "美国申请",
    "CN": "中国发明申请",
    "CM": "中国实用新型申请",
    "EP": "其他国家申请",
    "CS": "外观设计申请",
    "WO": "PCT申请",
    "DS": "外观设计申请",
    "DM": "外观设计申请",
}


def get_applytype(project):
    """从案号中提取国别代码，推导申请类型。"""
    m = re.search(r'\d{5}-\d{4}([A-Z]{2})\d{2}$', project)
    if m:
        code = m.group(1)
        return COUNTRY_CODE_TO_APPLY_TYPE.get(code, "")
    return ""


def get_country_code(project):
    """从案号中提取国别代码。"""
    m = re.search(r'\d{5}-\d{4}([A-Z]{2})\d{2}$', project)
    return m.group(1) if m else ""


# ─── 计划送审日 ──────────────────────────────────────────

from datetime import datetime, timedelta
from openai import OpenAI

# DeepSeek 配置（复用 parse_us_pdf 的密钥）
_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
_DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "REDACTED_API_KEY")
_DEEPSEEK_MODEL = "deepseek-chat"


def _ai_parse_ep_deadline(body, issue_date_str):
    """
    用 DeepSeek 从 EP 邮件正文中提取答复绝限日期和发文日。

    Returns:
        dict: {"deadline": "YYYY-MM-DD", "issue_date": "YYYY-MM-DD"} 或 None
    """
    client = OpenAI(api_key=_DEEPSEEK_API_KEY, base_url=_DEEPSEEK_BASE_URL)
    issue_hint = f"The issue date (date of the communication) is: {issue_date_str}\n" if issue_date_str else ""
    prompt = (
        f"This is an EP (European Patent) office action forwarding email from a patent agency.\n"
        f"{issue_hint}"
        f"Extract TWO dates from the email body below:\n"
        f"1. issue_date: the date the official communication was issued by EPO\n"
        f"2. deadline: the deadline date for responding to this communication\n"
        f"\n"
        f"IMPORTANT rules for identifying the correct deadline:\n"
        f"- Look for: 'due date of ...', 'within X months of ...', 'by Month DD, YYYY', "
        f"'i.e. by ...', 'we look forward to receiving ... by ...'.\n"
        f"- If a period (e.g. '6 months') is given, calculate from the correct base date "
        f"(which may be a publication date, not the issue date).\n"
        f"- Do NOT use the date of oral proceedings (hearing date) as the deadline.\n"
        f"- If the email contains BOTH a 'due date of ...' AND a 'we look forward to receiving ... by ...', "
        f"prefer the 'due date' as the deadline (it is the official EPO filing deadline).\n"
        f"- If the email explicitly states a non-extendable deadline, use that date.\n"
        f"- If only one date expression with 'by' exists, use it as the deadline.\n"
        f"\n"
        f'Return ONLY JSON: {{"issue_date": "YYYY-MM-DD", "deadline": "YYYY-MM-DD"}}\n'
        f'For any field not found, use null.\n'
        f"\n---\n{body[:12000]}\n---"
    )
    try:
        resp = client.chat.completions.create(
            model=_DEEPSEEK_MODEL,
            max_tokens=80,
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.choices[0].message.content.strip()
        m = re.search(r'\{.*?\}', content, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception as e:
        print(f"DeepSeek EP期限解析失败: {e}", file=sys.stderr)
    return None


def _ai_parse_cn_deadline(deadline_text, issue_date_str, is_pre_exam=False):
    """用 DeepSeek 将非标准 CN 答复期限文本转为绝限日期(YYYY-MM-DD)。
    计算规则通过提示词传达：起算(预审=发文日当天/非预审=次日)、工作日跳周末+法定节假日。"""
    client = OpenAI(api_key=_DEEPSEEK_API_KEY, base_url=_DEEPSEEK_BASE_URL)
    try:
        _wd = f"（星期{'一二三四五六日'[datetime.strptime(issue_date_str[:10], '%Y-%m-%d').weekday()]}）"
    except Exception:
        _wd = ""
    start_rule = ("预审案件：发文日当天就是第1个工作日（发文日本身算第1天）。"
                  if is_pre_exam else
                  "非预审案件：从发文日的次日开始数第1个工作日（发文日本身不算）。")
    case_hint = "该案为预审案件。" if is_pre_exam else "该案非预审案件。"
    prompt = (
        f"发文日 = {issue_date_str}{_wd}。{case_hint}\n"
        f"答复期限描述 = 「{deadline_text}」。\n"
        "请严格按下列规则计算答复截止日期，务必一步步把工作日数清楚，不要凭感觉：\n"
        f"规则A（起算）：{start_rule}\n"
        "规则B（工作日）：只算周一至周五，且跳过中国法定节假日（元旦/春节/清明/劳动节/端午/中秋/国庆）；周六周日不是工作日。\n"
        "规则C（N个工作日）：从起算日开始按规则B逐日累计，第N个工作日那天即截止日。\n"
        "规则D（N个月）：发文日 + N 个自然月（同一日号）。\n"
        "规则E（明确日期）：若描述本身就是具体日期，直接用它。\n"
        "示例（务必照此数）：预审、发文日是某周五、五个工作日 → 周五=第1、下周一=第2、下周二=第3、下周三=第4、下周四=第5 → 截止日=下周四。\n"
        '只返回 JSON：{"deadline": "YYYY-MM-DD"}；无法判断返回 {"deadline": null}。'
    )
    try:
        resp = client.chat.completions.create(
            model=_DEEPSEEK_MODEL,
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.choices[0].message.content.strip()
        m = re.search(r'\{.*?\}', content, re.DOTALL)
        if m:
            return json.loads(m.group()).get("deadline")
    except Exception as e:
        print(f"DeepSeek CN期限解析失败: {e}", file=sys.stderr)
    return None


def _parse_date(date_str):
    """尝试解析多种日期格式，返回 datetime 或 None。"""
    if not date_str:
        return None
    # ISO 格式：2026-02-14 或 2026-02-14T10:00:00+00:00
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip()[:10], fmt)
        except ValueError:
            continue
    # EP 英文格式：February 12, 2026
    try:
        return datetime.strptime(date_str.strip(), "%B %d, %Y")
    except ValueError:
        pass
    try:
        return datetime.strptime(date_str.strip(), "%B %d %Y")
    except ValueError:
        pass
    return None


def _add_months(dt, months):
    """日期加 N 个月。"""
    month = dt.month + months
    year = dt.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                        31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return dt.replace(year=year, month=month, day=day)


def _move_to_workday(dt):
    """如果落在周末，前移到最近的工作日（周五）。"""
    while dt.weekday() >= 5:  # 5=周六, 6=周日
        dt -= timedelta(days=1)
    return dt


def calc_dueDate(item):
    """
    根据国别和通知类型计算计划送审日。
    返回日期字符串 YYYY-MM-DD 或空字符串。
    """
    project = item.get("project", "")
    country = get_country_code(project)
    notification = item.get("notification_type", "")

    # 发文日
    issue_date = _parse_date(item.get("issue_date", "") or item.get("oa_doc_date", ""))
    # 收到日
    entrust_date = _parse_date(item.get("entrust_date", ""))
    # 答复期限
    deadline_date = _parse_date(item.get("project_deadline", ""))

    if not issue_date:
        return ""

    plan = None

    # CN / CM / CS
    if country in ("CN", "CM", "CS"):
        if deadline_date:
            diff_months = (deadline_date.year - issue_date.year) * 12 + (deadline_date.month - issue_date.month)
            if diff_months >= 4:
                plan = _add_months(issue_date, 2)
            else:
                plan = _add_months(issue_date, 1)
        else:
            # 默认按4月期限算
            plan = _add_months(issue_date, 2)

    # US
    elif country == "US":
        if notification in ("CTAV",):
            # Advisory Action → 查同案号 Final Rejection 的绝限日+1个月
            try:
                from db_query import execute
                sql = (
                    f"SELECT project_deadline FROM projects "
                    f"WHERE project='{project}' AND project_name LIKE '%Final Rejection%' "
                    f"ORDER BY oa_doc_date DESC LIMIT 1"
                )
                rows = execute(sql)
                if rows and rows[0].get("project_deadline"):
                    fr_deadline = _parse_date(str(rows[0]["project_deadline"]))
                    if fr_deadline:
                        deadline_date = _add_months(fr_deadline, 1)
                        item["project_deadline"] = deadline_date.strftime("%Y-%m-%d")
            except Exception as e:
                print(f"[CTAV] 查询Final Rejection绝限日失败: {e}", file=sys.stderr)
            # 送审日：收到日+15天
            if entrust_date:
                plan = entrust_date + timedelta(days=15)
            else:
                plan = issue_date + timedelta(days=15)
        elif notification in ("CTFR",):
            # Final → 收到日+15天
            if entrust_date:
                plan = entrust_date + timedelta(days=15)
            else:
                plan = issue_date + timedelta(days=15)
        else:
            # Non-Final 及其他 → 发文日+45天
            plan = issue_date + timedelta(days=45)

    # EP
    elif country == "EP":
        if deadline_date:
            diff_months = (deadline_date.year - issue_date.year) * 12 + (deadline_date.month - issue_date.month)
            if diff_months >= 6:
                plan = issue_date + timedelta(days=60)
            else:
                plan = issue_date + timedelta(days=40)
        else:
            # 默认按6月期限算
            plan = issue_date + timedelta(days=60)

    # 其他国家
    else:
        plan = _add_months(issue_date, 1)

    if not plan:
        return ""

    # 约束：计划送审日 <= 答复期限-15天
    if deadline_date:
        latest = deadline_date - timedelta(days=15)
        if plan > latest:
            # 取发文日/收到日与期限的中位数
            base = entrust_date or issue_date
            plan = base + (deadline_date - base) / 2

    # 遇周末前移到工作日
    plan = _move_to_workday(plan)

    return plan.strftime("%Y-%m-%d")


# ─── OA 次数查询 ─────────────────────────────────────────

def query_oaNum(project):
    """
    查询案号的下一个 OA 序号。
    从 projects 表中查找 project_name 含 OA{数字} 的记录，取最大值 + 1。
    查询失败时返回 None。
    """
    try:
        from db_query import execute
        sql = f"SELECT * FROM projects WHERE project='{project}'"
        rows = execute(sql)
        if isinstance(rows, str):
            return None

        max_oa = 0
        for row in rows:
            name = row.get("project_name", "") or ""
            m = re.search(r'OA(\d+)', name)
            if m:
                num = int(m.group(1))
                if num > max_oa:
                    max_oa = num

        return max_oa + 1
    except Exception as e:
        print(f"查询 OA 次数失败 ({project}): {e}", file=sys.stderr)
        return None


def fill_oaNum(results):
    """对 needs_oaNum=True 的记录查询并填充 OA 序号。"""
    # 缓存：同一案号只查一次
    cache = {}
    filled = 0

    for item in results:
        if not item.get("needs_oaNum"):
            continue

        project = item.get("project", "")
        if not project:
            continue

        if project not in cache:
            cache[project] = query_oaNum(project)

        oaNum = cache[project]
        if oaNum is not None:
            item["oaNum"] = oaNum
            if item.get("project_name") and "OA{N}" in item["project_name"]:
                item["project_name"] = item["project_name"].replace("OA{N}", f"OA{oaNum}")
            filled += 1
            # 同案号下次查询要 +1（同批邮件中可能有多条同案号）
            cache[project] = oaNum + 1

    print(f"OA 序号填充完成: {filled} 条", file=sys.stderr)
    return results


# ─── CN 规则 ─────────────────────────────────────────────

# 需要立项的 CN 通知类型及对应立项名称
CN_TYPES = {
    "审查意见通知书": lambda subj: _cn_oa_name(subj),
    "复审请求补正通知书": lambda _: "复审补正答复",
    "补正通知书": lambda _: "补正答复",
    "驳回决定": lambda _: "驳回复审评估",
    "办理登记手续通知书": lambda _: "分案评估",
    "复审通知书": lambda _: "复审意见答复",
}

# 办理登记手续通知书：只对这几个客户默认立项做分案评估，其余客户跳过（客户代码 = 案号第一段）
CN_DENGJI_CUSTOMERS = {"20618", "20735"}

# CN 主题正则：日期-通知类型-案号
CN_SUBJECT_RE = re.compile(r'^(\d{4}-\d{2}-\d{2})-(.+?)-(([0-9A-Z]{5}-\w+))$')

# 答复期限正则
CN_DEADLINE_RE = re.compile(r'答复期限[：:]\s*(.+?)[。\s]')


def _cn_oa_name(subject):
    """从主题中提取审查意见次数，生成立项名称。"""
    m = re.search(r'(第[一二三四五六七八九十]+次)审查意见', subject)
    if m:
        return f"{m.group(1)}审查意见答复"
    return "审查意见答复"


def classify_cn(email_data):
    """判断是否为 CN OA 邮件，返回解析结果或 None。"""
    subject = email_data.get("subject", "")
    sender = email_data.get("from", "")

    if "@metis-ip.com" not in sender:
        return None

    # 匹配通知类型
    matched_type = None
    name_fn = None
    for cn_type, fn in CN_TYPES.items():
        if cn_type in subject:
            matched_type = cn_type
            name_fn = fn
            break

    if not matched_type:
        return None

    # 解析主题
    result = {
        "region": "CN",
        "notification_type": matched_type,
        "project_name": name_fn(subject),
        "needs_oaNum": False,
    }

    m = CN_SUBJECT_RE.match(subject.strip())
    if m:
        result["issue_date"] = m.group(1)
        result["project"] = m.group(3)
    else:
        # 尝试从主题中提取案号
        docket_m = re.search(r'([0-9A-Z]{5}-\w{4}[A-Z]{2}\d{2})', subject)
        if docket_m:
            result["project"] = docket_m.group(1)

    # 发文日兜底：主题若是 日期-案号-类型 顺序（CN_SUBJECT_RE 不匹配），抓开头 YYYY-MM-DD 作发文日
    if not result.get("issue_date"):
        _dm = re.match(r'\s*(\d{4}-\d{2}-\d{2})', subject)
        if _dm:
            result["issue_date"] = _dm.group(1)

    # 办理登记手续通知书：仅指定客户立项做分案评估，其余客户跳过（客户代码 = 案号第一段）
    if matched_type == "办理登记手续通知书":
        cust = (result.get("project", "") or "").split("-")[0].strip()
        if cust not in CN_DENGJI_CUSTOMERS:
            return None

    # 从正文提取答复期限
    body = email_data.get("body", "")
    deadline_m = CN_DEADLINE_RE.search(body)
    if deadline_m:
        raw_deadline = deadline_m.group(1).strip()
        # 先尝试直接解析为日期
        if _parse_date(raw_deadline):
            result["project_deadline"] = raw_deadline
        else:
            # 非标准格式（如"五个工作日"、"两个月"），交给 DeepSeek 计算（规则写在提示词里）
            issue_str = result.get("issue_date", "")
            if issue_str:
                _pre = "预审案件" in f"{subject}\n{body}\n{email_data.get('html_body', '')}"
                ai_deadline = _ai_parse_cn_deadline(raw_deadline, issue_str, _pre)
                if ai_deadline:
                    result["project_deadline"] = ai_deadline
                    print(f"[DeepSeek] CN期限: '{raw_deadline}'(预审={_pre}) → {ai_deadline}", file=sys.stderr)
                else:
                    result["project_deadline"] = raw_deadline
            else:
                result["project_deadline"] = raw_deadline

    # 特殊标记
    _full = f"{subject}\n{body}\n{email_data.get('html_body', '')}"
    result["is_pre_exam"] = "预审案件" in _full
    result["is_priority_exam"] = "优先审查" in body
    # 预审案件 + 第一/二次审查意见通知书 → 转OA正文与Wiki备注加注「预审案件」
    if result["is_pre_exam"] and matched_type == "审查意见通知书" \
            and result.get("project_name") in ("第一次审查意见答复", "第二次审查意见答复"):
        result["prescreen_note"] = "预审案件"

    return result


# ─── EP 规则 ─────────────────────────────────────────────

# 需要立项的 EP 通信类型：主题关键词 → (立项名称, 是否单独立项, 是否需要OA序号)
EP_TYPES = {
    "European search report": ("EESR答复", True, True),
    "Communication R.70(2)": (None, False, False),  # 不单独立项，和 EESR 合并
    "Communication A.94(3)": ("Communication Pursuant to Article 94(3) EPC答复", True, True),
    "Intention to grant": ("Communication under Rule 71(3) EPC（授权意向通告）答复", True, False),
    "Further search fee": ("Partial Supplementary European Search Report", True, False),
    "Communication R.62a(1)": ("Communication pursuant to Rule 62a(1) EPC答复", True, False),
    "Summons to oral proceedings": ("Summons to attend oral proceedings pursuant to Rule 115(1)EPC（口头审理通知书）答复", True, True),
}

# EP 主题正则：【通信类型】... (EP号) ... Your Ref.: 案号; Our Ref: 代理号
# 注：Your Ref 值与分号间可能有空格（"EP01 ;"）；Our Ref 可能位于主题结尾、后无分隔符。
EP_SUBJECT_RE = re.compile(
    r'【(.+?)】.*?\((EP\d+\.\d)\).*?Your\s*Ref[.:_\s]+(\S+?)\s*[;,].*?Our\s*Ref[.:_\s]+(\S+?)\s*(?:[;,]|$)',
    re.IGNORECASE
)

# EP 发文日期
EP_ISSUE_DATE_RE = re.compile(r'(?:issued|on)\s+(\w+\s+\d{1,2},?\s*\d{4})', re.IGNORECASE)

# EP 答复期限
EP_DEADLINE_RE = re.compile(r'within\s+(\d+\s+months?)', re.IGNORECASE)


def classify_ep(email_data):
    """判断是否为 EP OA 邮件，返回解析结果或 None。"""
    subject = email_data.get("subject", "")
    sender = email_data.get("from", "")

    if "@panovision-ip.com" not in sender:
        return None

    # 匹配通信类型
    matched_key = None
    for ep_key in EP_TYPES:
        if ep_key.lower() in subject.lower():
            matched_key = ep_key
            break

    if not matched_key:
        return None

    project_name, standalone, needs_oaNum = EP_TYPES[matched_key]

    result = {
        "region": "EP",
        "notification_type": matched_key,
        "project_name": f"OA{{N}}-{project_name}" if needs_oaNum and project_name else project_name,
        "needs_oaNum": needs_oaNum,
        "standalone_project": standalone,
    }

    # 解析主题
    m = EP_SUBJECT_RE.search(subject)
    if m:
        result["ep_number"] = m.group(2)
        result["project"] = m.group(3)
        result["our_ref"] = m.group(4)

    # 是否分案
    result["is_divisional"] = "Divisional" in subject

    # 从正文提取日期和期限
    body = email_data.get("body", "")
    date_m = EP_ISSUE_DATE_RE.search(body)
    if date_m:
        result["issue_date"] = date_m.group(1)

    # 这些类型正文含多种 "within X months"，正则无法区分语义，强制走 DeepSeek
    FORCE_DEEPSEEK_TYPES = {
        "Communication R.70(2)",        # 基准日是公开日非发文日
        "Summons to oral proceedings",  # within X months 指通知期非提交期限
        "Intention to grant",           # within X months 指费用缴纳期非答复期限
    }

    if matched_key in FORCE_DEEPSEEK_TYPES:
        if body.strip():
            ai_result = _ai_parse_ep_deadline(body, result.get("issue_date", ""))
            if ai_result:
                if ai_result.get("deadline"):
                    result["project_deadline"] = ai_result["deadline"]
                # FORCE_DEEPSEEK 类型：DeepSeek 的 issue_date 覆盖正则值
                # 因为正则可能匹配到邮件链中的旧日期
                if ai_result.get("issue_date"):
                    result["issue_date"] = ai_result["issue_date"]
                print(f"[DeepSeek] {matched_key} 期限: {ai_result.get('deadline')}, 发文日: {ai_result.get('issue_date')}", file=sys.stderr)
    else:
        deadline_m = EP_DEADLINE_RE.search(body)
        if deadline_m and result.get("issue_date"):
            months = int(deadline_m.group(1).split()[0])
            issue_dt = _parse_date(result["issue_date"])
            if issue_dt:
                result["project_deadline"] = _add_months(issue_dt, months).strftime("%Y-%m-%d")

        # 正则未提取到期限 → DeepSeek fallback（不依赖 issue_date）
        if not result.get("project_deadline") and body.strip():
            ai_result = _ai_parse_ep_deadline(body, result.get("issue_date", ""))
            if ai_result:
                if ai_result.get("deadline"):
                    result["project_deadline"] = ai_result["deadline"]
                    print(f"[DeepSeek] EP期限: {ai_result['deadline']}", file=sys.stderr)
                if ai_result.get("issue_date") and not result.get("issue_date"):
                    result["issue_date"] = ai_result["issue_date"]
                    print(f"[DeepSeek] EP发文日: {ai_result['issue_date']}", file=sys.stderr)

    return result


# ─── US 规则 ─────────────────────────────────────────────

# 需要立项的 US Document Type → (立项名称, 是否需要OA序号)
US_TYPES_NEED_PROJECT = {
    "CTNF": ("Non-Final Rejection答复", True),
    "CTFR": ("Final Rejection答复", True),
    "NOA": ("分案/续案评估", False),
    "CTAV": ("Advisory Action答复", True),
    "CTRS": ("Requirement for Restriction Election答复", False),
    "EXIN": ("Examiner Interview Summary Record答复", False),
    "PPH.DECISION": ("PPH Decision dismissed补正答复", False),
    "NT.CR.APP.PA": ("Notice to file corrected application papers补正答复", False),
    "NTC.MISS.PRT": ("NOTICE TO FILE MISSING PARTS OF NONPROVISIONAL APPLICATION补正答复", False),
    "PETDEC": ("Petition Decision Dismissed补正答复", False),
    "CTEQ": ("Ex Parte Quayle Action答复", False),
}

# 不需要立项的 US Document Type
US_TYPES_SKIP = {"ISSUE.NTF", "892", "1449", "COCX","ABN","APP.FILE.REC","NTC.PUB","NTC.PUB.DATE","OA.APPENDIX","WELCOME.LET","M327","PREDOCK.NTF","EGRANT.NTF","TRACK1.GRANT"}

# NOA（分案/续案评估）只对这几个客户立项，其它客户的 NOA 跳过（客户代码 = 案号第一段）
NOA_PROJECT_CUSTOMERS = {"20608", "20618", "20849", "20633", "20609"}


class _USTableParser(HTMLParser):
    """解析 USPTO 邮件正文中的 HTML 表格。"""

    def __init__(self):
        super().__init__()
        self._in_td = False
        self._current_row = []
        self._rows = []
        self._current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self._in_td = True
            self._current_text = ""

    def handle_endtag(self, tag):
        if tag == "td":
            self._in_td = False
            self._current_row.append(self._current_text.strip())
        elif tag == "tr":
            if self._current_row:
                self._rows.append(self._current_row)
            self._current_row = []

    def handle_data(self, data):
        if self._in_td:
            self._current_text += data

    def get_rows(self):
        return self._rows


def _parse_us_table_from_text(body):
    """从纯文本中解析 US 邮件的表格结构（备用方案）。"""
    rows = []
    lines = body.split('\n')
    current_row = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('Application') and not stripped.startswith('Document'):
            current_row.append(stripped)
            if len(current_row) == 4:
                rows.append(current_row)
                current_row = []
    return rows


def parse_us_body(body, html_body=""):
    """解析 US 邮件正文中的通知表格，返回案件列表。"""
    rows = []

    # 优先从 HTML 解析
    if html_body:
        parser = _USTableParser()
        parser.feed(html_body)
        rows = parser.get_rows()

    # 如果 HTML 解析无结果，尝试从纯文本解析
    if not rows and body:
        rows = _parse_us_table_from_text(body)

    cases = []
    for row in rows:
        if len(row) >= 4:
            app_no = row[0].strip()
            doc_type = row[1].strip()
            mail_date = row[2].strip()
            project = row[3].strip()

            # 跳过表头
            if app_no.lower().startswith("application") or not app_no[0].isdigit():
                continue

            cases.append({
                "application_no": app_no,
                "document_type": doc_type,
                "oa_doc_date": mail_date,
                "project": project,
            })

    return cases


def classify_us(email_data):
    """判断是否为 US OA 邮件，返回需要立项的案件列表或 None。"""
    subject = email_data.get("subject", "")
    sender = email_data.get("from", "")

    if "noreply@uspto.gov" not in sender and "USPTO" not in subject:
        return None

    # eGrant 授权通知：表格结构与 Correspondence 不同（多 Patent 列会错位），且本就不需要 OA 立项 → 整封跳过
    if "egrant notification" in subject.lower():
        return None

    body = email_data.get("body", "")
    html_body = email_data.get("html_body", "")

    # 解析正文表格
    cases = parse_us_body(body, html_body)
    if not cases:
        return None

    # 筛选需要立项的案件
    results = []
    for case in cases:
        doc_type = case["document_type"]

        if doc_type in US_TYPES_SKIP:
            continue

        # NOA（分案/续案评估）只对指定客户立项，其它客户跳过（客户代码 = 案号第一段）
        if doc_type == "NOA":
            cust = (case.get("project", "") or "").split("-")[0].strip()
            if cust not in NOA_PROJECT_CUSTOMERS:
                continue

        type_info = US_TYPES_NEED_PROJECT.get(doc_type)
        if type_info:
            name, needs_oaNum = type_info
            project_name = f"OA{{N}}-{name}" if needs_oaNum else name
            results.append({
                "region": "US",
                "notification_type": doc_type,
                "project_name": project_name,
                "needs_oaNum": needs_oaNum,
                "application_no": case["application_no"],
                "project": case["project"],
                "oa_doc_date": case["oa_doc_date"],
            })
        else:
            # 未知类型，标记待确认
            results.append({
                "region": "US",
                "notification_type": doc_type,
                "project_name": f"[未知类型] {doc_type}",
                "needs_oaNum": False,
                "application_no": case["application_no"],
                "project": case["project"],
                "oa_doc_date": case["oa_doc_date"],
                "needs_confirmation": True,
            })

    # 同案号下的 892(引用文献通知)/1449(IDS) 行：本身不立项，但挂到该案 OA 立项项，供 dispatch 从 USPTO 下载
    ref_by_project = {}
    for case in cases:
        if case["document_type"] in ("892", "1449"):
            ref_by_project.setdefault(case["project"], []).append({
                "document_code": case["document_type"],
                "application_no": case["application_no"],
                "oa_doc_date": case["oa_doc_date"],
            })
    for item in results:
        refs = ref_by_project.get(item["project"])
        if refs:
            item["us_ref_docs"] = refs

    return results if results else None


# ─── 统一入口 ────────────────────────────────────────────

def classify_email(email_data):
    """
    对单封邮件进行分类和字段提取。
    返回 (result, None) 或 (None, skip_reason)。
    result 为 dict 或 list[dict]（US 一封邮件可能包含多个案件）。
    """
    subject = email_data.get("subject", "").strip()
    sender = email_data.get("from", "").strip()

    # 全局排除（先于区域判断）：这些邮件一律不立项
    if re.match(r'^\s*(re|回复)\s*[:：]', subject, re.IGNORECASE):
        return None, "回复邮件（RE:/回复:），不立项"
    if "reminder" in subject.lower():
        return None, "主题含 reminder，不立项"
    if "向外国申请专利保密审查意见通知书" in subject:
        return None, "向外国申请专利保密审查意见通知书，不立项"

    # 按优先级判断
    # 1. US
    if "noreply@uspto.gov" in sender or "USPTO" in subject:
        us_result = classify_us(email_data)
        if us_result is not None:
            return us_result, None
        return None, "US 邮件但正文中无需立项的 Document Type"

    # 2. EP
    if "@panovision-ip.com" in sender:
        ep_result = classify_ep(email_data)
        if ep_result is not None:
            return ep_result, None
        return None, "EP 邮件但主题未匹配已知通信类型"

    # 3. CN
    if "@metis-ip.com" in sender:
        cn_result = classify_cn(email_data)
        if cn_result is not None:
            return cn_result, None
        return None, "内部邮件但主题未匹配 CN 通知类型"

    return None, "发件人不属于已知来源（非 USPTO/Panovision/Metis）"


def type_oa_remark(notification):
    """按官文类型定「备注」（oa_remark）。其他OA返回 ''，交 dispatch 阶段查 atw 填 同族首案/非同族首案。
      - US NOA / CN 办理登记手续通知书(notification_type='分案评估') → 分案评估
      - 驳回决定 → 驳回复审评估
      - US 补正(NT.CR.APP.PA/NTC.MISS.PRT) / CN 补正通知书·复审请求补正通知书 → 补正
    """
    notification = notification or ""
    if notification in ("NOA", "分案评估"):
        return "分案评估"
    if notification == "驳回决定":
        return "驳回复审评估"
    if notification in ("NT.CR.APP.PA", "NTC.MISS.PRT") or "补正答复" in notification:
        return "补正"
    return ""


def process_emails(emails):
    """批量处理邮件列表，返回筛选结果。"""
    results = []
    ep_pending = []  # 暂存 standalone_project=False 的 EP 记录（如 R.70(2)）
    skipped = 0
    unknown_types = {}  # 未知类型去重统计

    for email_data in emails:
        classified, skip_reason = classify_email(email_data)
        if classified is None:
            skipped += 1
            subj = email_data.get("subject", "").strip()
            frm = email_data.get("from", "").strip()
            to = email_data.get("to", "")
            if isinstance(to, list):
                to = ", ".join(to)
            print(f"[跳过] {skip_reason}", file=sys.stderr)
            print(f"       主题: {subj}", file=sys.stderr)
            print(f"       发件人: {frm} | 收件人: {to}", file=sys.stderr)
            continue

        # US 返回的是列表
        items = classified if isinstance(classified, list) else [classified]
        for item in items:
            item["email_subject"] = email_data.get("subject", "")
            item["entrust_date"] = email_data.get("date", "")
            item["email_from"] = email_data.get("from", "")
            item["attachments"] = email_data.get("attachments", [])
            item["message_id"] = email_data.get("message_id", "")  # 汇报信侧用：关联 saved_pdfs

            # 从案号推导申请类型
            project = item.get("project", "")
            if project:
                item["applytype"] = get_applytype(project)

            item["submitby"] = "AUTO"
            item["now_status"] = "预立项"
            item["project_phase"] = "预立项"

            # issue_date 与 oa_doc_date 互相兜底
            if "issue_date" not in item:
                item["issue_date"] = item.get("oa_doc_date", "")
            if "oa_doc_date" not in item:
                item["oa_doc_date"] = item.get("issue_date", "")

            # 计划送审日
            item["dueDate"] = calc_dueDate(item)

            # oa_remark（备注）：能按类型确定的先定；其他OA留空，dispatch 阶段查 atw 填 同族首案/非同族首案
            item["oa_remark"] = type_oa_remark(item.get("notification_type", ""))

            # standalone_project=False 的 EP 记录（如 R.70(2)/70a(2)）：
            #  · 仍暂存 ep_pending，把期限合并到同案号 EESR 立项记录（立项侧逻辑不变）
            #  · 也进 results：供【汇报信 sink】处理——R.70(2)/70a(2) 是 EESR 汇报信的触发官文；
            #    【立项 sink】dispatch_oa 入口会按 standalone_project=False 过滤掉，行为与原来一致
            if item.get("region") == "EP" and item.get("standalone_project") is False:
                ep_pending.append(item)
                results.append(item)
                continue

            # 统计未知类型
            if item.get("needs_confirmation"):
                doc_type = item.get("notification_type", "")
                if doc_type not in unknown_types:
                    unknown_types[doc_type] = {"count": 0, "docket_samples": []}
                unknown_types[doc_type]["count"] += 1
                docket = item.get("project", "")
                if docket and len(unknown_types[doc_type]["docket_samples"]) < 3:
                    unknown_types[doc_type]["docket_samples"].append(docket)

            results.append(item)

    # R.70(2) 等非独立 EP 记录：合并期限到同案号 EESR
    for pending in ep_pending:
        deadline = pending.get("project_deadline", "")
        project = pending.get("project", "")
        if not deadline or not project:
            print(f"[R.70(2)] {project} 无期限或案号，跳过", file=sys.stderr)
            continue

        # 优先在同批 results 中找同案号 EESR
        merged = False
        for r in results:
            if (r.get("project") == project
                    and r.get("region") == "EP"
                    and "EESR" in (r.get("project_name") or "")):
                if not r.get("project_deadline"):
                    r["project_deadline"] = deadline
                    r["dueDate"] = calc_dueDate(r)
                    print(f"[R.70(2)] {project} 期限 {deadline} 已合并到同批 EESR", file=sys.stderr)
                merged = True
                break

        # 同批没有 EESR → 更新 TIP 数据库
        if not merged:
            try:
                from db_query import execute
                update_sql = (
                    f"UPDATE projects SET project_deadline='{deadline}' "
                    f"WHERE project='{project}' "
                    f"AND project_name LIKE '%EESR%' "
                    f"AND (project_deadline IS NULL OR project_deadline='')"
                )
                # execute(update_sql)
                print(f"[R.70(2)] {project} 期限 {deadline} 已更新到 TIP EESR 记录", file=sys.stderr)
            except Exception as e:
                print(f"[R.70(2)] {project} 更新 TIP EESR 期限失败: {e}", file=sys.stderr)

    # 填充 OA 序号（在字段过滤之前）
    needs_seq = [r for r in results if r.get("needs_oaNum")]
    if needs_seq:
        print(f"\n{len(needs_seq)} 条记录需要查询 OA 序号...", file=sys.stderr)
        fill_oaNum(results)

    # 打印未知类型汇总
    if unknown_types:
        print("\n⚠ 发现以下未知 Document Type（需确认是否立项）:", file=sys.stderr)
        for doc_type, info in sorted(unknown_types.items()):
            samples = ", ".join(info["docket_samples"])
            print(f"  {doc_type}: {info['count']} 条 (示例案号: {samples})", file=sys.stderr)
        print(file=sys.stderr)

    # 日期格式化 + 只保留指定字段
    OUTPUT_FIELDS = [
        "region", "application_no", "notification_type",
        "project", "project_name", "oa_doc_date", "entrust_date",
        "oaNum", "applytype", "project_deadline", "dueDate",
        "now_status", "project_phase", "submitby", "oa_remark",
        "wikiurl", "us_ref_docs", "prescreen_note", "standalone_project",
        # 汇报信侧需要：关联 _inbox 里的官文 PDF
        "message_id", "email_subject", "email_from",
    ]
    DATE_FIELDS = ["oa_doc_date", "entrust_date", "project_deadline", "dueDate"]
    final_results = []
    for item in results:
        for df in DATE_FIELDS:
            val = item.get(df, "")
            if val:
                dt = _parse_date(str(val))
                if dt:
                    item[df] = dt.strftime("%Y-%m-%d")
        # 保留布尔值（standalone_project 等），避免 False 被 `or ""` 变成空串而失去含义
        final_results.append({k: (lambda v: v if isinstance(v, bool) else (v or ""))(item.get(k, ""))
                              for k in OUTPUT_FIELDS})

    return final_results, skipped, unknown_types


# ─── .msg 文件支持 ───────────────────────────────────────

def load_msg_files(msg_dir):
    """从 .msg 文件目录加载邮件数据。"""
    try:
        import extract_msg
    except ImportError:
        print("错误: 需要 extract_msg 库。运行: pip install extract-msg", file=sys.stderr)
        sys.exit(1)

    emails = []
    for f in sorted(os.listdir(msg_dir)):
        if not f.endswith(".msg"):
            continue
        filepath = os.path.join(msg_dir, f)
        msg = extract_msg.Message(filepath)

        body = msg.body or ""
        html_body = ""
        raw_html = msg.htmlBody or b""
        if isinstance(raw_html, bytes):
            html_body = raw_html.decode("utf-8", errors="ignore")

        # 如果 body 为空，从 HTML 提取纯文本（过滤 style/script 标签）
        if not body.strip() and html_body:
            from html.parser import HTMLParser as _HP

            class _TE(_HP):
                def __init__(self):
                    super().__init__()
                    self.t = []
                    self._skip = False

                def handle_starttag(self, tag, attrs):
                    if tag in ("style", "script"):
                        self._skip = True

                def handle_endtag(self, tag):
                    if tag in ("style", "script"):
                        self._skip = False

                def handle_data(self, d):
                    if not self._skip:
                        self.t.append(d)

            te = _TE()
            te.feed(html_body)
            body = "".join(te.t).strip()

        email_data = {
            "subject": msg.subject or "",
            "from": msg.sender or "",
            "to": (msg.to or "").split(";"),
            "cc": (msg.cc or "").split(";") if msg.cc else [],
            "date": str(msg.date or ""),
            "body": body,
            "html_body": html_body,
            "attachments": [
                {
                    "filename": (a.longFilename or a.shortFilename or "").replace("\x00", ""),
                    "content_type": "",
                    "size": 0,
                }
                for a in msg.attachments
            ],
            "source_file": f,
        }
        emails.append(email_data)
        msg.close()

    return emails


# ─── CLI ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="OA 立项邮件筛选脚本")
    parser.add_argument("--input", help="read_email.py 输出的 JSON 文件路径（或 stdin）")
    parser.add_argument("--msg-dir", help=".msg 文件目录路径（测试用）")
    parser.add_argument("--output", help="输出 JSON 文件路径（默认 stdout）")
    args = parser.parse_args()

    # 加载邮件
    if args.msg_dir:
        emails = load_msg_files(args.msg_dir)
        print(f"从 .msg 目录加载了 {len(emails)} 封邮件", file=sys.stderr)
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            emails = json.load(f)
        print(f"从 JSON 文件加载了 {len(emails)} 封邮件", file=sys.stderr)
    else:
        # 从 stdin 读取
        emails = json.load(sys.stdin)
        print(f"从 stdin 加载了 {len(emails)} 封邮件", file=sys.stderr)

    # 筛选
    results, skipped, unknown_types = process_emails(emails)

    # 统计
    stats = {"total": len(emails), "matched": len(results), "skipped": skipped}
    by_region = {}
    for r in results:
        region = r.get("region", "UNKNOWN")
        by_region[region] = by_region.get(region, 0) + 1
    stats["by_region"] = by_region
    if unknown_types:
        stats["unknown_types"] = unknown_types

    print(f"筛选完成: {stats['matched']} 条需立项, {stats['skipped']} 条跳过", file=sys.stderr)
    for region, count in by_region.items():
        print(f"  {region}: {count} 条", file=sys.stderr)

    # 输出
    output = {"stats": stats, "results": results}
    output_json = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"已保存到 {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
