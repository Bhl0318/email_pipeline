"""email_core 测试用例（离线，不连 IMAP/SMTP）。

覆盖：MIME 解析、断点增量去重、config 取账号。收发本身需真实服务器，不在单测内。

运行：python3 scripts/email_core/test_email_core.py   或   pytest scripts/email_core/test_email_core.py
"""
import email
import os
import sys
import tempfile
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from email_core import (  # noqa: E402
    parse_message, decode_str, html_to_text, get_body, get_attachments,
    parse_address_list, config,
)
from email_core import checkpoint  # noqa: E402

RAW = """From: =?utf-8?B?5byg5LiJ?= <zhang@example.com>
To: a@example.com, b@example.com
Cc: c@example.com
Subject: =?utf-8?B?5rWL6K+V6YKu5Lu2?=
Date: Mon, 02 Feb 2026 10:00:00 +0800
Message-ID: <abc123@example.com>
Content-Type: text/plain; charset="utf-8"

正文第一行。
""".encode("utf-8")


def test_parse_message():
    m = parse_message(email.message_from_bytes(RAW))
    assert m["subject"] == "测试邮件"
    assert m["from"] == "张三 <zhang@example.com>"
    assert m["to"] == ["a@example.com", "b@example.com"]
    assert m["cc"] == ["c@example.com"]
    assert m["date"] == "2026-02-02T10:00:00+08:00"
    assert m["message_id"] == "<abc123@example.com>"
    assert m["body"] == "正文第一行。"


def test_decode_and_html():
    assert decode_str("=?utf-8?B?5byg5LiJ?=") == "张三"
    assert decode_str(None) == ""
    assert html_to_text("<p>你好<script>x=1</script>世界</p>") == "你好世界"


def test_parse_address_list():
    assert parse_address_list("a@x.com, b@x.com; c@x.com") == ["a@x.com", "b@x.com", "c@x.com"]
    assert parse_address_list(None) == []


def _multipart_with_attachment():
    msg = MIMEMultipart()
    msg["Subject"] = "带附件"
    msg.attach(MIMEText("正文", "plain", "utf-8"))
    part = MIMEBase("application", "pdf")
    part.set_payload(b"%PDF-1.4 fake")
    part.add_header("Content-Disposition", "attachment", filename="a.pdf")
    msg.attach(part)
    return email.message_from_bytes(msg.as_bytes())


def test_get_body_and_attachments():
    msg = _multipart_with_attachment()
    body, _ = get_body(msg)
    assert body == "正文"
    atts = get_attachments(msg)
    assert len(atts) == 1 and atts[0]["filename"] == "a.pdf"
    assert atts[0]["content_type"] == "application/pdf"


def test_checkpoint_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        checkpoint.set_checkpoint_path(os.path.join(d, "cp.json"))
        mails = [{"message_id": "<m1>", "date": "2026-02-01"},
                 {"message_id": "<m2>", "date": "2026-02-02"}]
        checkpoint.update_checkpoint("acc", "INBOX", mails)
        cp = checkpoint.get_checkpoint("acc", "INBOX")
        assert set(cp["processed_ids"]) == {"<m1>", "<m2>"}
        assert cp["last_time"] == "2026-02-02"
        # 再来一批含旧的 <m2> 与新的 <m3>，应只留 <m3>
        nxt = [{"message_id": "<m2>", "date": "2026-02-02"},
               {"message_id": "<m3>", "date": "2026-02-03"}]
        assert [m["message_id"] for m in checkpoint.filter_new_emails(nxt, "acc", "INBOX")] == ["<m3>"]


def test_get_account_config():
    cfg = {"accounts": {"docketing": {"user": "x@y.com"}}}
    assert config.get_account_config(cfg, "docketing")["user"] == "x@y.com"
    try:
        config.get_account_config(cfg, "nope")
    except KeyError:
        return
    raise AssertionError("缺账号应抛 KeyError")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("ok", fn.__name__)
    print(f"all passed ({len(fns)})")
