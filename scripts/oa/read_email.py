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
from filter_oa_email import process_emails
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "email_config.json")
CHECKPOINT_PATH = os.path.join(SCRIPT_DIR, "checkpoint.json")

# CN/EP 邮件主官文识别关键词（多附件时挑通知书/决定/官文那份）
_OFFICIAL_TITLE_KEYS = ("通知书", "决定", "审查意见", "补正", "复审",
                        "Communication", "Office Action", "Search Report",
                        "Examination", "Intention", "Rejection", "Notice")


def _pick_main_official_pdf(saved_pdfs):
    """从一封邮件的官文 PDF 里挑「主官文」那份：唯一则用它；多份按标题关键词命中；否则取第一份。"""
    pdfs = [p for p in (saved_pdfs or [])
            if p and p.lower().endswith(".pdf") and os.path.exists(p)]
    if not pdfs:
        return None
    if len(pdfs) == 1:
        return pdfs[0]
    for p in pdfs:
        name = os.path.basename(p)
        if any(k in name for k in _OFFICIAL_TITLE_KEYS):
            return p
    return pdfs[0]


def _official_doc_for_subpage(item, saved_pdfs):
    """返回该案要转成 Wiki 子页的主官文文件：
    US → 主官文有 Word 用 Word，否则用主官文 PDF；CN/EP → 邮件主官文 PDF。其余/无 → None。"""
    region = item.get("region")
    if region == "US":
        docx = [d for d in (item.get("us_doc_paths") or [])
                if d and d.lower().endswith(".docx") and os.path.exists(d)]
        if docx:
            return docx[0]
        _pdf = item.get("us_pdf_path")
        return _pdf if _pdf and os.path.exists(_pdf) else None
    if region in ("CN", "EP"):
        return _pick_main_official_pdf(saved_pdfs)
    return None


def _download_case_publication(project):
    """按本案公开号从 FPO 下载公布文本 PDF，存 attachment/{案号}/{公开号}.pdf。
    返回路径或 None（best-effort：取不到公开号/下载失败均静默跳过，不阻断上传）。"""
    project = (project or "").strip()
    if not project:
        return None
    try:
        from oainfo_cli import find_project_info
        _, pub_no = find_project_info(project)   # (案件名, 公开号)
    except Exception as e:
        print(f"[公布文本] {project} 取公开号失败: {e}", file=sys.stderr)
        return None
    pub_no = (pub_no or "").strip()
    if not pub_no:
        return None
    # 用公开号做文件名，去掉空格/斜杠等非法字符（如 'US 2025/0150762 A1' → 'US20250150762A1'）
    safe_pub = re.sub(r'[\\/:*?"<>|\s]', '', pub_no)
    attach_dir = os.path.join(SCRIPT_DIR, "..", "..", "attachment", project)
    out = os.path.join(attach_dir, f"{safe_pub}.pdf")
    if os.path.exists(out):
        return out
    try:
        os.makedirs(attach_dir, exist_ok=True)
        from download_patent_pdf import download_patent_pdf
        return download_patent_pdf(pub_no, out)
    except Exception as e:
        print(f"[公布文本] {project} 下载失败({pub_no}): {e}", file=sys.stderr)
        return None


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
        filename = filename.replace("\x00", "")
        # 避免文件名冲突
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filepath = os.path.join(output_dir, f"{name}_{datetime.now().strftime('%H%M%S')}{ext}")
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


# ─── 通知邮件 ────────────────────────────────────────────

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


def _build_notification_html(results):
    """将立项结果构建为 HTML 邮件正文。"""
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 表头字段
    columns = [
        ("国家", "region"),
        ("案号", "project"),
        ("立项名称", "project_name"),
        ("OA序号", "oaNum"),
        ("发文日", "oa_doc_date"),
        ("收到日", "entrust_date"),
        ("答复期限", "project_deadline"),
        ("计划送审日", "dueDate"),
        ("申请类型", "applytype"),
        ("状态", "now_status"),
        ("备注", "oa_remark"),
    ]

    header = "".join(
        f'<th style="padding:6px 10px;border:1px solid #ddd;background:#4472C4;color:#fff;'
        f'font-size:13px;white-space:nowrap;">{col[0]}</th>'
        for col in columns
    )

    rows = ""
    for i, item in enumerate(results):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        cells = ""
        for _, key in columns:
            val = item.get(key, "") or ""
            cells += f'<td style="padding:5px 10px;border:1px solid #ddd;font-size:13px;">{val}</td>'
        rows += f'<tr style="background:{bg};">{cells}</tr>\n'

    html = f"""<html><body style="font-family:Microsoft YaHei,Arial,sans-serif;">
<p>OA 立项自动化处理完成，共 <b>{len(results)}</b> 条立项结果：</p>
<table style="border-collapse:collapse;border:1px solid #ddd;margin:10px 0;">
<thead><tr>{header}</tr></thead>
<tbody>{rows}</tbody>
</table>
<p style="color:#888;font-size:12px;">发送时间：{today} | 自动发送，请勿直接回复</p>
</body></html>"""

    return html


def send_notification(results):
    """发送立项结果汇总邮件。"""
    if not results:
        print("[通知邮件] 无立项结果，跳过发送", file=sys.stderr)
        return

    cfg = load_config()
    pa_cfg = cfg.get("accounts", {}).get("pa")
    notif = cfg.get("notification", {})
    # OA 立项通知收件人/抄送与汇报信独立：优先 notification.oa，回退旧的扁平结构
    oa_notif = notif.get("oa", notif)
    recipients = oa_notif.get("recipients", [])
    cc = oa_notif.get("cc", [])

    if not pa_cfg:
        print("[通知邮件] 未配置 PA 账号，跳过发送", file=sys.stderr)
        return
    if not recipients:
        print("[通知邮件] 未配置收件人，跳过发送", file=sys.stderr)
        return

    # 构建邮件
    today = datetime.now().strftime("%Y-%m-%d")
    msg = MIMEMultipart("alternative")
    msg["From"] = pa_cfg["user"]
    msg["To"] = ", ".join(recipients)
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg["Subject"] = f"OA立项通知 - {today} ({len(results)}条)"

    html_body = _build_notification_html(results)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # SMTP 发送
    try:
        smtp = smtplib.SMTP(pa_cfg["smtp_host"], pa_cfg["smtp_port"])
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        # 尝试 OAuth2 认证
        token = _get_smtp_oauth2_token(pa_cfg)
        if token:
            auth_string = f"user={pa_cfg['user']}\x01auth=Bearer {token}\x01\x01"
            try:
                smtp.docmd("AUTH", "XOAUTH2 " + __import__("base64").b64encode(auth_string.encode()).decode())
            except smtplib.SMTPAuthenticationError:
                print("[通知邮件] OAuth2 认证失败，降级到密码认证", file=sys.stderr)
                smtp.login(pa_cfg["user"], pa_cfg["password"])
        else:
            smtp.login(pa_cfg["user"], pa_cfg["password"])

        # 实际收件人 = To + Cc（SMTP sendmail 要显式给全）
        smtp.sendmail(pa_cfg["user"], recipients + cc, msg.as_string())
        smtp.quit()
        print(f"[通知邮件] 发送成功: {len(results)} 条结果 → {', '.join(recipients)}"
              + (f" (CC: {', '.join(cc)})" if cc else ""), file=sys.stderr)
    except Exception as e:
        print(f"[通知邮件] 发送失败: {e}", file=sys.stderr)


# 压缩包扩展名：20608 只需从原邮件补带压缩包文件
_ARCHIVE_EXT = (".zip", ".rar", ".7z")


def _all_email_attachments(raw_bytes):
    """从原始邮件 MIME 提取全部附件 → [(filename, payload_bytes)]（含 zip 等所有类型）。"""
    import email as _email
    out = []
    if not raw_bytes:
        return out
    try:
        m = _email.message_from_bytes(raw_bytes)
    except Exception:
        return out
    for part in m.walk():
        if part.get_content_maintype() == "multipart":
            continue
        fname = part.get_filename()   # Python 会解码 RFC2047 文件名
        if not fname:
            continue
        try:
            payload = part.get_payload(decode=True)
        except Exception:
            payload = None
        if payload:
            out.append((fname, payload))
    return out


def send_forward_oa(all_results, all_emails=None, dry_run=False):
    """转OA：把每条立项逐案转给 OA 处理团队（替换原 send_notification 总表→qin.zhang）。
    收件人=杨姣/薄佳璐/客户公共邮箱；抄送=固定7人+客户接口人；主题保留原邮件；
    正文 OP02 模板；附官文 PDF。用 pa 账号发。dry_run 只打印不发。"""
    from email.mime.base import MIMEBase
    from email import encoders
    from forward_oa import (forward_recipients, forward_cc, build_forward_subject,
                            build_forward_body, forward_attachments,
                            build_assign_notifies)

    if not all_results:
        print("[转OA] 无立项结果，跳过", file=sys.stderr)
        return []

    pa_cfg = load_config().get("accounts", {}).get("pa")
    if not pa_cfg:
        print("[转OA] 未配置 PA 账号，跳过", file=sys.stderr)
        return []

    # msgid -> _inbox 官文 PDF（CN/EP 附件来源）
    msgid_to_pdfs = {}
    msgid_to_raw = {}   # msgid -> 原始 MIME（20608 需带原始邮件全部附件，含 zip）
    for _acc, _em in (all_emails or []):
        mid = _em.get("message_id", "")
        if not mid:
            continue
        if _em.get("saved_pdfs"):
            msgid_to_pdfs[mid] = _em.get("saved_pdfs", [])
        if _em.get("raw_bytes"):
            msgid_to_raw[mid] = _em.get("raw_bytes")

    # 逐案预构建
    plans = []
    for item in all_results:
        project = item.get("project", "")
        if not project:
            continue
        atts = forward_attachments(item, msgid_to_pdfs)
        plans.append({
            "item": item,
            "to": forward_recipients(project),
            "cc": forward_cc(project, item),
            "subject": build_forward_subject(item, atts),  # 【OA自动立项通知】+ 官文文件名(发文日-官文名-案号)
            "body": build_forward_body(item),
            "atts": atts,
        })
    if not plans:
        print("[转OA] 无有效案件（缺案号），跳过", file=sys.stderr)
        return []

    # 本次转OA立项动作（每案一条，供邮件动作记录页）；依据=官文类型
    fwd_actions = [{"message_id": p["item"].get("message_id", ""),
                    "project": p["item"].get("project", ""),
                    "action": "转OA立项",
                    "reason": f"OA立项官文类型:{p['item'].get('notification_type', '') or p['item'].get('project_name', '')}"}
                   for p in plans]

    if dry_run:
        for p in plans:
            atts = [os.path.basename(a) for a in p["atts"]]
            if (p["item"].get("project", "") or "")[:5] == "20608":
                raw = msgid_to_raw.get(p["item"].get("message_id", ""))
                for fname, _ in _all_email_attachments(raw):
                    if not fname.lower().endswith(_ARCHIVE_EXT):
                        continue
                    if fname not in atts:
                        atts.append(fname + "(原始邮件压缩包)")
            print(f"  [dry-run][转OA] {p['item'].get('project')}", file=sys.stderr)
            print(f"      主题: {p['subject']}", file=sys.stderr)
            print(f"      收件人({len(p['to'])}): {', '.join(p['to'])}", file=sys.stderr)
            print(f"      抄送({len(p['cc'])}): {', '.join(p['cc'])}", file=sys.stderr)
            print(f"      附件({len(atts)}): {', '.join(atts) if atts else '(无)'}", file=sys.stderr)
        print(f"  [dry-run][转OA] 共 {len(plans)} 封待发（未实际发送）", file=sys.stderr)
        # 审意涉新颖性/创造性的案不发分配链接
        for _nt in build_assign_notifies([p for p in plans if not p["item"].get("_skip_assign")]):
            print(f"  [dry-run][OA分配链接] → {_nt['to']} 抄送 {', '.join(_nt['cc'])}  主题: {_nt['subject']}", file=sys.stderr)
        return fwd_actions

    if os.environ.get("PIPELINE_NO_EMAIL"):
        print(f"  [测试] PIPELINE_NO_EMAIL 已设，跳过发送 {len(plans)} 封转OA邮件（Wiki/库照常）", file=sys.stderr)
        return fwd_actions

    # 打开一次 SMTP，逐案发送
    try:
        smtp = smtplib.SMTP(pa_cfg["smtp_host"], pa_cfg["smtp_port"])
        smtp.ehlo(); smtp.starttls(); smtp.ehlo()
        token = _get_smtp_oauth2_token(pa_cfg)
        if token:
            auth_string = f"user={pa_cfg['user']}\x01auth=Bearer {token}\x01\x01"
            try:
                smtp.docmd("AUTH", "XOAUTH2 " + __import__("base64").b64encode(auth_string.encode()).decode())
            except smtplib.SMTPAuthenticationError:
                print("[转OA] OAuth2 认证失败，降级密码认证", file=sys.stderr)
                smtp.login(pa_cfg["user"], pa_cfg["password"])
        else:
            smtp.login(pa_cfg["user"], pa_cfg["password"])
    except Exception as e:
        print(f"[转OA] SMTP 连接/认证失败，全部跳过: {e}", file=sys.stderr)
        return []

    sent = 0
    for p in plans:
        try:
            msg = MIMEMultipart()
            msg["From"] = pa_cfg["user"]
            msg["To"] = ", ".join(p["to"])
            if p["cc"]:
                msg["Cc"] = ", ".join(p["cc"])
            msg["Subject"] = p["subject"]
            msg.attach(MIMEText(p["body"], "plain", "utf-8"))
            attached_names = set()
            for fp in p["atts"]:
                with open(fp, "rb") as fh:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(fh.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment",
                                filename=("utf-8", "", os.path.basename(fp)))
                msg.attach(part)
                attached_names.add(os.path.basename(fp))
            # 20608（韶音）：额外带上原始邮件的压缩包文件，按文件名去重
            if (p["item"].get("project", "") or "")[:5] == "20608":
                raw = msgid_to_raw.get(p["item"].get("message_id", ""))
                extra = 0
                for fname, payload in _all_email_attachments(raw):
                    if not fname.lower().endswith(_ARCHIVE_EXT):
                        continue
                    if fname in attached_names:
                        continue
                    attached_names.add(fname)
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(payload)
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", "attachment",
                                    filename=("utf-8", "", fname))
                    msg.attach(part)
                    extra += 1
                if extra:
                    print(f"[转OA] {p['item'].get('project')} 20608 额外附原始邮件 {extra} 个压缩包", file=sys.stderr)
            smtp.sendmail(pa_cfg["user"], p["to"] + p["cc"], msg.as_string())
            sent += 1
            print(f"[转OA] {p['item'].get('project')} 已发 → {', '.join(p['to'])}", file=sys.stderr)
        except Exception as e:
            print(f"[转OA] {p['item'].get('project')} 发送失败: {e}", file=sys.stderr)

    # OA 分配链接：不发流程人员，按案号路由收件人分组发（20608→王志刚、其余→薛虹，均抄送海灵；复用已开 SMTP）
    # 审意涉新颖性/创造性的案不发分配链接（_skip_assign）
    for _nt in build_assign_notifies([p for p in plans if not p["item"].get("_skip_assign")]):
        try:
            nmsg = MIMEMultipart()
            nmsg["From"] = pa_cfg["user"]
            nmsg["To"] = _nt["to"]
            if _nt["cc"]:
                nmsg["Cc"] = ", ".join(_nt["cc"])
            nmsg["Subject"] = _nt["subject"]
            nmsg.attach(MIMEText(_nt["body"], "plain", "utf-8"))
            smtp.sendmail(pa_cfg["user"], [_nt["to"]] + _nt["cc"], nmsg.as_string())
            print(f"[OA分配链接] 已发 → {_nt['to']} 抄送 {', '.join(_nt['cc'])}", file=sys.stderr)
        except Exception as e:
            print(f"[OA分配链接] 发送失败 → {_nt.get('to')}: {e}", file=sys.stderr)

    try:
        smtp.quit()
    except Exception:
        pass
    print(f"[转OA] 完成：{sent}/{len(plans)} 封", file=sys.stderr)
    return fwd_actions


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
                since = datetime.now() - timedelta(days=7)
        else:
            since = datetime.now() - timedelta(days=7)

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
    {"account": "attorneys", "folder": "TEST"}
]

# 无 checkpoint 时的回溯窗口（天）。设计为每天定时运行，首次/丢断点只读最近 1 天，
# 不拉历史；有 checkpoint 时仍按断点增量读，漏跑一天下次会自动补上，不漏邮件。
LOOKBACK_DAYS = 1


def read_and_classify_oa(accounts=None, config_path=None):
    """读邮件 + 分类（OA 立项）。供单独运行和 email_pipeline 统一调度共用。
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

        # 更新断点
        if emails:
            update_checkpoint(account_name, folder, emails)

        # 筛选 OA 立项邮件
        results, skipped, unknown_types = process_emails(emails)

        all_emails.extend([(acc, em) for em in emails])
        all_results.extend(results)

    return all_emails, all_results


_customer_shortname_cache = {}


def query_customer_shortname(customer_code):
    """atw customer 表：customer_code（案号前5位）→ customer_shortname（客户简称）。
    查不到/连不上返回空串，不阻塞立项。按 code 缓存避免重复查。"""
    code = (customer_code or "")[:5]
    if not code:
        return ""
    if code in _customer_shortname_cache:
        return _customer_shortname_cache[code]
    name = ""
    try:
        from db_query import execute
        safe = code.replace("'", "\\'")
        rows = execute(f"SELECT customer_shortname FROM customer WHERE customer_code = '{safe}'")
        if rows and rows[0].get("customer_shortname"):
            name = rows[0]["customer_shortname"]
    except Exception as e:
        print(f"[customer] 查客户简称失败 {code}: {e}", file=sys.stderr)
    _customer_shortname_cache[code] = name
    return name


def _drop_closed_cases(all_results, is_closed):
    """剔除已结案案件（不立项）。is_closed(project)->bool 由调用方注入，便于测试。
    按 project 缓存，避免同案号重复查 IPEasy；无案号的条目保留（不查）。返回保留的 results。"""
    cache = {}
    kept = []
    for item in all_results:
        proj = item.get("project", "") or ""
        if proj:
            if proj not in cache:
                cache[proj] = is_closed(proj)
            if cache[proj]:
                print(f"[结案] {proj} 已结案（终止/维持/结案），跳过立项", file=sys.stderr)
                continue
        kept.append(item)
    return kept


def dispatch_oa(all_results, all_emails=None, dry_run=False, test_project_prefix=None):
    """OA 立项下游 sink：建OA信息表页 → US期限 → 上传官文附件 → 新增OA → projects → 立项通知。
    all_emails 用于按 message_id 取邮件官文 PDF（CN/EP）；US 官文来自下载。
    test_project_prefix 不为空时，把案号客户代码前缀换成它（如 20618-0895CN00 →
    90009-0895CN00），用于测试时避免撞已存在的 Wiki 页面。
    注：email_pipeline 模式下本函数不再 move 邮件，归档统一交 archive_emails。
    dry_run=True 时：不下载USPTO官文、不建/写Wiki、不上传附件、不发立项通知邮件。"""
    # 非独立 EP 记录（standalone_project=False，如 R.70(2)/70a(2)）不参与立项：
    # 这类项原先在分类阶段就被丢弃、从不进立项；现为供汇报信 sink 使用改为保留进 results，
    # 故在立项入口按此标志过滤掉，保持立项行为与原来完全一致。
    all_results = [it for it in (all_results or [])
                   if not (it.get("region") == "EP" and it.get("standalone_project") is False)]

    # 原始邮件主题含「结案报告」的不立项（仅 OA 侧过滤，不影响汇报信/分类器）。
    _before = len(all_results)
    all_results = [it for it in all_results if "结案报告" not in (it.get("email_subject", "") or "")]
    if len(all_results) < _before:
        print(f"  [结案报告] 主题含「结案报告」，跳过立项 {_before - len(all_results)} 条", file=sys.stderr)

    # 已结案案件不立项：查 IPEasy 状态（终止/维持/结案）→ 剔除。用真实案号,故先于测试前缀替换。
    from oainfo_cli import is_case_closed
    all_results = _drop_closed_cases(all_results, is_case_closed)

    # 测试用案号前缀替换：20618-0895CN00 → 90009-0895CN00（防 Wiki 页面已存在）
    # ⚠️ 直接改写 item['project']，OA 先于 report 跑且共用 all_results，开启时建议关 report sink
    if test_project_prefix:
        for _item in all_results:
            _p = _item.get("project", "") or ""
            if "-" in _p:
                # 客户简称要按真实案号查，先记下原客户代码（前5位），再替换前缀
                _item["_orig_customer_code"] = _p[:5]
                _item["project"] = f"{test_project_prefix}-{_p.split('-', 1)[1]}"
        print(f"  [测试] 案号前缀已替换为 {test_project_prefix}", file=sys.stderr)
    # 为每条立项结果创建 Wiki OA信息记录表页面（按案号建族页面+子页）
    if all_results and dry_run:
        print(f"  [dry-run] 跳过创建 OA 信息记录表 Wiki 页面（{len(all_results)} 条）", file=sys.stderr)
    elif all_results:
        from oainfo_cli import create_oa_page
        wiki_cache = {}        # project -> url
        wiki_id_cache = {}     # project -> page_id（供上传附件用）
        for item in all_results:
            project = item.get("project", "")
            if not project:
                item["wikiurl"] = ""
                continue
            if project not in wiki_cache:
                try:
                    wiki_result = create_oa_page(project)
                    wiki_cache[project] = wiki_result.get("url", "")
                    wiki_id_cache[project] = wiki_result.get("id")
                    print(f"[Wiki] {project}: {wiki_result.get('msg', '')}", file=sys.stderr)
                except Exception as e:
                    wiki_cache[project] = ""
                    wiki_id_cache[project] = None
                    print(f"[Wiki] {project} 创建失败: {e}", file=sys.stderr)
            item["wikiurl"] = wiki_cache[project]
            item["wiki_page_id"] = wiki_id_cache.get(project)
        print(f"Wiki 页面处理完成: {len(wiki_cache)} 个案号", file=sys.stderr)

    # US 答复期限：下载官文 PDF → 解析 months → 计算 deadline
    us_items = [r for r in all_results if r.get("region") == "US" and r.get("application_no")]
    if us_items and dry_run:
        print(f"  [dry-run] 跳过 {len(us_items)} 条 US 官文下载/期限解析", file=sys.stderr)
    elif us_items:
        from us_deadline import get_us_deadline
        from filter_oa_email import _parse_date, _add_months, calc_dueDate
        # 兜底标准期限（P1-综合期限速查表）：官文解析失败时，用 发文日(邮戳)+标准月数
        US_STANDARD_MONTHS = {"CTNF": 3, "CTFR": 3, "CTRS": 2}   # NOA 已不立项，移除
        print(f"\n{len(us_items)} 条 US 记录需要获取答复期限...", file=sys.stderr)
        for item in us_items:
            try:
                dl = get_us_deadline(
                    item["application_no"],
                    item.get("notification_type", ""),
                    item.get("oa_doc_date", ""),
                    item.get("project", ""),
                )
                if dl and dl.get("unpublished"):
                    item["us_unpublished"] = True   # 403：未公开/受限申请，转OA正文标注、官文无附件
                if dl and dl.get("deadline"):
                    item["project_deadline"] = dl["deadline"]
                    # 用新的 deadline 重算 dueDate
                    item["dueDate"] = calc_dueDate(item)
                    print(f"[US] {item['project']} 答复期限: {dl['deadline']}", file=sys.stderr)
                else:
                    # 兜底：发文日 + 标准月数
                    _m = US_STANDARD_MONTHS.get(item.get("notification_type", ""))
                    _d = _parse_date(item.get("oa_doc_date", "")) if _m else None
                    if _m and _d:
                        item["project_deadline"] = _add_months(_d, _m).strftime("%Y-%m-%d")
                        item["dueDate"] = calc_dueDate(item)
                        print(f"[US] {item['project']} 官文解析失败，按标准表兜底 {_m}月 → {item['project_deadline']}", file=sys.stderr)
                    else:
                        print(f"[US] {item['project']} 答复期限获取失败，留空", file=sys.stderr)
                # 记下本次下载的全部官文文件（含 Word），供转OA附件/Wiki 上传
                if dl and dl.get("doc_paths"):
                    item["us_doc_paths"] = dl["doc_paths"]
                # 记下下载的官文 PDF 路径，供上传到 OA 信息表页
                if dl and dl.get("pdf_path"):
                    item["us_pdf_path"] = dl["pdf_path"]
                    # 盖 DOCKETED 邮戳（仅主OA答复类+补正类）：生成盖章副本，保留原文件名（_stamped 子目录）
                    try:
                        from stamp_us_pdf import stamp_us_pdf
                        _sd = os.path.join(os.path.dirname(dl["pdf_path"]), "_stamped")
                        os.makedirs(_sd, exist_ok=True)
                        _out = os.path.join(_sd, os.path.basename(dl["pdf_path"]))
                        _stamped = stamp_us_pdf(dl["pdf_path"], item.get("notification_type", ""),
                                                item.get("oa_doc_date", ""), out_path=_out)
                        if _stamped:
                            item["us_stamped_pdf_path"] = _stamped
                            print(f"[US] {item['project']} 已盖DOCKETED邮戳", file=sys.stderr)
                    except Exception as e:
                        print(f"[US] {item['project']} 盖章失败(用原官文): {e}", file=sys.stderr)
                # 同案号 892/1449 文献：从 USPTO 下载（供转OA附件 + Wiki 上传；不盖章）
                ref_docs = item.get("us_ref_docs") or []
                if ref_docs:
                    from us_deadline import download_us_ref_doc
                    ref_paths = []
                    paths_892 = []      # 单独留下 892(Notice of References Cited)，供对比文件抽取
                    for rd in ref_docs:
                        _p = download_us_ref_doc(
                            rd.get("application_no", "") or item.get("application_no", ""),
                            rd.get("document_code", ""),
                            rd.get("oa_doc_date", "") or item.get("oa_doc_date", ""),
                            item.get("project", ""))
                        ref_paths.extend(_p)
                        if (rd.get("document_code") or "") == "892":
                            paths_892.extend(_p)
                    if ref_paths:
                        item["us_ref_pdf_paths"] = ref_paths
                        print(f"[US-ref] {item['project']} 文献 {len(ref_paths)} 份: "
                              f"{[os.path.basename(p) for p in ref_paths]}", file=sys.stderr)
                    if paths_892:
                        item["us_892_pdf_paths"] = paths_892
            except Exception as e:
                print(f"[US] {item['project']} 异常: {e}", file=sys.stderr)

    # 注：PPH.DECISION 已一律不立项（移入 US_TYPES_SKIP），原"读官文判 dismissed/granted"逻辑随之移除。

    # Examiner Interview Summary：官文含 "It is not necessary for applicant" → 无需答复，不立项
    exin_items = [r for r in all_results if r.get("notification_type") == "EXIN"]
    if exin_items and not dry_run:
        from parse_us_pdf import interview_no_action_needed
        for it in exin_items:
            if interview_no_action_needed(it.get("us_pdf_path", "")):
                it["_exin_drop"] = True
                print(f"[EXIN] {it.get('project')} 含『It is not necessary for applicant』→ 不立项", file=sys.stderr)
            else:
                print(f"[EXIN] {it.get('project')} → 立项", file=sys.stderr)
        all_results = [r for r in all_results if not r.get("_exin_drop")]

    # 上传官文附件到 OA 信息记录表页：CN/EP 取邮件附件 PDF，US 取下载的官文
    if all_results and dry_run:
        print(f"  [dry-run] 跳过上传官文附件到 OA 信息表页", file=sys.stderr)
    elif all_results:
        from oainfo_cli import WikiClient, find_publication_file
        try:
            from word_to_wiki import upload_doc_subpages
        except Exception as _e:
            upload_doc_subpages = None
            print(f"[官文转Wiki] 无法导入 word_to_wiki（跳过官文转子页）: {_e}", file=sys.stderr)
        # msgid -> 邮件保存的官文 PDF（report 读取层存到 _inbox 的）
        msgid_to_pdfs = {}
        for _acc, _em in (all_emails or []):
            mid = _em.get("message_id", "")
            if mid and _em.get("saved_pdfs"):
                msgid_to_pdfs[mid] = _em.get("saved_pdfs", [])
        wiki = WikiClient()
        uploaded = 0
        for item in all_results:
            page_id = item.get("wiki_page_id")
            if not page_id:
                continue
            files = list(msgid_to_pdfs.get(item.get("message_id", ""), []))
            if item.get("us_pdf_path"):
                files.append(item["us_pdf_path"])
            # 主官文其它格式（Word 版等）：官文可能只有 Word，一并上传 Wiki
            _pdf = item.get("us_pdf_path", "")
            files.extend([d for d in (item.get("us_doc_paths") or []) if d and d != _pdf])
            files.extend(item.get("us_ref_pdf_paths") or [])   # 同案号 892/1449 文献
            # 官文正文转 OA信息记录表页下的子页（US/CN/EP；有 Word 用 Word、没 Word 用 PDF）；
            # 建有序号版 + 无序号版两个子页（正文只抽一次，扫描件只 OCR 一次）
            if upload_doc_subpages:
                _src = _official_doc_for_subpage(
                    item, msgid_to_pdfs.get(item.get("message_id", ""), []))
                if _src:
                    # EP：官文附件是 panovision 按「代理号-日期-号-类型」命名的，子页标题统一改成
                    # 「发文日-类型-案号」（US 下载名/CN 附件名本就规范，不传 base_title 沿用文件名）。
                    _bt = None
                    if item.get("region") == "EP":
                        _dt = (item.get("oa_doc_date", "") or "")[:10]
                        _pj = item.get("project", "") or ""
                        _ty = (item.get("notification_type", "") or "").strip()
                        if _dt and _pj:
                            _bt = "-".join(x for x in (_dt, _ty, _pj) if x)
                    try:
                        for _st, _title in upload_doc_subpages(wiki, page_id, _src, base_title=_bt):
                            print(f"[官文转Wiki] {item.get('project','')} {os.path.basename(_src)} → "
                                  f"HTTP {_st} 子页:{_title}", file=sys.stderr)
                    except Exception as e:
                        print(f"[官文转Wiki] {item.get('project','')} 失败 {_src}: {e}", file=sys.stderr)
            # 公布/公告文件：客户目录名用 atw 客户简称拼；查不到简称/文件则跳过
            pub = find_publication_file(
                item.get("project", ""), item.get("region", ""),
                shortname=query_customer_shortname((item.get("project", "") or "")[:5]))
            if pub:
                files.append(pub)
                print(f"[公布文件] {item.get('project')} → {os.path.basename(pub)}", file=sys.stderr)
            # 本案公布文本：按公开号从 FPO 下载 PDF，一并上传（NAS 公布文件的补充/兜底）
            pub_txt = _download_case_publication(item.get("project", ""))
            if pub_txt and os.path.exists(pub_txt) and pub_txt not in files:
                files.append(pub_txt)
                print(f"[公布文本] {item.get('project')} → {os.path.basename(pub_txt)}", file=sys.stderr)
            for fp in files:
                try:
                    if wiki.upload_attachment(page_id, fp):
                        uploaded += 1
                except Exception as e:
                    print(f"[Wiki 附件] {item.get('project','')} 上传失败 {fp}: {e}", file=sys.stderr)
        print(f"[Wiki 附件] 上传完成: {uploaded} 个文件", file=sys.stderr)

    # OA收文日 + 答复期限：直接用 item 字段（与「新增OA列表」同源）写到 OA信息记录表
    # 「OA过程」表对应 OA{N} 行，不依赖对比文件解析。
    # OA次数：CN 审查意见用 parse_oa_seq(第N次)、US/EP 用 oaNum；
    # 补正/驳回/复审无「第N次」、无 oaNum → oa_seq 为空自然跳过（它们无 OA{N} 行）。
    from parse_cn_pdf import parse_oa_seq as _parse_oa_seq
    from oainfo_cli import fill_ref_docs_in_oa_row as _fill_oa_row
    for item in all_results:
        oa_seq = (_parse_oa_seq(item.get("project_name", "") or "")
                  if item.get("region") == "CN" else item.get("oaNum"))
        if not oa_seq:
            continue
        oa_doc_date = item.get("oa_doc_date", "")
        deadline = item.get("project_deadline", "")
        if not (oa_doc_date or deadline):
            continue
        try:
            _fill_oa_row(f"{item.get('project','')}-OA信息记录表", oa_seq, [],
                         oa_doc_date=oa_doc_date, project_deadline=deadline, dry_run=dry_run)
        except Exception as e:
            print(f"[OA收文日/期限] {item.get('project','')} 写回失败: {e}", file=sys.stderr)

    # 对比文件（仅 CN）：解析审查意见通知书官文 PDF「本通知书引用下列对比文件」表，
    # 填到该案 OA信息记录表页「OA过程」表对应 OA{N} 行的「对比文件链接」列。
    cn_items = [r for r in all_results if r.get("region") == "CN"]
    if cn_items:
        from parse_cn_pdf import extract_cn_ref_docs, parse_oa_seq
        from oainfo_cli import fill_ref_docs_in_oa_row
        # msgid -> 邮件保存的官文 PDF（report 读取层存到 _inbox 的）
        cn_msgid_to_pdfs = {}
        for _acc, _em in (all_emails or []):
            mid = _em.get("message_id", "")
            if mid and _em.get("saved_pdfs"):
                cn_msgid_to_pdfs[mid] = _em.get("saved_pdfs", [])
        for item in cn_items:
            pdfs = cn_msgid_to_pdfs.get(item.get("message_id", ""), [])
            if not pdfs:
                continue
            # 从该邮件的官文 PDF 里挑出解析到对比文件的那份（通知书 PDF）
            parsed = None
            for fp in pdfs:
                try:
                    r = extract_cn_ref_docs(fp)
                except Exception as e:
                    print(f"[对比文件] {item.get('project','')} 解析失败 {fp}: {e}", file=sys.stderr)
                    continue
                if r.get("ref_docs"):
                    parsed = r
                    break
            proj = item.get("project", "")
            if not parsed:
                _seq = parse_oa_seq(item.get("project_name", "") or "")
                print(f"[对比文件][CN] {proj} OA{_seq or '?'}：未从审查意见读到对比文件", file=sys.stderr)
                continue
            # OA 次数：优先用 PDF 里解析到的，其次从立项名称「第N次」推
            oa_seq = parsed.get("oa_seq") or parse_oa_seq(item.get("project_name", "") or "")
            docs = parsed["ref_docs"]
            print(f"[对比文件][CN] {proj} OA{oa_seq}：从审查意见读到 {len(docs)} 条对比文件 → "
                  f"{[d.get('doc_no') for d in docs]}", file=sys.stderr)
            try:
                _r = fill_ref_docs_in_oa_row(
                    f"{proj}-OA信息记录表", oa_seq, docs,
                    oa_doc_date=item.get("oa_doc_date", ""),      # OA收文日 ← 官文发文日
                    project_deadline=item.get("project_deadline", ""),  # 期限
                    dry_run=dry_run,
                )
                print(f"[对比文件][CN] {proj} OA{oa_seq} 写回记录表: {(_r or {}).get('status')}", file=sys.stderr)
            except Exception as e:
                print(f"[对比文件][CN] {proj} OA{oa_seq} 写回失败: {e}", file=sys.stderr)

    # 对比文件（US）：从 PTO-892(优先) 或主官文正文抽审查员引用的对比文件，归一化成 Google Patents 号，
    # 与 CN 同样填该案 OA信息记录表页「OA过程」表 OA{N} 行「对比文件链接」列（复用 fill_ref_docs_in_oa_row）。
    us_ref_items = [r for r in all_results if r.get("region") == "US"]
    if us_ref_items and not dry_run:
        from parse_us_refs import extract_us_ref_docs
        from oainfo_cli import fill_ref_docs_in_oa_row
        for item in us_ref_items:
            # 优先用 892（审查员正式引用清单），没有则退回主官文 PDF 正文
            src = (item.get("us_892_pdf_paths") or [None])[0] or item.get("us_pdf_path")
            if not src:
                continue
            proj = item.get("project", "")
            oa_seq = item.get("oaNum") or 1     # US 用已有的 OA 序号机制
            try:
                parsed = extract_us_ref_docs(src)
            except Exception as e:
                print(f"[对比文件][US] {proj} OA{oa_seq} 解析失败: {e}", file=sys.stderr)
                continue
            docs = parsed.get("ref_docs") or []
            if not docs:
                print(f"[对比文件][US] {proj} OA{oa_seq}：未从审查意见/892 读到对比文件", file=sys.stderr)
                continue
            print(f"[对比文件][US] {proj} OA{oa_seq}：从审查意见/892 读到 {len(docs)} 条对比文件 → "
                  f"{[d['doc_no'] for d in docs]}", file=sys.stderr)
            try:
                _r = fill_ref_docs_in_oa_row(
                    f"{proj}-OA信息记录表", oa_seq, docs,
                    oa_doc_date=item.get("oa_doc_date", ""),
                    project_deadline=item.get("project_deadline", ""),
                    dry_run=dry_run,
                )
                print(f"[对比文件][US] {proj} OA{oa_seq} 写回记录表: {(_r or {}).get('status')}", file=sys.stderr)
            except Exception as e:
                print(f"[对比文件][US] {proj} OA{oa_seq} 写回失败: {e}", file=sys.stderr)

    # 审意新颖性/创造性判断（立项时）：读审意全文 → DeepSeek 判是否涉及新颖性(US §102/EPC Art.54)或
    # 创造性(US §103/EPC Art.56)。命中任一 → 「其它备注事项」列标注 + 该案不进 OA 分配
    # （不进待分配、不发分配链接；立项/转OA/写Wiki 照常）。
    # 读不到审意 / DeepSeek 失败默认「无问题」，不误跳过分配（宁可多分一件，不漏分一件）。
    if all_results and not dry_run:
        try:
            from analyze_oa_issue import analyze_novelty_inventiveness
            from word_to_wiki import _content_pieces
            from parse_cn_pdf import parse_oa_seq as _parse_seq
            _mid2pdfs_ni = {}
            for _acc, _em in (all_emails or []):
                _m = _em.get("message_id", "")
                if _m and _em.get("saved_pdfs"):
                    _mid2pdfs_ni[_m] = _em.get("saved_pdfs", [])
            for item in all_results:
                proj = item.get("project", "")
                _seq = (_parse_seq(item.get("project_name", "") or "")
                        if item.get("region") == "CN" else item.get("oaNum")) or "?"
                _src = _official_doc_for_subpage(
                    item, _mid2pdfs_ni.get(item.get("message_id", ""), []))
                if not _src:
                    print(f"[审意分析] {proj} OA{_seq}：未找到审意官文，跳过判断（默认可分配）", file=sys.stderr)
                    continue
                try:
                    _paras, _tb = _content_pieces(_src)
                    _oa_text = "\n".join(_paras)
                except Exception as e:
                    print(f"[审意分析] {proj} OA{_seq}：读审意正文失败，跳过判断: {e}", file=sys.stderr)
                    continue
                if not _oa_text.strip():
                    print(f"[审意分析] {proj} OA{_seq}：审意正文为空，跳过判断（默认可分配）", file=sys.stderr)
                    continue
                v = analyze_novelty_inventiveness(_oa_text)
                if v.get("novelty") or v.get("inventiveness"):
                    _issues = [n for n, f in (("新颖性", v.get("novelty")),
                                              ("创造性", v.get("inventiveness"))) if f]
                    item["其它备注事项"] = v.get("note") or f"涉及{'、'.join(_issues)}"
                    item["_skip_assign"] = True
                    print(f"[审意分析] {proj} OA{_seq}：涉及{'、'.join(_issues)} → "
                          f"其它备注事项标注、不进OA分配", file=sys.stderr)
                else:
                    print(f"[审意分析] {proj} OA{_seq}：未见新颖性/创造性 → 正常分配", file=sys.stderr)
        except Exception as e:
            print(f"[审意分析] 模块不可用，全部按可分配处理: {e}", file=sys.stderr)

    print(f"\n{'='*40}", file=sys.stderr)
    print(f"汇总: {len(all_results)} 条立项结果", file=sys.stderr)
    print("results:", all_results)

    # 其他OA 备注：查 atw projects 判 同族首案/非同族首案（分案评估/补正/驳回复审评估 已由分类器定，不覆盖）
    # 必须在写 projects(INSERT) 之前，避免把当前案自身算进去
    if all_results and not dry_run:
        from oainfo_cli import family_first_case_remark
        for item in all_results:
            if item.get("oa_remark"):     # 已有类型化备注 → 保留
                continue
            item["oa_remark"] = family_first_case_remark(
                item.get("project", ""), item.get("project_name", ""))
            if item["oa_remark"]:
                print(f"[备注] {item.get('project')} → {item['oa_remark']}", file=sys.stderr)

    # 预审案件：备注一格追加「预审案件」（第一/二次审查意见 + 邮件含预审案件；无需查库，dry_run 也生效）
    for item in (all_results or []):
        note = item.get("prescreen_note")
        if note and note not in (item.get("oa_remark", "") or ""):
            item["oa_remark"] = f"{item.get('oa_remark', '')} {note}".strip()
            print(f"[预审] {item.get('project')} 备注加注：{note}", file=sys.stderr)

    # 为每条立项分配唯一 id（= projects.row_id）：埋进 Wiki 新增OA 行(data-oa-id) + TIP INSERT 复用，
    # 供 OA 分配按 id 打开/回写人员分配。必须在写 Wiki 与写 projects 之前生成。
    import uuid as _uuid
    for _it in (all_results or []):
        if not _it.get("oa_id"):
            _it["oa_id"] = str(_uuid.uuid4())

    # 写入 Wiki 新增 OA 页面
    if all_results and dry_run:
        print(f"  [dry-run] 跳过写 Wiki 新增OA（{len(all_results)} 条）", file=sys.stderr)
    elif all_results:
        from oainfo_cli import append_oa_to_wiki
        try:
            wiki_list_result = append_oa_to_wiki(all_results)
            print(f"[Wiki 新增OA] {wiki_list_result.get('msg', '')}", file=sys.stderr)
        except Exception as e:
            print(f"[Wiki 新增OA] 写入失败: {e}", file=sys.stderr)

    # 写入 TIP 系统（projects 表）
    inserted_items = []   # 成功 INSERT 进 projects 的案件；只有它们才进待分配库
    if all_results and dry_run:
        print(f"  [dry-run] 跳过写 projects 表（{len(all_results)} 条）", file=sys.stderr)
    elif all_results:
        from db_query import execute as db_execute
        inserted = 0
        for item in all_results:
            project = item.get("project", "")
            project_name = item.get("project_name", "")
            if not project or not project_name:
                continue
            # project_type：CN → 中国答复及其他；US/EP 等 → 海外答复及其他
            item["project_type"] = "中国答复及其他" if item.get("region") == "CN" else "海外答复及其他"
            # customer：客户简称，按真实客户代码查 atw customer 表（测试前缀下用原始代码）
            cust_code = item.get("_orig_customer_code") or (project or "")[:5]
            item["customer"] = query_customer_shortname(cust_code)
            # 客户案号(委托方案号)：查 IPEasy p_case_info.case_volume_customer（best-effort，取不到留空）
            try:
                from oainfo_cli import find_customer_case_no
                item["project_customernumber"] = find_customer_case_no(project)
            except Exception as e:
                print(f"[TIP] {project} 查客户案号失败: {e}", file=sys.stderr)
            # 检查是否已存在
            check_sql = f"SELECT COUNT(*) as cnt FROM projects WHERE project='{project}' AND project_name='{project_name}'"
            try:
                check = db_execute(check_sql)
                if check and check[0].get("cnt", 0) > 0:
                    print(f"[TIP] {project} {project_name} 已存在，跳过", file=sys.stderr)
                    continue
            except Exception:
                pass

            # 构建 INSERT；id 复用上面生成的 oa_id（与 Wiki 行 data-oa-id 一致）
            import uuid
            row_id = item.get("oa_id") or str(uuid.uuid4())
            fields = ["id", "project", "project_customernumber", "project_name", "project_type",
                       "customer", "oa_doc_date", "entrust_date",
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

            cols = ", ".join(fields)
            vals = ", ".join("NULL" if v == "__NULL__" else f"'{v}'" for v in values)
            insert_sql = f"INSERT INTO projects ({cols}) VALUES ({vals})"
            try:
                db_execute(insert_sql)
                inserted += 1
                inserted_items.append(item)   # 仅成功写库的才进待分配
                print(f"[TIP] {project} {project_name} 写入成功", file=sys.stderr)
            except Exception as e:
                print(f"[TIP] {project} {project_name} 写入失败: {e}", file=sys.stderr)

        print(f"TIP 写入完成: {inserted} 条", file=sys.stderr)

    # 落"待分配案件库"：只写成功进 projects 的案件(未写 projects 的——如已存在被跳过——不写)。
    if inserted_items and not dry_run:
        try:
            from oa_assign_store import add_pending
            # 审意涉新颖性/创造性的案不进待分配（_skip_assign），不发分配链接
            _to_pending = [it for it in inserted_items if not it.get("_skip_assign")]
            _skipped_n = len(inserted_items) - len(_to_pending)
            n = add_pending(_to_pending) if _to_pending else 0
            print(f"[待分配] 新增 {n} 件到 OA 分配待分配库"
                  + (f"（另 {_skipped_n} 件涉新颖性/创造性不进分配）" if _skipped_n else ""),
                  file=sys.stderr)
        except Exception as e:
            print(f"[待分配] 写入失败: {e}", file=sys.stderr)

    # AI 案件报告：立项即生成（见下方「分配报告」块）；分配页打开时先读 oa_assign_report 缓存，
    #     没有才现场懒生成（report/oa_assign.py analyze）。两处 save_report 为 UPSERT，不冲突。
    # CN/EP 审意官文是邮件附件（存在 _inbox，事后随邮件归档消失），故立项此刻复制到
    # attachment/{案号}/，与 US 下载件同目录，供 OA 分配按案号直接读。US 官文本就在该目录，无需复制。
    if inserted_items and not dry_run:
        try:
            from oa_report_ai import persist_email_official_docs
            _mid2pdfs = {}
            for _acc, _em in (all_emails or []):
                _mid = _em.get("message_id", "")
                if _mid and _em.get("saved_pdfs"):
                    _mid2pdfs[_mid] = _em.get("saved_pdfs", [])
            _saved = 0
            for item in inserted_items:
                if item.get("region") == "US":
                    continue  # US 官文已在 attachment/{案号}/
                _srcs = _mid2pdfs.get(item.get("message_id", ""), [])
                _saved += persist_email_official_docs(item.get("project", ""), _srcs)
            print(f"[官文归集] CN/EP 审意 PDF 复制到 attachment/案号/ 共 {_saved} 个", file=sys.stderr)
        except Exception as e:
            print(f"[官文归集] 失败: {e}", file=sys.stderr)

    # 立项即生成 AI 分配报告(报告+方案)落 oa_assign_report：这样发出分配链接后，薛虹点开即秒读缓存。
    # 官文已在上一步归集到 attachment/案号/，此刻生成能读到审意。单件失败不影响其它/主流程。
    if inserted_items and not dry_run:
        try:
            from oa_report_ai import build_case_report
            from oa_schemes import build_assignment_schemes, render_schemes_md
            from oa_assign_store import save_report
            _gen = 0
            for item in inserted_items:
                oa_id = item.get("oa_id", "")
                if not oa_id:
                    continue
                if item.get("_skip_assign"):   # 涉新颖性/创造性不分配 → 无需生成分配报告
                    continue
                try:
                    _md = build_case_report(item)
                    _sch = build_assignment_schemes(item.get("project", ""),
                                                    region=item.get("region", ""), report_md=_md)
                    _sec = render_schemes_md(_sch)
                    if _sec:
                        _md = _md.rstrip() + "\n\n" + _sec
                    save_report(oa_id, _md, _sch)
                    _gen += 1
                except Exception as e:
                    print(f"[分配报告] {item.get('project','')} 生成失败: {e}", file=sys.stderr)
            print(f"[分配报告] 立项即生成 {_gen} 件 → oa_assign_report", file=sys.stderr)
        except Exception as e:
            print(f"[分配报告] 模块不可用，跳过: {e}", file=sys.stderr)

    # 转OA：逐案转发给 OA 处理团队（替换原 send_notification 总表→qin.zhang；dry_run 内部处理）
    # 返回本次转OA立项动作 [{message_id, project, action, reason}]，供 main.py 汇总写邮件动作页
    return send_forward_oa(all_results, all_emails, dry_run=dry_run) or []


def record_email_actions(all_results, all_emails, oa_actions=None, report_actions=None, dry_run=False):
    """汇总两个 sink 的动作，按日折叠写入「邮件动作」Wiki 页（每案一行，不漏每封邮件）。
    dry_run 时只构建不写页。返回构建的 records。"""
    from oainfo_cli import build_email_action_records, append_email_actions_to_wiki
    records = build_email_action_records(all_results, all_emails, oa_actions or [], report_actions or [])
    if dry_run:
        print(f"[邮件动作] dry-run：{len(records)} 条待写（未写 Wiki）", file=sys.stderr)
        return records
    try:
        res = append_email_actions_to_wiki(records)
        print(f"[邮件动作] {res.get('msg', '')}", file=sys.stderr)
    except Exception as e:
        print(f"[邮件动作] 写入失败: {e}", file=sys.stderr)
    return records


def archive_emails(all_emails, all_results=None, dry_run=False):
    """单次归档：仅把分类命中的邮件 move 到 TEST_AUTO；未命中（既非OA也非汇报信）的保持不动。

    命中判定按 message_id 是否出现在 all_results（分类结果，OA/汇报信共用）。
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
    # 单独运行：读取 → 分类 → OA 下游 → 归档
    _all_emails, _all_results = read_and_classify_oa()
    dispatch_oa(_all_results, _all_emails)
    archive_emails(_all_emails, _all_results)
