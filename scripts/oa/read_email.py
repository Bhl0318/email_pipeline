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
    imap = imaplib.IMAP4_SSL(account_cfg["imap_host"], account_cfg["imap_port"])

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
        "message_id": msg.get("Message-ID", ""),
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
                since = datetime.now() - timedelta(days=700)
        else:
            since = datetime.now() - timedelta(days=700)

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


def dispatch_oa(all_results, dry_run=False):
    """OA 立项下游 sink：US 期限 → Wiki 新增OA → projects(注释) → 发立项通知邮件。
    注：email_pipeline 模式下本函数不再 move 邮件，归档统一交 archive_emails。
    dry_run=True 时：不下载USPTO官文、不写Wiki、不发立项通知邮件。"""
    # email_pipeline 测试标记：给 OA 立项的 project_name 统一加后缀，便于在
    # 数据表 / Wiki 里识别哪些是本管线（测试）生成的。只影响 OA 线，不动汇报信。
    PROJECT_NAME_SUFFIX = "_by_email_pipline"
    for _item in all_results:
        _pn = _item.get("project_name", "") or ""
        if _pn and not _pn.endswith(PROJECT_NAME_SUFFIX):
            _item["project_name"] = _pn + PROJECT_NAME_SUFFIX
    # # 为每条立项结果创建 Wiki OA信息记录表页面（暂时注释）
    # if all_results:
    #     from oainfo_cli import create_oa_page
    #     wiki_cache = {}
    #     for item in all_results:
    #         project = item.get("project", "")
    #         if not project:
    #             item["wikiurl"] = ""
    #             continue
    #         if project not in wiki_cache:
    #             try:
    #                 wiki_result = create_oa_page(project)
    #                 wiki_cache[project] = wiki_result.get("url", "")
    #                 print(f"[Wiki] {project}: {wiki_result.get('msg', '')}", file=sys.stderr)
    #             except Exception as e:
    #                 wiki_cache[project] = ""
    #                 print(f"[Wiki] {project} 创建失败: {e}", file=sys.stderr)
    #         item["wikiurl"] = wiki_cache[project]
    #     print(f"Wiki 页面处理完成: {len(wiki_cache)} 个案号", file=sys.stderr)

    # US 答复期限：下载官文 PDF → 解析 months → 计算 deadline
    us_items = [r for r in all_results if r.get("region") == "US" and r.get("application_no")]
    if us_items and dry_run:
        print(f"  [dry-run] 跳过 {len(us_items)} 条 US 官文下载/期限解析", file=sys.stderr)
    elif us_items:
        from us_deadline import get_us_deadline
        print(f"\n{len(us_items)} 条 US 记录需要获取答复期限...", file=sys.stderr)
        for item in us_items:
            try:
                dl = get_us_deadline(
                    item["application_no"],
                    item.get("notification_type", ""),
                    item.get("oa_doc_date", ""),
                    item.get("project", ""),
                )
                if dl and dl.get("deadline"):
                    item["project_deadline"] = dl["deadline"]
                    # 用新的 deadline 重算 dueDate
                    from filter_oa_email import calc_dueDate
                    item["dueDate"] = calc_dueDate(item)
                    print(f"[US] {item['project']} 答复期限: {dl['deadline']}", file=sys.stderr)
                else:
                    print(f"[US] {item['project']} 答复期限获取失败，留空", file=sys.stderr)
            except Exception as e:
                print(f"[US] {item['project']} 异常: {e}", file=sys.stderr)

    print(f"\n{'='*40}", file=sys.stderr)
    print(f"汇总: {len(all_results)} 条立项结果", file=sys.stderr)
    print("results:", all_results)

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
            # 检查是否已存在
            check_sql = f"SELECT COUNT(*) as cnt FROM projects WHERE project='{project}' AND project_name='{project_name}'"
            try:
                check = db_execute(check_sql)
                if check and check[0].get("cnt", 0) > 0:
                    print(f"[TIP] {project} {project_name} 已存在，跳过", file=sys.stderr)
                    continue
            except Exception:
                pass

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

            cols = ", ".join(fields)
            vals = ", ".join("NULL" if v == "__NULL__" else f"'{v}'" for v in values)
            insert_sql = f"INSERT INTO projects ({cols}) VALUES ({vals})"
            try:
                db_execute(insert_sql)
                inserted += 1
                print(f"[TIP] {project} {project_name} 写入成功", file=sys.stderr)
            except Exception as e:
                print(f"[TIP] {project} {project_name} 写入失败: {e}", file=sys.stderr)

        print(f"TIP 写入完成: {inserted} 条", file=sys.stderr)

    # 发送立项结果通知邮件
    if all_results and dry_run:
        print(f"  [dry-run] 跳过发送立项通知邮件（{len(all_results)} 条）", file=sys.stderr)
    elif all_results:
        send_notification(all_results)


def archive_emails(all_emails, dry_run=False):
    """单次归档：按账号把处理过的邮件 move 到 TEST_AUTO。
    email_pipeline 模式下归档只在这里发生一次（各 sink 内不再 move）。
    dry_run=True 时只打印不真正 move。"""
    groups = {}
    for acc, em in all_emails:
        key = (acc["account"], acc["folder"])
        if key not in groups:
            groups[key] = [acc, []]
        mid = em.get("message_id", "")
        if mid:
            groups[key][1].append(mid)
    for (account_name, folder), (acc, message_ids) in groups.items():
        if not message_ids:
            continue
        if dry_run:
            print(f"  [dry-run] 跳过归档 {len(message_ids)} 封（{account_name}/{folder} → TEST_AUTO）", file=sys.stderr)
            continue
        cfg = get_account_config(account_name)
        move_emails(cfg, folder, message_ids, target_folder="TEST_AUTO")


if __name__ == "__main__":
    # 单独运行：读取 → 分类 → OA 下游 → 归档
    _all_emails, _all_results = read_and_classify_oa()
    dispatch_oa(_all_results)
    archive_emails(_all_emails)
