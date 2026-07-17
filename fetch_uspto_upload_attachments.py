#!/usr/bin/env python3
"""抓取「美代理回邮」附件，按案号归档为待上传 USPTO 的文件包。

场景：环节4 把递交件发给美国代理人后，美代理签好回邮到指定邮箱文件夹。本脚本读取该
文件夹里每封邮件的附件（无附件则跳过），从**附件文件名**里解析案号，把同一案号的附件
存到同一个文件夹（以案号命名）。这些文件即环节7 要上传 Patent Center 的件。

参考 projects/set_skill/skill-catalog/skills/email/scripts/read_email.py 的 IMAP
登录 / UTF-7 文件夹名 / 邮件头解码。凭据复用本目录 scripts/email_config.json（多账号）。

用法：
  python3 fetch_uspto_upload_attachments.py <邮箱文件夹> [账号=docketing] [输出根目录=uspto_upload]
例：
  python3 fetch_uspto_upload_attachments.py "美代理签字回邮"
  python3 fetch_uspto_upload_attachments.py "美代理签字回邮" docketing uspto_upload

⚠️ 只读邮箱、只落本地文件；不移动/删除任何邮件。连真实邮箱，请在受控环境运行。
"""
import sys
import os
import re
import json
import base64
import imaplib
import email
from email.header import decode_header

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "scripts", "email_config.json")

# 案号格式：[0-9A-Z]{5}-[0-9A-Z]{4}[A-Z]{2}[0-9A-Z]{2}（如 20609-0083US01）
CASE_RE = re.compile(r"[0-9A-Z]{5}-[0-9A-Z]{4}[A-Z]{2}[0-9A-Z]{2}")


def load_account(account_key):
    """从 scripts/email_config.json 取指定账号配置（含 imap/oauth2）。"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    accounts = cfg.get("accounts") or {}
    if account_key not in accounts:
        raise SystemExit(f"email_config.json 中找不到账号 '{account_key}'，可用：{list(accounts)}")
    return accounts[account_key]


def _truthy(v):
    """配置里 enabled 可能是布尔 True 或字符串 'True'，统一判真。"""
    return str(v).strip().lower() in ("1", "true", "yes")


def get_oauth2_token(cfg):
    oauth = cfg.get("oauth2", {})
    if not _truthy(oauth.get("enabled")):
        return None
    import requests
    try:
        resp = requests.post(oauth["token_url"], data={
            "client_id": oauth["client_id"],
            "client_secret": oauth["client_secret"],
            "resource": oauth["resource"],
            "username": cfg["user"],
            "password": cfg.get("password", ""),
            "grant_type": "password",
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.partner.microsoftonline.cn",
        })
        data = resp.json()
        if "access_token" in data:
            return data["access_token"]
        print(f"OAuth2 获取 token 失败：{data.get('error_description', data)}")
        return None
    except Exception as e:
        print(f"OAuth2 请求失败：{e}")
        return None


def login_imap(cfg):
    """登录 IMAP，优先 OAuth2，失败降级密码认证（同参考脚本）。"""
    imap = imaplib.IMAP4_SSL(cfg["imap_host"], int(cfg["imap_port"]))
    token = get_oauth2_token(cfg)
    if token:
        auth_string = f"user={cfg['user']}\x01auth=Bearer {token}\x01\x01"
        try:
            imap.authenticate("XOAUTH2", lambda x: auth_string.encode())
            return imap
        except Exception as e:
            print(f"OAuth2 IMAP 登录失败，降级到密码认证：{e}")
    imap.login(cfg["user"], cfg["password"])
    return imap


def imap_utf7_encode(s):
    """把文件夹名编码为 IMAP modified UTF-7（中文文件夹名需要）。"""
    if all(0x20 <= ord(c) <= 0x7E for c in s):
        return s.replace("&", "&-")
    out, buf = [], []

    def flush():
        if buf:
            b64 = base64.b64encode("".join(buf).encode("utf-16-be")).decode()
            out.append("&" + b64.rstrip("=").replace("/", ",") + "-")
            buf.clear()

    for c in s:
        if 0x20 <= ord(c) <= 0x7E:
            flush()
            out.append("&-" if c == "&" else c)
        else:
            buf.append(c)
    flush()
    return "".join(out)


def select_folder(imap, folder):
    status, data = imap.select(f'"{imap_utf7_encode(folder)}"', readonly=True)
    if status != "OK":
        detail = data[0].decode(errors="replace") if data and data[0] else "不存在或无权限"
        raise SystemExit(f"无法打开文件夹 {folder}：{detail}")


def decode_str(s):
    """解码邮件头 / 附件名。"""
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


def iter_attachments(msg):
    """产出 (filename, payload_bytes)。只认真正的附件（有文件名或 Content-Disposition=attachment）。"""
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        disp = (part.get("Content-Disposition") or "").lower()
        raw_name = part.get_filename()
        if not raw_name and "attachment" not in disp:
            continue  # 正文等非附件部分
        filename = decode_str(raw_name).strip() if raw_name else ""
        if not filename:
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        yield filename, payload


def _safe_name(name):
    """去掉路径分隔符，避免附件名里带 / \\ 造成越界写入。"""
    return os.path.basename(name.replace("\\", "/")).strip() or "attachment"


def _unique_path(dir_path, filename):
    """同名文件已存在时追加 -1/-2… 避免覆盖。"""
    base, ext = os.path.splitext(filename)
    path = os.path.join(dir_path, filename)
    i = 1
    while os.path.exists(path):
        path = os.path.join(dir_path, f"{base}-{i}{ext}")
        i += 1
    return path


def fetch(folder, account_key="docketing", output_root="uspto_upload"):
    cfg = load_account(account_key)
    out_root = output_root if os.path.isabs(output_root) else os.path.join(SCRIPT_DIR, output_root)

    imap = login_imap(cfg)
    try:
        select_folder(imap, folder)
        _, msg_nums = imap.search(None, "ALL")
        msg_list = msg_nums[0].split()
        print(f"文件夹「{folder}」共 {len(msg_list)} 封邮件")

        saved_by_case = {}   # 案号 -> 存了几个附件
        emails_with_att = 0
        skipped_no_case = 0

        for num in msg_list:
            _, data = imap.fetch(num, "(RFC822)")
            if not data or not data[0]:
                continue
            msg = email.message_from_bytes(data[0][1])
            subject = decode_str(msg.get("Subject", ""))

            atts = list(iter_attachments(msg))
            if not atts:
                continue  # 无附件，跳过
            emails_with_att += 1

            for filename, payload in atts:
                fname = _safe_name(filename)
                m = CASE_RE.search(fname)
                if not m:
                    skipped_no_case += 1
                    print(f"  [跳过] 附件名无案号：{fname}（邮件：{subject[:40]}）")
                    continue
                case_no = m.group(0)
                case_dir = os.path.join(out_root, case_no)
                os.makedirs(case_dir, exist_ok=True)
                dest = _unique_path(case_dir, fname)
                with open(dest, "wb") as f:
                    f.write(payload)
                saved_by_case[case_no] = saved_by_case.get(case_no, 0) + 1
                print(f"  [存] {case_no}/ <- {os.path.basename(dest)}")

        print("\n===== 汇总 =====")
        print(f"含附件邮件：{emails_with_att} 封")
        print(f"归档案号：{len(saved_by_case)} 个 -> {out_root}")
        for case_no, n in sorted(saved_by_case.items()):
            print(f"  {case_no}: {n} 个附件")
        if skipped_no_case:
            print(f"附件名无案号被跳过：{skipped_no_case} 个")
    finally:
        try:
            imap.logout()
        except Exception:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 fetch_uspto_upload_attachments.py <邮箱文件夹> [账号=docketing] [输出根目录=uspto_upload]")
        sys.exit(1)
    folder_arg = sys.argv[1]
    account_arg = sys.argv[2] if len(sys.argv) > 2 else "docketing"
    output_arg = sys.argv[3] if len(sys.argv) > 3 else "uspto_upload"
    fetch(folder_arg, account_arg, output_arg)
