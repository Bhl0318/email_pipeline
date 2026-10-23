#!/usr/bin/env python3
"""只读列出指定邮箱文件夹中的原始邮件 Message-ID。

示例：
  python check_mail_ids.py --account docketing --folder INBOX --count 50
  python check_mail_ids.py --account docketing --folder "Metis+Porus+Poseidon/Done" --since 2026-10-21 --count 0

每行输出一个 Message-ID；--count 0 表示输出搜索范围内的全部邮件。
不读取邮件正文、不更新断点、不改变已读状态、不移动邮件。
"""

import argparse
import email
import json
import re
import sys
from datetime import datetime
from pathlib import Path

FOUNDATION_DIR = Path(__file__).resolve().parent / "reusable" / "foundation"
sys.path.insert(0, str(FOUNDATION_DIR))

from email_core.imap_client import login_imap  # noqa: E402


def _date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d-%b-%Y")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("日期格式应为 YYYY-MM-DD") from exc


def list_mail_ids(imap, folder, *, since=None, before=None, count=50):
    """按 IMAP UID 从新到旧读取邮件头，返回 Message-ID 列表。"""
    safe_folder = folder.replace("\\", "\\\\").replace('"', '\\"')
    status, _ = imap.select(f'"{safe_folder}"', readonly=True)
    if status != "OK":
        raise RuntimeError(f"无法打开邮箱文件夹: {folder}")

    criteria = []
    if since:
        criteria.extend(("SINCE", since))
    if before:
        criteria.extend(("BEFORE", before))
    status, result = imap.uid("SEARCH", None, *(criteria or ["ALL"]))
    if status != "OK":
        raise RuntimeError(f"搜索邮箱文件夹失败: {folder}")
    uids = result[0].split() if result and result[0] else []
    if count:
        uids = uids[-count:]

    message_ids = []
    for uid in reversed(uids):
        status, parts = imap.uid("FETCH", uid, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])")
        if status != "OK":
            print(f"[跳过] UID {uid.decode('ascii', errors='replace')} 邮件头读取失败", file=sys.stderr)
            continue
        raw_header = next((part[1] for part in parts if isinstance(part, tuple) and isinstance(part[1], bytes)), None)
        if raw_header is None:
            continue
        msg = email.message_from_bytes(raw_header)
        message_id = re.sub(r"\s+", "", msg.get("Message-ID", "") or "")
        if message_id:
            message_ids.append(message_id)
        else:
            print(f"[跳过] UID {uid.decode('ascii', errors='replace')} 没有 Message-ID", file=sys.stderr)
    return message_ids


def main():
    parser = argparse.ArgumentParser(description="只读打印指定邮箱文件夹的原始邮件 Message-ID")
    parser.add_argument("--account", default="docketing", help="email_config.json 中的账号名称（默认 docketing）")
    parser.add_argument("--folder", default="INBOX", help="邮箱文件夹（默认 INBOX）")
    parser.add_argument("--count", type=int, default=50, help="最多读取最新 N 封；0 表示全部（默认 50）")
    parser.add_argument("--since", type=_date, help="起始日期 YYYY-MM-DD（含当天）")
    parser.add_argument("--before", type=_date, help="截止日期 YYYY-MM-DD（不含当天）")
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parent / "email_config.json",
                        help="邮箱配置文件路径")
    args = parser.parse_args()
    if args.count < 0:
        parser.error("--count 不能小于 0")
    if "\r" in args.folder or "\n" in args.folder:
        parser.error("--folder 不能包含换行")

    with args.config.open(encoding="utf-8") as handle:
        accounts = json.load(handle).get("accounts", {})
    if args.account not in accounts:
        parser.error(f"账号 {args.account!r} 不存在；可用账号: {', '.join(accounts)}")

    imap = login_imap(accounts[args.account])
    try:
        for message_id in list_mail_ids(imap, args.folder, since=args.since,
                                        before=args.before, count=args.count):
            print(message_id)
    finally:
        imap.logout()


if __name__ == "__main__":
    main()
