"""IMAP 收信客户端（可复用）。

抽自 oa/read_email.py 的 get_oauth2_token/login_imap/list_folders/read_emails/move_emails，
逻辑不变。OAuth2(XOAUTH2) 优先、失败降级密码认证。account_cfg 由调用方传入，不绑配置文件。

依赖：标准库 imaplib/email + requests。
"""
import email
import imaplib
import sys

import requests

from .mime_parse import parse_message
from .checkpoint import filter_new_emails


def get_oauth2_token(account_cfg):
    """用 password 授权换 access_token 做 XOAUTH2；未启用/失败返回 None。

    输入：account_cfg dict（需含 oauth2.{token_url,client_id,client_secret,resource} 与 user/password）
    输出：str | None
    """
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
        print(f"OAuth2 获取 token 失败: {data.get('error_description', data)}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"OAuth2 请求失败: {e}", file=sys.stderr)
        return None


def login_imap(account_cfg):
    """建 IMAP4_SSL 连接并登录（XOAUTH2 优先、失败降级密码）。返回已登录连接。

    输入：account_cfg dict（imap_host/imap_port/user/password，可选 imap_timeout/oauth2）
    输出：imaplib.IMAP4_SSL
    """
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


def list_folders(account_cfg):
    """打印邮箱所有文件夹（调试用）。输入 account_cfg，无返回。"""
    imap = login_imap(account_cfg)
    status, folders = imap.list()
    if status == "OK":
        for f in folders:
            print(f.decode("utf-8", errors="replace"))
    imap.logout()


def read_emails(account_cfg, folder="INBOX", since=None, before=None,
                count=50, attachment_dir=None, account_name=None):
    """读取邮件，返回结构化列表（只读打开，不改邮箱）。

    输入：
      account_cfg  账号 dict
      folder       文件夹名（默认 INBOX）
      since/before datetime，转 IMAP SINCE/BEFORE 搜索
      count        最多取最新 N 封（默认 50）
      attachment_dir  传了则落盘附件
      account_name 传了则用断点过滤已处理邮件（增量）
    输出：list[dict]（parse_message 的结构，含 seq；从新到旧）
    """
    imap = login_imap(account_cfg)
    status, _ = imap.select(f'"{folder}"', readonly=True)
    if status != "OK":
        print(f"错误: 无法打开文件夹 '{folder}'", file=sys.stderr)
        imap.logout()
        return []

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

    if len(msg_list) > count:
        msg_list = msg_list[-count:]
    msg_list.reverse()

    results = []
    for i, num in enumerate(msg_list):
        _, data = imap.fetch(num, "(RFC822)")
        raw = data[0][1]
        msg = email.message_from_bytes(raw)
        parsed = parse_message(msg, attachment_dir)
        parsed["seq"] = i + 1
        results.append(parsed)
        if (i + 1) % 10 == 0:
            print(f"已读取 {i + 1}/{len(msg_list)} 封...", file=sys.stderr)
    print(f"共读取 {len(results)} 封邮件", file=sys.stderr)
    imap.logout()

    if account_name:
        results = filter_new_emails(results, account_name, folder)
        print(f"其中 {len(results)} 封为新邮件", file=sys.stderr)
    return results


def move_emails(account_cfg, folder, message_ids, target_folder="TEST_AUTO"):
    """按 Message-ID 把邮件从 folder 移动到 target_folder（copy+删除 expunge，不可逆）。

    输入：account_cfg、folder、message_ids(list[str])、target_folder
    输出：int（成功移动条数）；副作用：改动邮箱
    """
    if not message_ids:
        return 0
    imap = login_imap(account_cfg)
    imap.create(f'"{target_folder}"')
    status, _ = imap.select(f'"{folder}"')
    if status != "OK":
        print(f"错误: 无法打开文件夹 '{folder}'", file=sys.stderr)
        imap.logout()
        return 0

    moved = 0
    for msg_id in message_ids:
        _, nums = imap.search(None, f'HEADER Message-ID "{msg_id}"')
        for num in nums[0].split():
            if not num:
                continue
            status, _ = imap.copy(num, f'"{target_folder}"')
            if status == "OK":
                imap.store(num, "+FLAGS", "\\Deleted")
                moved += 1
    imap.expunge()
    imap.logout()
    print(f"已移动 {moved} 封邮件到 {target_folder}", file=sys.stderr)
    return moved
