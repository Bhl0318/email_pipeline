#!/usr/bin/env python3
"""Message-ID 折行清洗 + _inbox 目录名合法性 的复现/回归测试。

复现 [WinError 123]：折行 Message-ID 含 \\r\\n\\t，被当目录名建到 output/_inbox/ 下失败。
  cd scripts/report && python3 test_msgid_sanitize.py
"""
import os
import sys
import re
import email

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from read_email import parse_message

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def test_folded_message_id_cleaned():
    # 构造 Message-ID 被折行（\r\n + 制表符）的邮件，复现线上那封
    raw = (
        "Subject: test\r\n"
        "From: a@b.com\r\n"
        "Message-ID: <\r\n\t_SH0PR01MB08573EAE1_SH0PR01MB0857_CHNPR01"
        "@SH0PR01MB0857.CHNPR01.prod.partner.outlook.cn>\r\n"
        "\r\nbody\r\n"
    )
    msg = email.message_from_string(raw)
    p = parse_message(msg)
    mid = p["message_id"]
    ok(not any(c in mid for c in "\r\n\t"), f"message_id 无 \\r\\n\\t (repr={mid!r})")
    ok(mid.startswith("<") and mid.endswith(">"), "message_id 仍是 <...> 形式")


def test_inbox_dirname_legal():
    # 用清洗后的 msgid 造 _inbox 目录名，不含非法/空白字符
    mid = "<_SH0PR01MB08573EAE1_SH0PR01@SH0PR01MB0857.CHNPR01.prod.partner.outlook.cn>"
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', mid or '').strip('_')[:80] or "seq_1"
    ok(not any(c in safe for c in '\r\n\t /\\:*?"<>|'), f"目录名合法 (safe={safe!r})")
    ok(len(safe) <= 80, "目录名长度受限 <=80")


if __name__ == "__main__":
    for fn in [test_folded_message_id_cleaned, test_inbox_dirname_legal]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
