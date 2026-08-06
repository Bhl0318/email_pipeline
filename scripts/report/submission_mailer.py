#!/usr/bin/env python3
"""US 递交 · 自包含 SMTP 发信小工具（供环节7 机 D:\\up_uspto 发环节8 预览链接用）。

不依赖 FastAPI/report_server——只读同目录 email_config.json 的 accounts.{key}，
OAuth2（password 授权）优先、失败降级密码认证，逻辑与 report_server._send_smtp 一致。
仅新增、不改动任何现有流程代码。
"""
import os
import sys
import json
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import getaddresses

import requests

_CFG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_config.json")


def _load_cfg():
    with open(_CFG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _account_cfg(cfg, key):
    acc = (cfg.get("accounts") or {}).get(key)
    if not acc:
        raise RuntimeError(f"email_config.json 缺少 accounts.{key}")
    return acc


def _oauth2_token(account_cfg):
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
        print(f"[mailer] OAuth2 取 token 失败: {data.get('error_description', data)}", file=sys.stderr)
    except Exception as e:  # noqa: BLE001
        print(f"[mailer] OAuth2 请求失败: {e}", file=sys.stderr)
    return None


def _send_smtp(msg, account_cfg, recipients, cc_addrs=None):
    """发送 MIMEMultipart。OAuth2 优先、失败降级密码。失败抛异常。"""
    smtp = smtplib.SMTP(account_cfg["smtp_host"], account_cfg["smtp_port"], timeout=30)
    try:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        token = _oauth2_token(account_cfg)
        if token:
            auth_string = f"user={account_cfg['user']}\x01auth=Bearer {token}\x01\x01"
            try:
                smtp.docmd("AUTH", "XOAUTH2 " + base64.b64encode(auth_string.encode()).decode())
            except smtplib.SMTPAuthenticationError:
                print("[mailer] OAuth2 认证失败，降级密码认证", file=sys.stderr)
                smtp.login(account_cfg["user"], account_cfg["password"])
        else:
            smtp.login(account_cfg["user"], account_cfg["password"])
        if msg["From"]: del msg["From"]
        if msg["To"]:   del msg["To"]
        if msg["Cc"]:   del msg["Cc"]
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


def send_html(subject, html, recipients, cc_addrs=None, account_key=None):
    """发一封 HTML 邮件。account_key 缺省用 submission.account（再缺省 'pa'）。失败抛异常。"""
    cfg = _load_cfg()
    sub = cfg.get("submission") or {}
    key = account_key or sub.get("account") or "pa"
    account_cfg = _account_cfg(cfg, key)
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html", "utf-8"))
    _send_smtp(msg, account_cfg, recipients, cc_addrs)


def uspto_review_recipients():
    """环节8 预览链接收件人：submission.uspto_review_recipients，缺省 hailing.bi@metis-ip.com。"""
    sub = (_load_cfg().get("submission") or {})
    rec = [r for r in (sub.get("uspto_review_recipients") or []) if r]
    return rec or ["hailing.bi@metis-ip.com"]


def review_base_url():
    """预览页 base：submission.review_base_url，缺省 http://10.10.70.88:8501。"""
    sub = (_load_cfg().get("submission") or {})
    return (sub.get("review_base_url") or "http://10.10.70.88:8501").rstrip("/")
