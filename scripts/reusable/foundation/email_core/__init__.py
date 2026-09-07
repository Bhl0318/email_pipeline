"""email_core —— 可复用邮件收发核心库。

抽自 oa/read_email.py 与 report/submission_mailer.py（两条业务线原本各拷一份），
逻辑不变，作为独立可复用资产。account_cfg 由调用方传入，不绑死配置文件。
目前为纯新增资产，未迁移原调用方（原文件仍保留各自实现）。

子模块：
  config       load_config / get_account_config
  imap_client  get_oauth2_token / login_imap / list_folders / read_emails / move_emails
  mime_parse   decode_str / html_to_text / get_body / get_attachments / save_attachments /
               parse_email_date / parse_address_list / parse_message
  checkpoint   load/save/get/update_checkpoint / filter_new_emails / set_checkpoint_path
  smtp_client  get_smtp_oauth2_token / send_smtp / send_html

用法：
    from email_core import config, read_emails, send_html
    acc = config.get_account_config("scripts/email_config.json", "docketing")
    mails = read_emails(acc, folder="INBOX", count=10)
"""
from . import config, imap_client, mime_parse, checkpoint, smtp_client
from .imap_client import get_oauth2_token, login_imap, list_folders, read_emails, move_emails
from .mime_parse import (
    decode_str, html_to_text, get_body, get_attachments, save_attachments,
    parse_email_date, parse_address_list, parse_message,
)
from .checkpoint import (
    load_checkpoint, save_checkpoint, get_checkpoint, update_checkpoint,
    filter_new_emails, set_checkpoint_path,
)
from .smtp_client import get_smtp_oauth2_token, send_smtp, send_html

__all__ = [
    "config", "imap_client", "mime_parse", "checkpoint", "smtp_client",
    "get_oauth2_token", "login_imap", "list_folders", "read_emails", "move_emails",
    "decode_str", "html_to_text", "get_body", "get_attachments", "save_attachments",
    "parse_email_date", "parse_address_list", "parse_message",
    "load_checkpoint", "save_checkpoint", "get_checkpoint", "update_checkpoint",
    "filter_new_emails", "set_checkpoint_path",
    "get_smtp_oauth2_token", "send_smtp", "send_html",
]
