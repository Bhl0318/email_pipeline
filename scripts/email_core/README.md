# email_core —— 可复用邮件收发核心库（接口说明）

抽自 `oa/read_email.py` 与 `report/submission_mailer.py`（两条业务线原本各拷一份），逻辑不变。
`account_cfg` 由调用方传入，不绑死配置文件。依赖：标准库 + `requests`。
目前为纯新增资产，未迁移原调用方。

可运行示例：`python3 scripts/examples/email_core_demo.py`（MIME 解析部分离线实跑；收发部分需真实账号，仅示范写法）。

## 如何调

```python
import os, sys
sys.path.insert(0, "<...>/scripts")
from email_core import config, read_emails, send_html
acc = config.get_account_config("scripts/email_config.json", "docketing")
```

`account_cfg` 结构（同 email_config.json 的 accounts.<name>）：
`imap_host/imap_port`（收）或 `smtp_host/smtp_port`（发）、`user/password`，可选
`oauth2:{enabled,token_url,client_id,client_secret,resource}`、`imap_timeout`。

## 接口

### config（`config.py`）

| 函数 | 输入 | 输出 |
|---|---|---|
| `load_config(path)` | 配置文件路径 | dict（全量） |
| `get_account_config(cfg, name)` | dict 或路径, 账号名 | account dict；不存在抛 KeyError |

### imap_client（`imap_client.py`）

| 函数 | 输入 | 输出 / 副作用 |
|---|---|---|
| `get_oauth2_token(account_cfg)` | 账号 dict | access_token str｜None |
| `login_imap(account_cfg)` | 账号 dict | 已登录 IMAP4_SSL（XOAUTH2 优先、降级密码） |
| `list_folders(account_cfg)` | 账号 dict | 打印文件夹（无返回） |
| `read_emails(account_cfg, folder="INBOX", since=None, before=None, count=50, attachment_dir=None, account_name=None)` | since/before 为 datetime；account_name 传了走断点增量 | list[dict]（parse_message 结构，从新到旧）；只读打开不改邮箱 |
| `move_emails(account_cfg, folder, message_ids, target_folder="TEST_AUTO")` | Message-ID 列表 | int 移动条数；**copy+删除 expunge，不可逆** |

### mime_parse（`mime_parse.py`，纯函数）

| 函数 | 输入 | 输出 |
|---|---|---|
| `parse_message(msg, attachment_dir=None)` | email.message.Message | dict：subject/from/to/cc/date/message_id/body/html_body/attachments（+saved_attachments） |
| `decode_str(s)` | 邮件头 str｜None | 解码后 str |
| `html_to_text(html)` | str | 纯文本（剥 style/script） |
| `get_body(msg)` | Message | (纯文本, html) |
| `get_attachments(msg)` | Message | list[{filename,content_type,size}]（不落盘） |
| `save_attachments(msg, output_dir)` | Message, 目录 | list[路径]（落盘，重名加后缀） |
| `parse_email_date(msg)` / `parse_address_list(header)` | Message / 头值 | ISO 字符串 / 地址列表 |

### checkpoint（`checkpoint.py`，增量去重）

| 函数 | 输入 | 输出 / 副作用 |
|---|---|---|
| `set_checkpoint_path(path)` | 路径 | 覆盖默认断点文件（默认 email_core/checkpoint.json） |
| `filter_new_emails(emails, account, folder)` | 邮件列表 + 键 | list[dict]（去掉已处理的） |
| `update_checkpoint(account, folder, emails)` | 键 + 邮件 | 无（写断点，最多留 2000 条 ID） |
| `get_checkpoint / load_checkpoint / save_checkpoint` | — | 断点 dict 读写 |

### smtp_client（`smtp_client.py`）

| 函数 | 输入 | 输出 / 副作用 |
|---|---|---|
| `get_smtp_oauth2_token(account_cfg)` | 账号 dict | token str｜None |
| `send_smtp(msg, account_cfg, recipients, cc_addrs=None)` | 已构造 MIMEMultipart + 账号 + 收件人 | 无（发信，失败抛异常；会重写 From/To/Cc） |
| `send_html(subject, html, recipients, account_cfg, cc_addrs=None)` | 主题/HTML/收件人/账号 | 无（发一封 HTML 邮件，失败抛异常） |

## 来源与替代（🟡 原为多份副本）

| 本模块 | 抽自 | 迁移状态 |
|---|---|---|
| imap_client / mime_parse / checkpoint | `oa/read_email.py`（与 `report/read_email.py` 逐字相同） | 未迁移，两条线仍各保留一份 |
| smtp_client.get_smtp_oauth2_token | `oa/read_email.py` | 未迁移 |
| smtp_client.send_smtp / send_html | `report/submission_mailer.py`（与 `report_server._send_smtp` 同逻辑） | 未迁移 |

差异说明：`config.get_account_config` 缺账号时抛 KeyError（原 read_email 版是 sys.exit，库不宜退进程）；其余逻辑与源一致。
