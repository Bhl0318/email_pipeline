#!/usr/bin/env python3
"""
通用邮件读取脚本 — 支持多账号、文件夹选择、时间过滤、结构化 JSON 输出。

用法:
  python3 read_email.py [选项]

选项:
  --account NAME      账号名称，对应 email_config.json 中的 key（默认: docketing）
  --folder FOLDER     IMAP 文件夹（默认: INBOX）
  --since DATE        起始日期，格式 YYYY-MM-DD（默认: 7天前）
  --before DATE       截止日期，格式 YYYY-MM-DD
  --count N           最多读取 N 封（默认: 50）
  --output FILE       输出 JSON 文件路径（默认: 输出到 stdout）
  --list-folders      仅列出该账号所有可用文件夹
  --save-attachments DIR  将附件保存到指定目录

示例:
  # 读取 docketing 最近 7 天的邮件
  python3 read_email.py

  # 读取 attorneys 邮箱 2026-03-01 以来的邮件并保存为 JSON
  python3 read_email.py --account attorneys --since 2026-03-01 --output emails.json

  # 列出 docketing 邮箱的所有文件夹
  python3 read_email.py --list-folders
"""
import sys
import os
import json
import imaplib
import smtplib
import email
import argparse
import re
from datetime import datetime, timedelta
from email.header import decode_header
from email.utils import parsedate_to_datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from html.parser import HTMLParser
from classify_report import process_emails
from db_query import execute_params
import requests
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "email_config.json")
CHECKPOINT_PATH = os.path.join(SCRIPT_DIR, "checkpoint.json")
# 汇报信侧：转达邮件的官文 PDF 临时保存到 _inbox，写库时再移到 output/{案号}/source/
OUTPUT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "output"))
OUTPUT_INBOX_DIR = os.path.join(OUTPUT_DIR, "_inbox")
# 压缩包扩展名：20608 汇报信只需从原邮件补带压缩包文件
_ARCHIVE_EXT = (".zip", ".rar", ".7z")

# 汇报信模板层 (地区,通知类型)→(模板文件名,是否附PDF)：已挪进 oa_report_rules.json 的 `_templates` 段，
# 模块级 REPORT_TYPE_TO_TEMPLATE 在 _load_oa_rules 之后由 _load_report_templates() 构建（见下方）。
# 缺模板的类型不列入 = 不发汇报信；扩展模板改 json 即可，不用动代码。
REVIEW_BASE_URL = "http://10.10.70.88:8501"

# 每封审核链接通知固定抄送
REVIEW_NOTIFY_CC  = ["hailing.bi@metis-ip.com", "dandan.cheng@metis-ip.com", "qin.zhang@metis-ip.com", "yuan.wang@metis-ip.com", "tzhao@metis-ip.com"]

# 汇报信准备人（收审核链接的人）路由：按国别
# 规则：CN 全部→任惠；US/EP→王晶；未命中→不分配（None，不发）。
REPORT_PREPARER_REN  = "hui.ren@metis-ip.com"   # 任惠
REPORT_PREPARER_WANG = "jing.wang@metis-ip.com" # 王晶


def _report_preparer_email(region, project):
    """按国别返回汇报信准备人邮箱：CN→任惠，US/EP→王晶；未命中返回 None（不分配、不发）。
    注：仅作 OA 规则表未命中时的兜底，OA 官文优先走 oa_report_rules.json。"""
    if region == "CN":
        return REPORT_PREPARER_REN
    if region in ("US", "EP"):
        return REPORT_PREPARER_WANG
    return None


# ─── OA 官文规则表（客户 × 官文类型 × 次数 → assign/skip/ignore）─────────
# 源: oa_report_rules.json（由 汇报信规则矩阵-2026-07-30 的 CN/US/EP-OA 三表结构化）
_OA_RULES_CACHE = None
_OA_ORDINAL_RE = re.compile(r'第([一二三四五六七八九十百]+)次')


def _load_oa_rules():
    global _OA_RULES_CACHE
    if _OA_RULES_CACHE is None:
        _OA_RULES_CACHE = _load_oa_rules_impl()
    return _OA_RULES_CACHE


def _load_oa_rules_impl():
    """OA 官文规则来源：先从四表(rules_store 重建，与 JSON 完全同形)读，用它判断是否发汇报信；
    表为空/读库失败 → 回退 oa_report_rules.json（不破坏流水线）。下游解析逻辑不变。"""
    try:
        import rules_store
        d = rules_store.build_oa_rules()
        if d and any(r in d for r in ("CN", "US", "EP")):
            print("[OA规则] 已从数据表加载", file=sys.stderr)
            return d
        print("[OA规则] 数据表为空，回退 oa_report_rules.json", file=sys.stderr)
    except Exception as e:
        print(f"[OA规则] 读表失败，回退 oa_report_rules.json: {e}", file=sys.stderr)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oa_report_rules.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[OA规则] 加载 oa_report_rules.json 失败: {e}", file=sys.stderr)
        return {}


def _load_report_templates():
    """从 oa_report_rules.json 的 `_templates` 段构建 (地区)→(通知类型)→(md文件, 是否附PDF)。
    列表 [md, bool] 转成元组以兼容原用法。缺失/加载失败时返回空 dict（= 都不发汇报信）。"""
    raw = _load_oa_rules().get("_templates", {})
    return {region: {nt: tuple(v) for nt, v in types.items()}
            for region, types in raw.items() if not region.startswith("_")}


# 汇报信模板层（原代码硬编码，现由 oa_report_rules.json 的 _templates 段驱动）
REPORT_TYPE_TO_TEMPLATE = _load_report_templates()


def _oa_ordinal_is_first(item):
    """CN 审查意见是否第一次：从立项名称/主题的"第X次"判，抽不到默认第一次。"""
    m = _OA_ORDINAL_RE.search(item.get("project_name", "") or "")
    return (m.group(1) == "一") if m else True


def _resolve_oa_action(region, ntype, project, item):
    """按 (国别, 官文类型, 客户码, 次数) 查 OA 规则表。
    返回 {"action": "assign"/"skip"/"ignore", ...} 或 None（不在规则表 → 调用方回退旧逻辑）。"""
    region_rules = _load_oa_rules().get(region, {})
    rule_type = ntype
    if region == "CN" and ntype == "审查意见通知书":
        rule_type = "审查意见通知书@1" if _oa_ordinal_is_first(item) else "审查意见通知书@2+"
    # EP Intention to grant：主题含 R.71(3) 时按 EP-其他官文的 Rule 71(3) 规则走（不分配/转发）
    if region == "EP" and ntype == "Intention to grant":
        subj = item.get("email_subject") or ""
        if re.search(r'R\.?\s*71\s*\(\s*3\s*\)|Rule\s*71\s*\(\s*3\s*\)', subj, re.IGNORECASE):
            rule_type = "Intention to grant@R71(3)"
    type_rules = region_rules.get(rule_type)
    if not type_rules:
        return None
    if "*" in type_rules:                       # 所有客户同规则
        return type_rules["*"]
    code = (project or "")[:5]
    rule = type_rules.get(code)                 # 精确客户码优先
    if rule is None and code.startswith("5"):   # 再 5 开头
        rule = type_rules.get("5开头")
    if rule is None:                            # 最后兜底"其他"
        rule = type_rules.get("其他")
    return rule

# USPTO Document Type 代码 → 英文全名（用于汇报信"官文英文名称"字段）
US_DOC_TYPE_FULLNAME = {
    "CTNF":         "Non-Final Office Action",
    "CTFR":         "Final Office Action",
    "CTAV":         "Advisory Action",
    "CTRS":         "Requirement for Restriction Election",
    "CTEQ":         "Ex Parte Quayle Action",
    "NT.CR.APP.PA": "Notice to file corrected application papers",
    "M327":         "Notice to file corrected application papers",
    "NTC.MISS.PRT": "Notice to file missing parts of nonprovisional application",
    "PETDEC":       "Petition Decision Dismissed",
}


def build_report_fields(region, item):
    """按地区构造写入 report_tasks.fields_json 的字段集。
    只放邮件能拿到的字段 + 汇报信特有字段。
    案件主数据（客户名/客户案号/申请号/申请名/申请日）不在这里，
    由 report_server.py 在审核页加载时实时 enrich（查 customer + p_case_info）。"""
    project = item.get("project", "")
    issue_date = item.get("issue_date", "") or item.get("oa_doc_date", "")
    deadline = item.get("project_deadline", "") or item.get("dueDate", "")
    ntype = item.get("notification_type", "")

    # 从 project_name（如"第二次审查意见答复"）提取序数，写入 N 供模板 {{N}} 使用
    _m = re.search(r'第([一二三四五六七八九十百]+)次', item.get("project_name", ""))
    oa_ordinal = _m.group(1) if _m else "一"

    common = {
        "代理所案号": project,
        "通知类型":   ntype,
        "N":          oa_ordinal,
        "签名品牌":   "七星天",
        "发文日期":   issue_date,
        "截止日期":   deadline,
        "期限描述":   "",
        "指示期限":   "",
    }

    if region == "CN":
        return {
            **common,
            # 驳回/复审用（IPEasy p_case_info 暂无对应列，审核人手填）
            "联系人":     "请提供",
            "联系人邮箱": "请提供",
            "联系人手机": "请提供",
            # 复审用
            "复审案件编号": "请提供",
        }

    if region == "US":
        return {
            **common,
            # 流程联系人（模板末尾"如您对此案有流程方面的疑问…"，审核人手填）
            "联系人":     "请提供",
            "联系人邮箱": "请提供",
            "联系人手机": "请提供",
            "申请号":         item.get("application_no", "") or "请提供",
            "递交日":         "请提供",
            "延期描述":       "",
            "延期后截止日期": "",
            "官文英文名称":   US_DOC_TYPE_FULLNAME.get(ntype, ntype),
            "补正类型":       "",
            "补正内容":       "",
            "IDS邮箱":        "IDS@metis-ip.com",
            "案号字段名":     "委托方案号",
        }

    if region == "EP":
        return {
            **common,
            # 流程联系人（模板末尾"如您对此案有流程方面的疑问…"，审核人手填）
            "联系人":     "请提供",
            "联系人邮箱": "请提供",
            "联系人手机": "请提供",
            "申请号":         item.get("ep_number", "") or "请提供",
            "申请日":         "请提供",
            "收文日期":       issue_date,
            "答复通知日期":   "",
            "延期月数":       "",
            "延期后截止日期": "",
            "官文英文名称":   ntype,
            # 检索报告类
            "发明组数":       "",
            "引用文献数":     "",
            "剩余组数":       "",
            "缴费截止日期":   "",
            "每组检索费":     "",
            # 优先权翻译
            "优先权数量":     "",
            "优先权申请号":   "",
            # 预授权
            "授权号":         "",
            "公告日期":       "",
            "生效截止日期":   "",
            "生效指示期限":   "",
            "分案截止日期":   "",
            "指示日期":       "",
            "生效国家列表":   "",
            # 庭审
            "口审日期时间":     "",
            "书面答复截止日期": "",
        }

    return common


# ─── 配置 ───────────────────────────────────────────────

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def set_config_path(path):
    """覆盖 email_config.json 路径。email_pipeline 统一调度时注入共用 config；
    单独运行时不调用，沿用本目录的 email_config.json。"""
    global CONFIG_PATH
    CONFIG_PATH = path


# ─── 断点记录 ────────────────────────────────────────────

def load_checkpoint():
    """加载断点记录。"""
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_checkpoint(data):
    """保存断点记录。"""
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_checkpoint(account, folder):
    """获取指定账号+文件夹的断点信息。"""
    cp = load_checkpoint()
    key = f"{account}:{folder}"
    return cp.get(key, {})


def update_checkpoint(account, folder, emails):
    """处理完成后更新断点：记录最新时间和已处理的 Message-ID。"""
    if not emails:
        return

    cp = load_checkpoint()
    key = f"{account}:{folder}"
    existing = cp.get(key, {})
    old_ids = set(existing.get("processed_ids", []))

    # 收集新的 Message-ID
    new_ids = set()
    latest_time = existing.get("last_time", "")
    for em in emails:
        msg_id = em.get("message_id", "")
        if msg_id:
            new_ids.add(msg_id)
        em_date = em.get("date", "")
        if em_date > latest_time:
            latest_time = em_date

    # 合并 ID，只保留最近 30 天的（按数量限制，最多保留 2000 条）
    all_ids = list(old_ids | new_ids)
    if len(all_ids) > 2000:
        all_ids = all_ids[-2000:]

    cp[key] = {
        "last_time": latest_time,
        "updated_at": datetime.now().isoformat(),
        "processed_ids": all_ids,
    }
    save_checkpoint(cp)
    print(f"断点已更新: {key} | 最新时间: {latest_time} | 已记录 {len(all_ids)} 条 ID", file=sys.stderr)


def filter_new_emails(emails, account, folder):
    """过滤掉已处理过的邮件，返回新邮件列表。"""
    cp = get_checkpoint(account, folder)
    processed_ids = set(cp.get("processed_ids", []))

    if not processed_ids:
        return emails

    new_emails = []
    duplicates = 0
    for em in emails:
        msg_id = em.get("message_id", "")
        if msg_id and msg_id in processed_ids:
            duplicates += 1
            continue
        new_emails.append(em)

    if duplicates:
        print(f"跳过 {duplicates} 封已处理邮件", file=sys.stderr)
    return new_emails


def get_account_config(account_name):
    cfg = load_config()
    accounts = cfg.get("accounts", {})
    if account_name not in accounts:
        print(f"错误: 账号 '{account_name}' 不存在。可用账号: {', '.join(accounts.keys())}")
        sys.exit(1)
    return accounts[account_name]


# ─── 认证 ───────────────────────────────────────────────

def get_oauth2_token(account_cfg):
    oauth = account_cfg.get("oauth2", {})
    if not oauth.get("enabled"):
        return None
    try:
        resp = requests.post(oauth["token_url"], data={
            "client_id": oauth["client_id"],
            "client_secret": oauth["client_secret"],
            "resource": oauth["resource"],
            "username": account_cfg["user"],
            "password": account_cfg["password"],
            "grant_type": "password",
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded",
        })
        data = resp.json()
        if "access_token" in data:
            return data["access_token"]
        print(f"OAuth2 获取 token 失败: {data.get('error_description', data)}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"OAuth2 请求失败: {e}", file=sys.stderr)
        return None


def login_imap(account_cfg):
    # 加 timeout：无超时时服务器无响应会一直挂到 TCP 重传超时(数分钟)才抛 WinError 10060
    imap = imaplib.IMAP4_SSL(account_cfg["imap_host"], account_cfg["imap_port"],
                             timeout=account_cfg.get("imap_timeout", 30))

    token = get_oauth2_token(account_cfg)
    if token:
        auth_string = f"user={account_cfg['user']}\x01auth=Bearer {token}\x01\x01"
        try:
            imap.authenticate("XOAUTH2", lambda x: auth_string.encode())
            return imap
        except Exception as e:
            print(f"OAuth2 IMAP 登录失败，降级到密码认证: {e}", file=sys.stderr)

    imap.login(account_cfg["user"], account_cfg["password"])
    return imap


# ─── 解析工具 ────────────────────────────────────────────

def decode_str(s):
    if s is None:
        return ""
    parts = decode_header(s)
    result = []
    for content, charset in parts:
        if isinstance(content, bytes):
            result.append(content.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(content)
    return "".join(result)


class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._text = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._text.append(data)

    def get_text(self):
        return "".join(self._text).strip()


def html_to_text(html):
    extractor = _HTMLTextExtractor()
    extractor.feed(html)
    return extractor.get_text()


def get_body(msg):
    """提取邮件正文，返回 (纯文本body, 原始html_body)。"""
    plain_body = ""
    html_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain" and not plain_body:
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    plain_body = payload.decode(charset, errors="replace")
            elif content_type == "text/html" and not html_body:
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    html_body = payload.decode(charset, errors="replace")
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        if payload:
            text = payload.decode(charset, errors="replace")
            if msg.get_content_type() == "text/html":
                html_body = text
            else:
                plain_body = text

    # 纯文本：优先 plain，其次从 html 提取
    body = plain_body.strip()
    if not body and html_body.strip():
        body = html_to_text(html_body)

    return body, html_body


def get_attachments(msg):
    """返回附件信息列表: [{filename, content_type, size}]"""
    attachments = []
    if not msg.is_multipart():
        return attachments
    for part in msg.walk():
        disposition = str(part.get("Content-Disposition", ""))
        if "attachment" in disposition or "inline" in disposition:
            filename = decode_str(part.get_filename())
            if not filename:
                continue
            # 清理文件名中的 \x00
            filename = filename.replace("\x00", "")
            payload = part.get_payload(decode=True)
            size = len(payload) if payload else 0
            attachments.append({
                "filename": filename,
                "content_type": part.get_content_type(),
                "size": size,
            })
    return attachments


def _safe_filename(name):
    """清洗附件文件名：去掉折行(\\r\\n\\t)和 Windows 非法字符，避免 open() 报 Errno 22。
    例如 MIME 折行导致的 'Partial European search\\r\\n report.pdf'。"""
    name = re.sub(r'[\r\n\t]+', ' ', name or '')
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:200] or "attachment.pdf"


def _save_pdf_attachments_to_inbox(msg, msg_id, seq):
    """汇报信侧：把转达邮件里的 PDF 附件保存到 OUTPUT_INBOX_DIR/{safe_msgid}/，
    返回保存的路径列表。写库时再移到 output/{案号}/source/。"""
    if not msg.is_multipart():
        return []
    # 目录名 allowlist：只留字母数字和 ._-，其余（含空白/控制字符/@等）一律换 _，防非法路径
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', msg_id or '').strip('_')[:80] or f"seq_{seq}"
    target = os.path.join(OUTPUT_INBOX_DIR, safe)
    saved = []
    for part in msg.walk():
        disposition = str(part.get("Content-Disposition", ""))
        if "attachment" not in disposition and "inline" not in disposition:
            continue
        filename = decode_str(part.get_filename())
        if not filename:
            continue
        filename = _safe_filename(filename)
        if not filename.lower().endswith(".pdf"):
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        os.makedirs(target, exist_ok=True)
        filepath = os.path.join(target, filename)
        with open(filepath, "wb") as f:
            f.write(payload)
        saved.append(filepath)
    return saved


def save_attachments(msg, output_dir):
    """将附件保存到指定目录，返回保存的文件路径列表。"""
    saved = []
    if not msg.is_multipart():
        return saved
    os.makedirs(output_dir, exist_ok=True)
    for part in msg.walk():
        disposition = str(part.get("Content-Disposition", ""))
        if "attachment" not in disposition and "inline" not in disposition:
            continue
        filename = decode_str(part.get_filename())
        if not filename:
            continue
        filename = _safe_filename(filename)
        # 同名直接覆盖（去掉时间戳后缀）
        filepath = os.path.join(output_dir, filename)
        payload = part.get_payload(decode=True)
        if payload:
            with open(filepath, "wb") as f:
                f.write(payload)
            saved.append(filepath)
    return saved


def parse_email_date(msg):
    """解析邮件日期为 ISO 格式字符串。"""
    date_str = msg.get("Date", "")
    if not date_str:
        return ""
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except Exception:
        return date_str


def parse_address_list(header_value):
    """解析收件人/CC 字段为地址列表。"""
    if not header_value:
        return []
    decoded = decode_str(header_value)
    # 简单按逗号或分号分隔
    addresses = re.split(r'[;,]', decoded)
    return [a.strip() for a in addresses if a.strip()]


def parse_message(msg, attachment_dir=None):
    """解析一封邮件为结构化字典。"""
    body, html_body = get_body(msg)
    result = {
        "subject": decode_str(msg.get("Subject", "")),
        "from": decode_str(msg.get("From", "")),
        "to": parse_address_list(msg.get("To")),
        "cc": parse_address_list(msg.get("Cc")),
        "date": parse_email_date(msg),
        # 去折行：Message-ID 头可能被折行含 \r\n\t，清掉内部空白，避免用作路径/IMAP搜索/键值时出错
        "message_id": re.sub(r"\s+", "", msg.get("Message-ID", "") or ""),
        "body": body,
        "html_body": html_body,
        "attachments": get_attachments(msg),
    }

    if attachment_dir:
        result["saved_attachments"] = save_attachments(msg, attachment_dir)

    return result


# ─── 邮件移动 ────────────────────────────────────────────

def move_emails(account_cfg, folder, message_ids, target_folder="TEST_AUTO"):
    """将指定 Message-ID 的邮件从 folder 移动到 target_folder。"""
    if not message_ids:
        return 0

    imap = login_imap(account_cfg)

    # 确保目标文件夹存在，不存在则创建
    imap.create(f'"{target_folder}"')

    # 选择源文件夹（可写模式）
    status, _ = imap.select(f'"{folder}"')
    if status != "OK":
        print(f"错误: 无法打开文件夹 '{folder}'", file=sys.stderr)
        imap.logout()
        return 0

    moved = 0
    for msg_id in message_ids:
        # 按 Message-ID 搜索
        _, nums = imap.search(None, f'HEADER Message-ID "{msg_id}"')
        for num in nums[0].split():
            if not num:
                continue
            # 复制到目标文件夹
            status, _ = imap.copy(num, f'"{target_folder}"')
            if status == "OK":
                # 标记删除原邮件
                imap.store(num, "+FLAGS", "\\Deleted")
                moved += 1

    # 执行删除
    imap.expunge()
    imap.logout()
    print(f"已移动 {moved} 封邮件到 {target_folder}", file=sys.stderr)
    return moved


# ─── 审核任务通知邮件 ────────────────────────────────────

def _get_smtp_oauth2_token(account_cfg):
    """获取 SMTP 用的 OAuth2 token。"""
    oauth = account_cfg.get("oauth2", {})
    if not oauth.get("enabled"):
        return None
    try:
        resp = requests.post(oauth["token_url"], data={
            "client_id": oauth["client_id"],
            "client_secret": oauth["client_secret"],
            "resource": oauth["resource"],
            "username": account_cfg["user"],
            "password": account_cfg["password"],
            "grant_type": "password",
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        data = resp.json()
        if "access_token" in data:
            return data["access_token"]
        print(f"SMTP OAuth2 获取 token 失败: {data.get('error_description', data)}", file=sys.stderr)
    except Exception as e:
        print(f"SMTP OAuth2 请求失败: {e}", file=sys.stderr)
    return None


def _build_review_links_html(links):
    """HTML 表格列出审核链接清单。"""
    today = datetime.now().strftime("%Y-%m-%d")
    rows = ""
    for i, it in enumerate(links):
        bg = "#f9fafb" if i % 2 == 0 else "#ffffff"
        cells = [
            it.get("project", ""),
            it.get("ntype", ""),
            it.get("issue_date", ""),
            f'<a href="{it["link"]}" style="color:#2563eb;text-decoration:none;">打开审核页 &raquo;</a>',
        ]
        row = "".join(
            f'<td style="padding:8px 12px;border:1px solid #e5e7eb;font-size:13px;color:#1e293b;">{c}</td>'
            for c in cells
        )
        rows += f'<tr style="background:{bg};">{row}</tr>\n'

    header_cells = ["代理所案号", "通知类型", "发文日期", "审核链接"]
    header = "".join(
        f'<th style="padding:8px 12px;border:1px solid #e5e7eb;background:#f1f5f9;color:#475569;font-size:13px;text-align:left;">{h}</th>'
        for h in header_cells
    )

    return f"""<html><body style="font-family:'Microsoft YaHei',Arial,sans-serif;color:#1e293b;">
<p>汇报信审核任务自动生成完成，共 <b>{len(links)}</b> 条待审核：</p>
<table style="border-collapse:collapse;border:1px solid #e5e7eb;margin:12px 0;">
<thead><tr>{header}</tr></thead>
<tbody>{rows}</tbody>
</table>
<p style="color:#94a3b8;font-size:12px;margin-top:14px;">生成时间：{today} | 自动发送，请勿直接回复</p>
</body></html>"""


def _send_one_review_email(pa_cfg, to_list, links, cc_list=None):
    """给一个准备人发一封审核链接通知邮件（links 为其名下的任务）。"""
    cc_list = [c for c in (cc_list or []) if c and c not in to_list]
    today = datetime.now().strftime("%Y-%m-%d")
    msg = MIMEMultipart("alternative")
    msg["From"] = pa_cfg["user"]
    msg["To"] = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    msg["Subject"] = f"汇报信审核任务通知 - {today} ({len(links)}条)"
    msg.attach(MIMEText(_build_review_links_html(links), "html", "utf-8"))

    try:
        smtp = smtplib.SMTP(pa_cfg["smtp_host"], pa_cfg["smtp_port"], timeout=30)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        token = _get_smtp_oauth2_token(pa_cfg)
        if token:
            auth_string = f"user={pa_cfg['user']}\x01auth=Bearer {token}\x01\x01"
            try:
                import base64 as _b64
                smtp.docmd("AUTH", "XOAUTH2 " + _b64.b64encode(auth_string.encode()).decode())
            except smtplib.SMTPAuthenticationError:
                print("[审核通知] OAuth2 认证失败，降级到密码认证", file=sys.stderr)
                smtp.login(pa_cfg["user"], pa_cfg["password"])
        else:
            smtp.login(pa_cfg["user"], pa_cfg["password"])

        smtp.sendmail(pa_cfg["user"], to_list + cc_list, msg.as_string())
        smtp.quit()
        print(f"[审核通知] 发送成功: {len(links)} 条 → {', '.join(to_list)}"
              + (f" (CC: {', '.join(cc_list)})" if cc_list else ""), file=sys.stderr)
    except Exception as e:
        print(f"[审核通知] 发送失败 → {', '.join(to_list)}: {e}", file=sys.stderr)


def _smtp_send(pa_cfg, msg, all_rcpts):
    """底层 SMTP 发送（OAuth2 XOAUTH2 优先，认证失败降级密码）。失败抛异常。"""
    smtp = smtplib.SMTP(pa_cfg["smtp_host"], pa_cfg["smtp_port"], timeout=30)
    try:
        smtp.ehlo(); smtp.starttls(); smtp.ehlo()
        token = _get_smtp_oauth2_token(pa_cfg)
        authed = False
        if token:
            import base64 as _b64
            auth_string = f"user={pa_cfg['user']}\x01auth=Bearer {token}\x01\x01"
            code, _ = smtp.docmd("AUTH", "XOAUTH2 " + _b64.b64encode(auth_string.encode()).decode())
            if code == 334:                     # 有 challenge，回空行取最终码
                code, _ = smtp.docmd("")
            authed = (code == 235)
        if not authed:
            smtp.login(pa_cfg["user"], pa_cfg["password"])
        smtp.sendmail(pa_cfg["user"], all_rcpts, msg.as_string())
    finally:
        try: smtp.quit()
        except Exception: pass


def _resolve_forward_targets(addrs, project):
    """把转发目标里的占位「对应案件接口」替换成查库接口人邮箱；其余固定邮箱原样。去重。"""
    out, seen = [], set()
    def _add(m):
        m = (m or "").strip()
        if m and m.lower() not in seen:
            seen.add(m.lower()); out.append(m)
    for a in (addrs or []):
        if a == "对应案件接口":
            try:
                from enrich_report import query_case_interface
                for c in query_case_interface(project):
                    _add(c.get("email"))   # 现在返回 [{name,email}]，取邮箱（空的 _add 会跳过）
            except Exception as e:
                print(f"  [转发] 查接口人失败 {project}: {e}", file=sys.stderr)
        else:
            _add(a)
    return out


def _forward_official_email(pa_cfg, raw_bytes, orig_subject, to_list, cc_list):
    """把原始官文邮件作为 .eml 附件，从 pa 账号 Fwd 给接口人。best-effort。"""
    if os.environ.get("PIPELINE_NO_EMAIL"):
        print(f"  [测试] PIPELINE_NO_EMAIL 已设，跳过转发原始官文：{orig_subject}", file=sys.stderr)
        return
    if not raw_bytes or not to_list:
        if not raw_bytes:
            print(f"  [转发跳过] {orig_subject} 无原始邮件，无法原样转发", file=sys.stderr)
        return
    from email.mime.message import MIMEMessage
    import email as _email
    cc_list = [c for c in (cc_list or []) if c and c not in to_list]
    msg = MIMEMultipart()
    msg["From"] = pa_cfg["user"]
    msg["To"] = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    msg["Subject"] = f"Fwd: {orig_subject}"
    msg.attach(MIMEText("系统自动转发官文邮件，原件见附件。", "plain", "utf-8"))
    try:
        rfc = MIMEMessage(_email.message_from_bytes(raw_bytes))
    except Exception as e:
        print(f"  [转发失败] 原件封装失败 {orig_subject}: {e}", file=sys.stderr)
        return
    rfc.add_header("Content-Disposition", "attachment", filename="original.eml")
    msg.attach(rfc)
    try:
        _smtp_send(pa_cfg, msg, to_list + cc_list)
        print(f"  [转发成功] {orig_subject} → {', '.join(to_list)}"
              + (f" (CC {', '.join(cc_list)})" if cc_list else ""), file=sys.stderr)
    except Exception as e:
        print(f"  [转发失败] {orig_subject} → {', '.join(to_list)}: {e}", file=sys.stderr)


def send_review_links_email(links):
    """按准备人分组，把各自名下的审核链接分别发给对应准备人。"""
    if os.environ.get("PIPELINE_NO_EMAIL"):
        print(f"  [测试] PIPELINE_NO_EMAIL 已设，跳过发送 {len(links or [])} 条审核链接通知", file=sys.stderr)
        return
    if not links:
        print("[审核通知] 无待审核任务，跳过发送", file=sys.stderr)
        return

    cfg = load_config()
    pa_cfg = cfg.get("accounts", {}).get("pa")
    if not pa_cfg:
        print("[审核通知] 未配置 PA 账号，跳过发送", file=sys.stderr)
        return

    # 按准备人邮箱分组；未命中准备人规则（preparer 为空）直接跳过不发
    groups = {}
    for it in links:
        to_email = it.get("preparer")
        if not to_email:
            print(f"  [跳过审核通知] {it.get('project','')} 未命中准备人规则，不发", file=sys.stderr)
            continue
        groups.setdefault(to_email, []).append(it)

    for to_email, group_links in groups.items():
        _send_one_review_email(pa_cfg, [to_email], group_links, cc_list=REVIEW_NOTIFY_CC)


# ─── 主功能 ──────────────────────────────────────────────

def list_folders(account_cfg):
    """列出邮箱所有文件夹。"""
    imap = login_imap(account_cfg)
    status, folders = imap.list()
    if status == "OK":
        for f in folders:
            decoded = f.decode("utf-8", errors="replace")
            print(decoded)
    imap.logout()


def read_emails(account_cfg, folder="INBOX", since=None, before=None,
                count=50, attachment_dir=None, account_name=None):
    """读取邮件，返回结构化列表。"""
    imap = login_imap(account_cfg)

    # 选择文件夹
    status, _ = imap.select(f'"{folder}"', readonly=True)
    if status != "OK":
        print(f"错误: 无法打开文件夹 '{folder}'", file=sys.stderr)
        imap.logout()
        return []

    # 构建 IMAP 搜索条件
    criteria = []
    if since:
        criteria.append(f'SINCE {since.strftime("%d-%b-%Y")}')
    if before:
        criteria.append(f'BEFORE {before.strftime("%d-%b-%Y")}')

    search_query = " ".join(criteria) if criteria else "ALL"
    _, msg_nums = imap.search(None, search_query)
    msg_list = msg_nums[0].split()

    if not msg_list:
        print("没有符合条件的邮件", file=sys.stderr)
        imap.logout()
        return []

    # 取最新的 count 封
    if len(msg_list) > count:
        msg_list = msg_list[-count:]

    # 从新到旧
    msg_list.reverse()

    results = []
    for i, num in enumerate(msg_list):
        _, data = imap.fetch(num, "(RFC822)")
        raw = data[0][1]
        msg = email.message_from_bytes(raw)
        parsed = parse_message(msg, attachment_dir)
        parsed["seq"] = i + 1
        parsed["raw_bytes"] = raw   # 原始 MIME，供二期"原样转发"用
        # 汇报信侧扩展：保存 PDF 附件到 _inbox，留待写库时移到 output/{案号}/source/
        parsed["saved_pdfs"] = _save_pdf_attachments_to_inbox(msg, parsed.get("message_id", ""), i + 1)
        results.append(parsed)

        # 进度提示
        if (i + 1) % 10 == 0:
            print(f"已读取 {i + 1}/{len(msg_list)} 封...", file=sys.stderr)

    print(f"共读取 {len(results)} 封邮件", file=sys.stderr)
    imap.logout()

    # 过滤已处理的邮件
    if account_name:
        results = filter_new_emails(results, account_name, folder)
        print(f"其中 {len(results)} 封为新邮件", file=sys.stderr)

    return results


# ─── CLI ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="通用邮件读取脚本")
    parser.add_argument("--account", default="docketing", help="账号名称（默认: docketing）")
    parser.add_argument("--folder", default="INBOX", help="IMAP 文件夹（默认: INBOX）")
    parser.add_argument("--since", help="起始日期 YYYY-MM-DD（默认: 7天前）")
    parser.add_argument("--before", help="截止日期 YYYY-MM-DD")
    parser.add_argument("--count", type=int, default=50, help="最多读取数量（默认: 50）")
    parser.add_argument("--output", help="输出 JSON 文件路径")
    parser.add_argument("--list-folders", action="store_true", help="列出所有文件夹")
    parser.add_argument("--save-attachments", help="附件保存目录")
    args = parser.parse_args()

    account_cfg = get_account_config(args.account)

    # 列出文件夹模式
    if args.list_folders:
        list_folders(account_cfg)
        return

    # 解析日期：优先用命令行参数，其次用断点时间，最后默认 7 天前
    since = None
    if args.since:
        since = datetime.strptime(args.since, "%Y-%m-%d")
    else:
        cp = get_checkpoint(args.account, args.folder)
        last_time = cp.get("last_time", "")
        if last_time:
            try:
                since = datetime.fromisoformat(last_time) - timedelta(hours=1)  # 多回溯1小时防遗漏
                print(f"从断点继续: {since.isoformat()}", file=sys.stderr)
            except ValueError:
                since = datetime.now() - timedelta(days=200)
        else:
            since = datetime.now() - timedelta(days=200)

    before = None
    if args.before:
        before = datetime.strptime(args.before, "%Y-%m-%d")

    # 读取邮件
    results = read_emails(
        account_cfg,
        folder=args.folder,
        since=since,
        before=before,
        count=args.count,
        attachment_dir=args.save_attachments,
        account_name=args.account,
    )

    # 更新断点
    if results:
        update_checkpoint(args.account, args.folder, results)

    # 输出
    output_json = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"已保存到 {args.output}", file=sys.stderr)
    else:
        print(output_json)


# ─── email_pipeline 统一调度入口 ──────────────────────────
# 原 __main__ 批处理逻辑拆成三个函数，便于 email_pipeline 单次读取后扇出复用。
# 单独运行（python read_email.py）行为不变：见文件末尾 __main__。

# 默认读取的邮箱账号 + 文件夹（单独跑时用；email_pipeline 会从 pipeline_config.json 传入）
DEFAULT_ACCOUNTS = [
    {"account": "docketing", "folder": "TEST"},
    # {"account": "attorneys", "folder": "TEST"}
]

# 无 checkpoint 时的回溯窗口（天）。设计为每天定时运行，首次/丢断点只读最近 1 天，
# 不拉历史；有 checkpoint 时仍按断点增量读，漏跑一天下次会自动补上，不漏邮件。
LOOKBACK_DAYS = 1


def read_and_classify(accounts=None, config_path=None):
    """读邮件 + 分类。供单独运行和 email_pipeline 统一调度共用。
    返回 (all_emails, all_results):
      all_emails:  list[(acc_dict, email_dict)]  保留 acc 以便归档时按账号 move
      all_results: list[result_dict]
    config_path 不为空时覆盖共用 email_config.json 路径（email_pipeline 注入）。"""
    if config_path:
        set_config_path(config_path)
    if accounts is None:
        accounts = DEFAULT_ACCOUNTS

    all_emails = []
    all_results = []

    for acc in accounts:
        account_name = acc["account"]
        folder = acc["folder"]
        print(f"\n{'='*40}", file=sys.stderr)
        print(f"读取邮箱: {account_name} / {folder}", file=sys.stderr)

        # 读取断点
        cp = get_checkpoint(account_name, folder)
        last_time = cp.get("last_time", "")
        if last_time:
            try:
                since = datetime.fromisoformat(last_time) - timedelta(hours=1)
                print(f"从断点继续: {since.isoformat()}", file=sys.stderr)
            except ValueError:
                since = datetime.now() - timedelta(days=LOOKBACK_DAYS)
        else:
            since = datetime.now() - timedelta(days=LOOKBACK_DAYS)

        # 读取邮件
        cfg = get_account_config(account_name)
        emails = read_emails(cfg, folder=folder, since=since, account_name=account_name)

        # 更新断点（记入 processed_ids + last_time：未命中邮件不移动，靠此去重避免下次重复读）
        if emails:
            update_checkpoint(account_name, folder, emails)

        # 邮件分类
        results, skipped, unknown_types = process_emails(emails)

        # 建索引：msgid → saved_pdfs（汇报信侧用，写库时移到 output/{案号}/source/）
        msgid_to_saved_pdfs = {
            em.get("message_id", ""): em.get("saved_pdfs", [])
            for em in emails if em.get("saved_pdfs")
        }
        # 诊断：有多少封邮件落了 PDF 到 _inbox
        _inbox_total = sum(len(v) for v in msgid_to_saved_pdfs.values())
        print(f"[官文 PDF] _inbox 已落 {len(msgid_to_saved_pdfs)} 封邮件 / {_inbox_total} 个 PDF", file=sys.stderr)
        if msgid_to_saved_pdfs:
            sample = next(iter(msgid_to_saved_pdfs.keys()))
            print(f"          示例 msgid: {sample!r}", file=sys.stderr)

        # 打印每封识别到的邮件类型
        print(f"\n--- {account_name}/{folder} 分类结果（识别 {len(results)} / 跳过 {skipped} / 共 {len(emails)} 封） ---", file=sys.stderr)
        for r in results:
            region = r.get("region", "?")
            ntype = r.get("notification_type", "?")
            project = r.get("project", "")
            subj = (r.get("email_subject") or "").strip().replace("\n", " ")
            if len(subj) > 60:
                subj = subj[:59] + "…"
            if region == 'CN':
                print(f"  [{region}] {ntype:<20} {project:<22} {subj}", file=sys.stderr)

        all_emails.extend([(acc, em) for em in emails])
        all_results.extend(results)

    return all_emails, all_results


def dispatch_report(all_results, all_emails, dry_run=False):
    """汇报信下游 sink：官文 PDF 入库 + 写 report_tasks + 发审核链接邮件。
    all_emails 用于重建 msgid → saved_pdfs 索引（跨账号，message_id 全局唯一）。
    注：email_pipeline 模式下本函数不再 move 邮件，归档统一交 archive_emails。
    dry_run=True 时：照常分类/打印，但不移 PDF、不写 report_tasks、不发邮件。"""
    # 重建 msgid → saved_pdfs 索引
    msgid_to_saved_pdfs = {
        em.get("message_id", ""): em.get("saved_pdfs", [])
        for (_acc, em) in all_emails if em.get("saved_pdfs")
    }
    # msgid → 原始邮件（二期"原样转发"用其 raw_bytes）
    msgid_to_email = {em.get("message_id", ""): em for (_acc, em) in (all_emails or [])}
    _fwd_pa_cfg = load_config().get("accounts", {}).get("pa")   # 转发从 pa 账号发

    all_review_links = []  # 收集所有审核链接，最后统一发一封通知邮件
    report_actions = []    # 本次汇报信动作 [{message_id, project, action}]，供 main.py 汇总写邮件动作页

    # 写入 TIP 系统（projects 表）
    if all_results:
        from db_query import execute as db_execute
        inserted = 0
        for item in all_results:
            project = item.get("project", "")
            project_name = item.get("project_name", "")
            if not project or not project_name:
                continue
            # 检查是否已存在
            # check_sql = f"SELECT COUNT(*) as cnt FROM projects WHERE project='{project}' AND project_name='{project_name}'"
            # try:
            #     check = db_execute(check_sql)
            #     if check and check[0].get("cnt", 0) > 0:
            #         print(f"[TIP] {project} {project_name} 已存在，跳过", file=sys.stderr)
            #         continue
            # except Exception:
            #     pass

            # 构建 INSERT
            import uuid
            row_id = str(uuid.uuid4())
            fields = ["id", "project", "project_name", "oa_doc_date", "entrust_date",
                       "oaNum", "applytype", "project_deadline", "dueDate",
                       "now_status", "project_phase", "submitby", "oa_remark", "wikiurl"]
            values = []
            for f in fields:
                if f == "id":
                    values.append(row_id)
                    continue
                v = item.get(f, "")
                if v is None:
                    v = ""
                # oa_doc_date 为 date 类型，空值用 NULL
                if f == "oa_doc_date" and not v:
                    values.append("__NULL__")
                    continue
                values.append(str(v).replace("'", "\\'"))

            # cols = ", ".join(fields)
            # vals = ", ".join("NULL" if v == "__NULL__" else f"'{v}'" for v in values)
            # insert_sql = f"INSERT INTO projects ({cols}) VALUES ({vals})"
            # try:
            #     db_execute(insert_sql)
            #     inserted += 1
            #     print(f"[TIP] {project} {project_name} 写入成功", file=sys.stderr)
            # except Exception as e:
            #     print(f"[TIP] {project} {project_name} 写入失败: {e}", file=sys.stderr)

            # 汇报信：CN/US/EP 三个地区，类型在 REPORT_TYPE_TO_TEMPLATE 映射里 → 用同 row_id 写 report_tasks
            region = item.get("region", "")
            ntype = item.get("notification_type", "")
            tpl_info = REPORT_TYPE_TO_TEMPLATE.get(region, {}).get(ntype)
            # OA 规则表决策（客户×类型×次数）：assign 分配 / skip 不分配(记转发) / ignore 不处理
            preparer_override = None
            if tpl_info:
                action = _resolve_oa_action(region, ntype, project, item)
                if action is None:
                    # 不在 OA 规则表 → 回退旧逻辑：CN 5 开头跳过
                    if region == "CN" and project.startswith("5"):
                        print(f"  [跳过汇报信] CN 5开头客户 {project}（{ntype}）不分配汇报信", file=sys.stderr)
                        tpl_info = None
                else:
                    act = action.get("action")
                    if act == "ignore":
                        tpl_info = None
                    elif act == "skip":
                        fwd = action.get("forward") or {}
                        fwd_to = _resolve_forward_targets(fwd.get("to"), project)
                        fwd_cc = _resolve_forward_targets(fwd.get("cc"), project)
                        print(f"  [规则-skip] {project} {ntype} 不分配汇报信，转发 to={fwd_to} cc={fwd_cc}", file=sys.stderr)
                        if fwd_to:   # 解析到转发地址才算「转发原始」动作
                            report_actions.append({"message_id": item.get("message_id", ""),
                                                   "project": project, "action": "转发原始",
                                                   "reason": f"OA规则表skip不分配汇报信→转发接口人({ntype})"})
                        if not dry_run and fwd_to and _fwd_pa_cfg:
                            em = msgid_to_email.get(item.get("message_id", ""))
                            _forward_official_email(
                                _fwd_pa_cfg,
                                em.get("raw_bytes") if em else None,
                                (em.get("subject") if em else "") or item.get("email_subject") or ntype,
                                fwd_to, fwd_cc)
                        elif not fwd_to:
                            print(f"  [转发跳过] {project} {ntype} 未解析到接口人/转发地址", file=sys.stderr)
                        tpl_info = None
                    elif act == "assign":
                        preparer_override = action.get("preparer")
                        # 双动作：分配汇报信的同时，把原始官文再转发一份（如韶音 20608 发 shokz+赵彤）
                        also = action.get("also_forward")
                        if also and not dry_run and _fwd_pa_cfg:
                            af_to = _resolve_forward_targets(also.get("to"), project)
                            af_cc = _resolve_forward_targets(also.get("cc"), project)
                            if af_to:
                                em = msgid_to_email.get(item.get("message_id", ""))
                                print(f"  [assign+转发] {project} {ntype} 分配 {preparer_override} 并转发 to={af_to} cc={af_cc}", file=sys.stderr)
                                _forward_official_email(
                                    _fwd_pa_cfg,
                                    em.get("raw_bytes") if em else None,
                                    (em.get("subject") if em else "") or item.get("email_subject") or ntype,
                                    af_to, af_cc)
            if tpl_info:
                report_actions.append({"message_id": item.get("message_id", ""),
                                       "project": project, "action": "分配汇报信",
                                       "reason": f"命中汇报信模板:{region}/{ntype}"})
                template, attach_pdf = tpl_info
                report_fields = build_report_fields(region, item)
                # 注：客户名/申请号/申请名/申请日/客户案号 等案件主数据不在这里填，
                #     由 report_server.py 在审核页加载时实时 enrich（保证拿最新数据）

                # 把该邮件的官文 PDF 从 _inbox 移到 output/{案号}/source/
                source_attachments = []
                item_msgid = item.get("message_id", "")
                src_pdfs = msgid_to_saved_pdfs.get(item_msgid, [])
                if not src_pdfs:
                    if not item_msgid:
                        print(f"  [无官文 PDF] item.message_id 为空——classify_report.py 可能未拉最新版（缺 line 760）", file=sys.stderr)
                    elif msgid_to_saved_pdfs:
                        print(f"  [无官文 PDF] msgid={item_msgid!r} 在 _inbox 索引中没找到（msgid 串不一致？）", file=sys.stderr)
                elif not project:
                    print(f"  [无官文 PDF] item.project 为空，不知道往哪个案号搬", file=sys.stderr)
                else:
                    case_source_dir = os.path.join(OUTPUT_DIR, project, "source")
                    os.makedirs(case_source_dir, exist_ok=True)
                    for src in src_pdfs:
                        if not os.path.exists(src):
                            print(f"  [跳过] 源 PDF 不存在: {src}", file=sys.stderr)
                            continue
                        fname = os.path.basename(src)
                        dst = os.path.join(case_source_dir, fname)
                        try:
                            if dry_run:
                                print(f"  [dry-run] 跳过移动官文 PDF: {fname}", file=sys.stderr)
                            else:
                                shutil.move(src, dst)
                            # 相对 output/ 的路径，confirm 时拼绝对路径
                            rel = f"{project}/source/{os.path.basename(dst)}"
                            source_attachments.append(rel)
                        except Exception as e:
                            print(f"  [移动官文 PDF 失败] {src}: {e}", file=sys.stderr)

                # 20608(韶音)：OA 汇报信需带上原邮件的压缩包文件。
                # PDF 已由上面的 _inbox 流程移入 source；这里从原邮件 raw_bytes 补出压缩包。
                # 与 OA 立项侧 send_forward_oa 的 20608 处理保持一致(均只补带压缩包)。
                if project and project[:5] == "20608":
                    em = msgid_to_email.get(item_msgid)
                    raw = em.get("raw_bytes") if em else None
                    if raw:
                        try:
                            orig_msg = email.message_from_bytes(raw)
                            case_source_dir = os.path.join(OUTPUT_DIR, project, "source")
                            added = []
                            # 任何带文件名的 part 都看(不依赖 Content-Disposition)，只留压缩包
                            for part in orig_msg.walk():
                                if part.get_content_maintype() == "multipart":
                                    continue
                                fname = decode_str(part.get_filename())
                                if not fname:
                                    continue
                                fname = _safe_filename(fname)
                                if not fname.lower().endswith(_ARCHIVE_EXT):
                                    continue
                                rel = f"{project}/source/{fname}"
                                if rel in source_attachments:
                                    continue
                                if dry_run:
                                    added.append(fname)
                                    continue
                                payload = part.get_payload(decode=True)
                                if not payload:
                                    continue
                                os.makedirs(case_source_dir, exist_ok=True)
                                with open(os.path.join(case_source_dir, fname), "wb") as fh:
                                    fh.write(payload)
                                source_attachments.append(rel)
                                added.append(fname)
                            if added:
                                tag = "dry-run 将补带压缩包" if dry_run else "汇报信补带原邮件压缩包"
                                print(f"  [20608] {tag}: {added}", file=sys.stderr)
                        except Exception as e:
                            print(f"  [20608 附件补带失败] {item_msgid}: {e}", file=sys.stderr)

                # US 官文 PDF 不走邮件附件：uspto.gov 通知邮件常不带 PDF，官文由 OA sink
                # 经 USPTO API 下载（item['us_pdf_path']）。把它也并入审核任务附件。
                # 依赖 OA sink 先于本 sink 跑（main.py 已保证）；OA 关或没下到则无此附件。
                us_pdf = item.get("us_pdf_path", "")
                if us_pdf and project:
                    if not os.path.exists(us_pdf):
                        print(f"  [US官文PDF] 路径不存在，跳过: {us_pdf}", file=sys.stderr)
                    else:
                        case_source_dir = os.path.join(OUTPUT_DIR, project, "source")
                        os.makedirs(case_source_dir, exist_ok=True)
                        dst = os.path.join(case_source_dir, os.path.basename(us_pdf))
                        rel = f"{project}/source/{os.path.basename(dst)}"
                        if rel not in source_attachments:
                            try:
                                if dry_run:
                                    print(f"  [dry-run] 跳过复制 US 官文 PDF: {os.path.basename(us_pdf)}", file=sys.stderr)
                                else:
                                    shutil.copy2(us_pdf, dst)  # 复制非移动：OA 已用它上传 Wiki，保留原件
                                source_attachments.append(rel)
                            except Exception as e:
                                print(f"  [复制 US 官文 PDF 失败] {us_pdf}: {e}", file=sys.stderr)

                review_link = f"{REVIEW_BASE_URL}/review/{row_id}"
                if dry_run:
                    print(f"  [dry-run] 将写 report_tasks（template={template}, attach_pdf={attach_pdf}, 官文PDF×{len(source_attachments)}）", file=sys.stderr)
                    print(f"  [dry-run] 审核链接: {review_link}", file=sys.stderr)
                    all_review_links.append({
                        "link":       review_link,
                        "project":    project,
                        "ntype":      ntype,
                        "issue_date": item.get("issue_date", "") or item.get("oa_doc_date", ""),
                        "preparer":   preparer_override or _report_preparer_email(region, project),
                    })
                else:
                    try:
                        execute_params(
                            "INSERT INTO report_tasks (id, template, attach_pdf, fields_json, source_attachments, status) "
                            "VALUES (%s, %s, %s, %s, %s, 'pending')",
                            (row_id, template, 1 if attach_pdf else 0,
                             json.dumps(report_fields, ensure_ascii=False),
                             json.dumps(source_attachments, ensure_ascii=False) if source_attachments else None),
                        )
                        print(f"  → 审核链接: {review_link}", file=sys.stderr)
                        if source_attachments:
                            print(f"    附 {len(source_attachments)} 个官文 PDF", file=sys.stderr)
                        # 收集到通知邮件列表
                        all_review_links.append({
                            "link":       review_link,
                            "project":    project,
                            "ntype":      ntype,
                            "issue_date": item.get("issue_date", "") or item.get("oa_doc_date", ""),
                            "preparer":   preparer_override or _report_preparer_email(region, project),
                        })
                    except Exception as e:
                        print(f"  [report_tasks 写库失败] {e}", file=sys.stderr)

        print(f"TIP 写入完成: {inserted} 条", file=sys.stderr)

    # 所有任务写完，统一发审核任务通知邮件
    if dry_run:
        print(f"[dry-run] 跳过发送审核链接邮件（本应汇总 {len(all_review_links)} 条）", file=sys.stderr)
    else:
        send_review_links_email(all_review_links)

    return report_actions


def archive_emails(all_emails, all_results=None, dry_run=False):
    """单次归档：仅把分类命中的邮件 move 到 TEST_AUTO；未命中（既非OA也非汇报信）的保持不动。

    命中判定按 message_id 是否出现在 all_results（read_and_classify 的分类结果，OA/汇报信共用）。
    all_results 不传时退回旧行为：全部按命中处理（兼容单 sink 直调）。
    未命中邮件不移动（留在原文件夹），靠 checkpoint 去重避免下次重复处理。
    email_pipeline 模式下归档只在这里发生一次（各 sink 内不再 move）。
    dry_run=True 时只打印不真正 move。"""
    matched_mids = {item.get("message_id", "") for item in (all_results or []) if item.get("message_id")}
    # groups[(account, folder)] = [acc, 命中 mids[], 未命中计数]
    groups = {}
    for acc, em in all_emails:
        key = (acc["account"], acc["folder"])
        if key not in groups:
            groups[key] = [acc, [], 0]
        mid = em.get("message_id", "")
        if not mid:
            continue
        # all_results 未提供 → 一律按命中（旧行为：全归 TEST_AUTO）
        if all_results is None or mid in matched_mids:
            groups[key][1].append(mid)
        else:
            groups[key][2] += 1  # 未命中：不动
    for (account_name, folder), (acc, matched, skipped_n) in groups.items():
        # no_archive 文件夹（如 Done 归档夹）：命中/未命中都不移动，只读，靠 checkpoint 去重
        if acc.get("no_archive"):
            print(f"  {account_name}/{folder} no_archive：命中 {len(matched)} + 未命中 {skipped_n} 封全部留原处", file=sys.stderr)
            continue
        if skipped_n:
            print(f"  未命中 {skipped_n} 封保持不动（{account_name}/{folder}）", file=sys.stderr)
        if not matched:
            continue
        if dry_run:
            print(f"  [dry-run] 跳过归档 {len(matched)} 封（{account_name}/{folder} → TEST_AUTO）", file=sys.stderr)
            continue
        cfg = get_account_config(account_name)
        move_emails(cfg, folder, matched, target_folder="TEST_AUTO")


if __name__ == "__main__":
    # 单独运行：读取 → 分类 → 汇报信下游 → 归档
    _all_emails, _all_results = read_and_classify()
    dispatch_report(_all_results, _all_emails)
    archive_emails(_all_emails, _all_results)
