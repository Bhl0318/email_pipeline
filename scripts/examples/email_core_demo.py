"""email_core 用法示例。

离线部分（MIME 解析）直接跑并打印输入→输出；
收发部分（IMAP/SMTP）需真实账号，只示范调用写法（默认不执行）。

运行：python3 scripts/examples/email_core_demo.py
"""
import email
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from email_core import parse_message, decode_str, html_to_text  # noqa: E402

RAW = """From: =?utf-8?B?5byg5LiJ?= <zhang@example.com>
To: a@example.com, b@example.com
Cc: c@example.com
Subject: =?utf-8?B?5rWL6K+V6YKu5Lu2?=
Date: Mon, 02 Feb 2026 10:00:00 +0800
Message-ID: <abc123@example.com>
Content-Type: text/plain; charset="utf-8"

正文内容第一行。
"""


def demo_offline():
    print("== MIME 解析（离线）==")
    msg = email.message_from_bytes(RAW.encode("utf-8"))
    parsed = parse_message(msg)
    for k in ("subject", "from", "to", "cc", "date", "message_id", "body"):
        print(f"  {k:<11}: {parsed[k]!r}")
    print("  decode_str(乱码头) :", decode_str("=?utf-8?B?5byg5LiJ?="))
    print("  html_to_text       :", html_to_text("<p>你好<script>x=1</script>世界</p>"))


def demo_network_syntax():
    print("\n== 收发（需真实账号，仅示范写法，不执行）==")
    print(r"""
    from email_core import config, read_emails, move_emails, send_html
    from email_core.checkpoint import update_checkpoint

    acc = config.get_account_config("scripts/email_config.json", "docketing")

    # 读最近 10 封（account_name 传了则按断点增量去重）
    mails = read_emails(acc, folder="INBOX", count=10, account_name="docketing")
    # 处理后记断点
    update_checkpoint("docketing", "INBOX", mails)
    # 归档：把处理过的移走（不可逆）
    move_emails(acc, "INBOX", [m["message_id"] for m in mails], target_folder="TEST_AUTO")

    # 发信（account_cfg 需含 smtp_host/smtp_port）
    pa = config.get_account_config("scripts/email_config.json", "pa")
    send_html("主题", "<b>正文</b>", ["to@example.com"], pa, cc_addrs=["cc@example.com"])
    """)


if __name__ == "__main__":
    demo_offline()
    demo_network_syntax()
