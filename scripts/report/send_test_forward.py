#!/usr/bin/env python3
"""测试"原样转发"链路：读 PA 邮箱指定文件夹里的邮件，用二期真正的转发函数
`_forward_official_email` 原样转发（原件作 .eml 附件、从 pa 账号发）给指定收件人。

用法：
  python3 send_test_forward.py [收件人] [文件夹]
  默认：收件人=hailing.bi@metis-ip.com，文件夹=huibaoxin_TEST

前提：在 PA 邮箱(patents_pa@metis-ip.com)的该文件夹里放好待转发的测试邮件。
只读取+转发，不删邮件、不碰数据库、不动任务。
"""
import os
import sys
import json
import email

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from read_email import login_imap, _forward_official_email, decode_str  # noqa: E402

CONFIG_PATH = os.path.join(SCRIPT_DIR, "email_config.json")


def main():
    to_addr = sys.argv[1].strip() if len(sys.argv) > 1 else "hailing.bi@metis-ip.com"
    folder = sys.argv[2].strip() if len(sys.argv) > 2 else "huibaoxin_TEST"

    cfg = json.load(open(CONFIG_PATH, encoding="utf-8"))
    pa = cfg.get("accounts", {}).get("pa")
    if not pa:
        print("[!] email_config.json 缺 accounts.pa", file=sys.stderr)
        sys.exit(1)

    # pa 是发信账号，可能没配 imap_host —— 补上（同租户 IMAP 端点）
    imap_cfg = dict(pa)
    if not imap_cfg.get("imap_host"):
        doc = cfg.get("accounts", {}).get("docketing", {})
        imap_cfg["imap_host"] = doc.get("imap_host", "smtp.partner.outlook.cn")
        imap_cfg["imap_port"] = doc.get("imap_port", 993)

    print(f"读 {pa['user']} 的文件夹「{folder}」，转发给 {to_addr} …")
    imap = login_imap(imap_cfg)
    try:
        status, _ = imap.select(f'"{folder}"', readonly=True)
        if status != "OK":
            print(f"[!] 打不开文件夹「{folder}」（检查名字/是否存在）", file=sys.stderr)
            sys.exit(1)
        status, data = imap.search(None, "ALL")
        nums = data[0].split() if data and data[0] else []
        if not nums:
            print(f"[i] 文件夹「{folder}」里没有邮件", file=sys.stderr)
            return
        print(f"共 {len(nums)} 封，逐封转发：")
        for num in nums:
            _, d = imap.fetch(num, "(RFC822)")
            raw = d[0][1]
            subject = decode_str(email.message_from_bytes(raw).get("Subject", "")) or "(无主题)"
            print(f"  → 转发：{subject}")
            _forward_official_email(pa, raw, subject, [to_addr], [])
    finally:
        try: imap.logout()
        except Exception: pass


if __name__ == "__main__":
    main()
