"""SMTP 发信客户端（可复用）。

SMTP OAuth2 取 token 抽自 oa/read_email.py；send_smtp/send_html 抽自
report/submission_mailer.py（自包含发信，与 report_server._send_smtp 同逻辑）。
STARTTLS + XOAUTH2 优先、失败降级密码。account_cfg 由调用方传入，不绑配置文件。

依赖：标准库 smtplib/email + requests。
"""
import base64
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import getaddresses

import requests


def get_smtp_oauth2_token(account_cfg):
    """换 SMTP 用 OAuth2 token；未启用/失败返回 None。

    输入：account_cfg dict（oauth2.{token_url,client_id,client_secret,resource}+user/password）
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
        }, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
        data = resp.json()
        if "access_token" in data:
            return data["access_token"]
        print(f"[smtp] OAuth2 取 token 失败: {data.get('error_description', data)}", file=sys.stderr)
    except Exception as e:  # noqa: BLE001
        print(f"[smtp] OAuth2 请求失败: {e}", file=sys.stderr)
    return None


def send_smtp(msg, account_cfg, recipients, cc_addrs=None):
    """发送已构造的 MIMEMultipart。XOAUTH2 优先、失败降级密码。失败抛异常。

    输入：msg(MIMEMultipart)、account_cfg(需 smtp_host/smtp_port/user/password[/oauth2])、
          recipients(list[str])、cc_addrs(list[str]|None)
    输出：无（副作用：发信）；会重写 msg 的 From/To/Cc 头。
    """
    smtp = smtplib.SMTP(account_cfg["smtp_host"], account_cfg["smtp_port"], timeout=30)
    try:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        token = get_smtp_oauth2_token(account_cfg)
        if token:
            auth_string = f"user={account_cfg['user']}\x01auth=Bearer {token}\x01\x01"
            try:
                smtp.docmd("AUTH", "XOAUTH2 " + base64.b64encode(auth_string.encode()).decode())
            except smtplib.SMTPAuthenticationError:
                print("[smtp] OAuth2 认证失败，降级密码认证", file=sys.stderr)
                smtp.login(account_cfg["user"], account_cfg["password"])
        else:
            smtp.login(account_cfg["user"], account_cfg["password"])
        if msg["From"]:
            del msg["From"]
        if msg["To"]:
            del msg["To"]
        if msg["Cc"]:
            del msg["Cc"]
        msg["From"] = account_cfg["user"]
        msg["To"] = ", ".join(recipients)
        if cc_addrs:
            msg["Cc"] = ", ".join(cc_addrs)
        all_rcpts = [addr for _, addr in getaddresses(recipients + (cc_addrs or [])) if addr]
        smtp.sendmail(account_cfg["user"], all_rcpts, msg.as_string())
    finally:
        try:
            smtp.quit()
        except Exception:
            pass


def send_html(subject, html, recipients, account_cfg, cc_addrs=None):
    """发一封 HTML 邮件（便捷封装）。失败抛异常。

    输入：subject、html、recipients(list[str])、account_cfg、cc_addrs
    输出：无（副作用：发信）
    """
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html", "utf-8"))
    send_smtp(msg, account_cfg, recipients, cc_addrs)
