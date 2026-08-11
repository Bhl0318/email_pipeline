#!/usr/bin/env python3
"""发信账号连通性测试：逐个测 email_config.json 里的账号能否真正 SMTP 发送。

主要用于验证「发美代理」按代理所切换的三个账号：
  metis_filling / poseidon_filling / porus_filling（patent_filling@ 各域）。

对每个账号会：①尝试取 OAuth2 token（成功/失败）②starttls 后用 XOAUTH2 或降级密码登录
③真发一封测试邮件到指定收件人。逐步打印，失败给出具体异常，便于判断是账号不在同租户、
不允许 ROPC、还是 SMTP 服务器/端口不对。

用法（在 scripts/report 目录下）：
  python test_send_accounts.py                         # 默认收件人 hailing.bi@metis-ip.com，测三个 filling 账号
  python test_send_accounts.py you@metis-ip.com        # 指定收件人
  python test_send_accounts.py you@metis-ip.com pa     # 指定收件人 + 只测某几个账号 key
  python test_send_accounts.py you@metis-ip.com metis_filling poseidon_filling porus_filling
"""
import os
import sys
import json
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests

CFG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_config.json")
DEFAULT_ACCOUNTS = ["metis_filling", "poseidon_filling", "porus_filling"]
DEFAULT_TO = "hailing.bi@metis-ip.com"


def _load_cfg():
    with open(CFG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _try_oauth2(acc):
    """取 OAuth2 token，返回 (token 或 None, 说明)。"""
    oauth = acc.get("oauth2", {})
    if not oauth.get("enabled"):
        return None, "该账号未启用 OAuth2（将直接用密码登录）"
    try:
        resp = requests.post(oauth["token_url"], data={
            "client_id": oauth["client_id"],
            "client_secret": oauth["client_secret"],
            "resource": oauth["resource"],
            "username": acc["user"],
            "password": acc["password"],
            "grant_type": "password",
        }, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
        data = resp.json()
        if "access_token" in data:
            return data["access_token"], "OAuth2 取 token 成功"
        return None, f"OAuth2 取 token 失败：{data.get('error_description') or data}"
    except Exception as e:  # noqa: BLE001
        return None, f"OAuth2 请求异常：{type(e).__name__}: {e}"


def test_account(key, acc, to_addr):
    print(f"\n===== 测试账号 [{key}] {acc.get('user')} =====")
    print(f"  SMTP: {acc.get('smtp_host')}:{acc.get('smtp_port')}")
    token, note = _try_oauth2(acc)
    print(f"  OAuth2: {note}")

    try:
        smtp = smtplib.SMTP(acc["smtp_host"], acc["smtp_port"], timeout=30)
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ 连不上 SMTP 服务器：{type(e).__name__}: {e}")
        return False
    try:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        auth_used = ""
        if token:
            auth_string = f"user={acc['user']}\x01auth=Bearer {token}\x01\x01"
            try:
                smtp.docmd("AUTH", "XOAUTH2 " + base64.b64encode(auth_string.encode()).decode())
                auth_used = "XOAUTH2"
            except smtplib.SMTPAuthenticationError as e:
                print(f"  OAuth2 认证被拒，降级密码登录：{e}")
                smtp.login(acc["user"], acc["password"])
                auth_used = "密码(OAuth2降级)"
        else:
            smtp.login(acc["user"], acc["password"])
            auth_used = "密码"
        print(f"  认证方式：{auth_used} ✅")

        msg = MIMEMultipart()
        msg["Subject"] = f"[发信测试] {key} {acc['user']}"
        msg["From"] = acc["user"]
        msg["To"] = to_addr
        msg.attach(MIMEText(
            f"这是账号 {key}（{acc['user']}）的 SMTP 发信测试。\n"
            f"认证方式：{auth_used}。收到即表示该账号可正常发信。", "plain", "utf-8"))
        smtp.sendmail(acc["user"], [to_addr], msg.as_string())
        print(f"  ✅ 已发送测试邮件到 {to_addr}（请到收件箱确认收到）")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ 发送失败：{type(e).__name__}: {e}")
        return False
    finally:
        try:
            smtp.quit()
        except Exception:
            pass


def main(argv):
    to_addr = argv[1] if len(argv) > 1 else DEFAULT_TO
    keys = argv[2:] if len(argv) > 2 else DEFAULT_ACCOUNTS
    cfg = _load_cfg()
    accounts = cfg.get("accounts", {})
    print(f"收件人：{to_addr}")
    print(f"待测账号：{', '.join(keys)}")
    results = {}
    for k in keys:
        acc = accounts.get(k)
        if not acc:
            print(f"\n===== [{k}] ⚠️ email_config.json 无此账号，跳过 =====")
            results[k] = None
            continue
        results[k] = test_account(k, acc, to_addr)

    print("\n========== 汇总 ==========")
    for k, ok in results.items():
        mark = "✅ 可发送" if ok else ("⚠️ 无此账号" if ok is None else "❌ 失败")
        print(f"  {k:18} {mark}")


if __name__ == "__main__":
    main(sys.argv)
