# email_core —— 可复用邮件收发核心库（接口说明）

抽自 `oa/read_email.py` 与 `report/submission_mailer.py`，逻辑不变。`account_cfg` 由调用方传入，不绑配置文件。依赖：标准库 + `requests`。目前为纯新增，未迁移原调用方。
可运行示例：`python3 scripts/examples/email_core_demo.py`。
测试：`python3 scripts/email_core/test_email_core.py`（6 条；MIME 解析/断点/取账号离线，收发不在单测内，已通过）。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts")
from email_core import config, read_emails, move_emails, send_html, parse_message
from email_core.checkpoint import update_checkpoint
acc = config.get_account_config("scripts/email_config.json", "docketing")
```

`account_cfg` 结构（同 email_config.json 的 accounts.<name>）：`imap_host/imap_port`（收）或 `smtp_host/smtp_port`（发）、`user/password`，可选 `oauth2:{enabled,token_url,client_id,client_secret,resource}`、`imap_timeout`。

## 逐函数：调用方法 / 输入 / 返回

### config（`config.py`）

| 函数 | 调用方法 | 输入 | 返回 |
|---|---|---|---|
| `load_config` | `load_config("scripts/email_config.json")` | path: str | dict（全量配置） |
| `get_account_config` | `get_account_config(cfg_or_path, "docketing")` | cfg: dict 或路径 str；account_name: str | account dict；账号不存在抛 KeyError |

### imap_client（`imap_client.py`，收信）

| 函数 | 调用方法 | 输入 | 返回 / 副作用 |
|---|---|---|---|
| `get_oauth2_token` | `get_oauth2_token(acc)` | account_cfg: dict | access_token str；未启用/失败→None |
| `login_imap` | `imap = login_imap(acc)` | account_cfg: dict | 已登录 IMAP4_SSL（XOAUTH2 优先、降级密码） |
| `list_folders` | `list_folders(acc)` | account_cfg: dict | 无（打印所有文件夹） |
| `read_emails` | `mails = read_emails(acc, folder="INBOX", count=10, account_name="docketing")` | account_cfg；folder="INBOX"；since/before: datetime｜None；count=50；attachment_dir｜None（传了落盘附件）；account_name｜None（传了走断点增量） | list[dict]（parse_message 结构+seq，从新到旧）；只读打开不改邮箱 |
| `move_emails` | `move_emails(acc, "INBOX", ids, target_folder="TEST_AUTO")` | account_cfg；folder；message_ids: list[str]；target_folder="TEST_AUTO" | int（移动条数）；**copy+删除 expunge，不可逆** |

### mime_parse（`mime_parse.py`，纯解析）

| 函数 | 调用方法 | 输入 | 返回 |
|---|---|---|---|
| `parse_message` | `d = parse_message(msg, attachment_dir=None)` | msg: email.message.Message；attachment_dir｜None | dict：subject/from/to/cc/date/message_id/body/html_body/attachments（+saved_attachments） |
| `decode_str` | `decode_str(msg.get("Subject"))` | s: str｜None（RFC2047 头） | 解码后 str；None→`""` |
| `html_to_text` | `html_to_text(html)` | html: str | 纯文本 str（剥 style/script） |
| `get_body` | `body, html = get_body(msg)` | msg: Message | (纯文本 str, html str) |
| `get_attachments` | `get_attachments(msg)` | msg: Message | list[{filename,content_type,size}]（不落盘） |
| `save_attachments` | `save_attachments(msg, "out_dir")` | msg: Message；output_dir: str | list[str]（落盘路径，重名加时分秒后缀） |
| `parse_email_date` | `parse_email_date(msg)` | msg: Message | ISO 字符串（解析失败返回原串，无→`""`） |
| `parse_address_list` | `parse_address_list(msg.get("To"))` | header_value: str｜None | list[str]（地址）；None→[] |

### checkpoint（`checkpoint.py`，增量去重）

| 函数 | 调用方法 | 输入 | 返回 / 副作用 |
|---|---|---|---|
| `set_checkpoint_path` | `set_checkpoint_path("cp.json")` | path: str | 无（覆盖默认断点文件路径） |
| `filter_new_emails` | `new = filter_new_emails(mails, "docketing", "INBOX")` | emails: list[dict]；account；folder | list[dict]（去掉 message_id 命中断点的） |
| `update_checkpoint` | `update_checkpoint("docketing", "INBOX", mails)` | account；folder；emails: list[dict] | 无（写断点，最多留 2000 条 ID） |
| `get_checkpoint` | `get_checkpoint("docketing", "INBOX")` | account；folder | dict（该键的断点信息） |
| `load_checkpoint` / `save_checkpoint` | `load_checkpoint()` / `save_checkpoint(d)` | 无 / dict | dict / 无（读写整个断点文件） |

### smtp_client（`smtp_client.py`，发信）

| 函数 | 调用方法 | 输入 | 返回 / 副作用 |
|---|---|---|---|
| `send_html` | `send_html("主题", "<b>正文</b>", ["to@x.com"], acc, cc_addrs=["cc@x.com"])` | subject；html；recipients: list[str]；account_cfg；cc_addrs｜None | 无（发一封 HTML 邮件，失败抛异常） |
| `send_smtp` | `send_smtp(msg, acc, recipients, cc_addrs=None)` | msg: MIMEMultipart；account_cfg；recipients；cc_addrs｜None | 无（发信，失败抛异常；会重写 msg 的 From/To/Cc） |
| `get_smtp_oauth2_token` | `get_smtp_oauth2_token(acc)` | account_cfg: dict | token str；未启用/失败→None |

## 来源与差异

| 本模块 | 抽自 |
|---|---|
| imap_client / mime_parse / checkpoint / get_smtp_oauth2_token | `oa/read_email.py`（与 `report/read_email.py` 逐字相同） |
| smtp_client.send_smtp / send_html | `report/submission_mailer.py` |

差异：`get_account_config` 缺账号时抛 KeyError（原 read_email 版是 sys.exit，库不宜退进程）；其余逻辑与源一致。
