#!/usr/bin/env python3
"""发一封测试邮件，验证发信账号是否可用（OAuth2 XOAUTH2 优先，降级密码）。

用法：
  python3 send_test_email.py <收件人邮箱> [账号]
  账号可选：pa(默认,patents_pa,转发/审核通知用) / qxt(七星天 report@) / zhyc(众慧 report_zhyc@)

示例：
  python3 send_test_email.py hailing.bi@metis-ip.com
  python3 send_test_email.py hailing.bi@metis-ip.com zhyc

只发一封纯文本测试邮件，不碰数据库、不动任何任务。
"""
import os
import sys
import json
import base64
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "email_config.json")


def _get_account(cfg, key):
    """pa 从 accounts.pa；qxt/zhyc 从 senders。返回发信账号 dict。"""
    if key == "pa":
        return cfg.get("accounts", {}).get("pa")
    return (cfg.get("senders", {}) or {}).get(key)


def _get_token(acc):
    o = acc.get("oauth2", {})
    if not o.get("enabled"):
        return None
    r = requests.post(o["token_url"], data={
        "client_id": o["client_id"], "client_secret": o["client_secret"],
        "resource": o["resource"], "username": acc["user"], "password": acc["password"],
        "grant_type": "password",
    }, timeout=30).json()
    if "access_token" in r:
        return r["access_token"]
    print(f"[!] OAuth2 取 token 失败: {r.get('error')} - {r.get('error_description','')[:160]}",
          file=sys.stderr)
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    to_addr = sys.argv[1].strip()
    key = sys.argv[2].strip() if len(sys.argv) > 2 else "pa"

    cfg = json.load(open(CONFIG_PATH, encoding="utf-8"))
    acc = _get_account(cfg, key)
    if not acc:
        print(f"[!] email_config.json 里找不到账号 {key}", file=sys.stderr)
        sys.exit(1)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = MIMEText(f"这是一封测试邮件。\n账号: {acc['user']}\n时间: {now}\n", "plain", "utf-8")
    msg["From"] = acc["user"]
    msg["To"] = to_addr
    msg["Subject"] = f"[测试邮件] {key} {now}"

    print(f"发信账号: {acc['user']}  → 收件人: {to_addr}")
    smtp = smtplib.SMTP(acc["smtp_host"], acc["smtp_port"], timeout=30)
    try:
        smtp.ehlo(); smtp.starttls(); smtp.ehlo()
        token = _get_token(acc)
        authed = False
        if token:
            auth = f"user={acc['user']}\x01auth=Bearer {token}\x01\x01"
            code, resp = smtp.docmd("AUTH", "XOAUTH2 " + base64.b64encode(auth.encode()).decode())
            if code == 334:
                code, resp = smtp.docmd("")
            authed = (code == 235)
            if not authed:
                print(f"[!] XOAUTH2 认证未通过({code}): {resp}", file=sys.stderr)
        if not authed:
            print("[i] 尝试密码登录…", file=sys.stderr)
            smtp.login(acc["user"], acc["password"])
        smtp.sendmail(acc["user"], [to_addr], msg.as_string())
        print("✅ 发送成功")
    except Exception as e:
        print(f"❌ 发送失败: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        try: smtp.quit()
        except Exception: pass


if __name__ == "__main__":
    main()
