# email_core —— 邮件收发核心（接口说明）

**做什么用**：收发和解析邮件——登录 IMAP 收信、把邮件解析成结构化数据、按已处理记录增量去重、用 SMTP 发信。账号信息由调用方传入，不绑死配置文件。依赖：标准库 + `requests`。从现有业务文件抽出，逻辑不变。

可运行示例：`python3 scripts/reusable/examples/email_core_demo.py`。

## 如何 import

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/foundation")
from email_core import config, read_emails, move_emails, send_html, parse_message
from email_core.checkpoint import update_checkpoint
acc = config.get_account_config("scripts/email_config.json", "docketing")
```

`account_cfg` 结构（同 email_config.json 的 accounts.<name>）：`imap_host/imap_port`（收）或 `smtp_host/smtp_port`（发）、`user/password`，可选 `oauth2:{enabled,token_url,client_id,client_secret,resource}`、`imap_timeout`。

## 逐函数：作用 / 输入 / 返回

### config（`config.py`）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `load_config(path)` | 读 email_config.json 全部内容 | path: str | dict |
| `get_account_config(cfg, account_name)` | 从配置里取某个账号的信息 | cfg: dict 或路径 str；account_name: str | account dict；账号不存在抛 KeyError |

### imap_client（`imap_client.py`，收信）

| 函数 | 作用 | 输入 | 返回 / 副作用 |
|---|---|---|---|
| `get_oauth2_token(account_cfg)` | 用账号换 OAuth2 令牌 | account_cfg: dict | token str；未启用/失败→None |
| `login_imap(account_cfg)` | 登录 IMAP（OAuth2 优先，失败降级密码） | account_cfg: dict | 已登录 IMAP4_SSL |
| `list_folders(account_cfg)` | 列出邮箱所有文件夹 | account_cfg: dict | 无（打印） |
| `read_emails(account_cfg, folder="INBOX", since=None, before=None, count=50, attachment_dir=None, account_name=None)` | 读某文件夹邮件，返回结构化列表 | account_cfg；folder（可选，默认 INBOX）；since/before（可选，datetime）；count（可选，默认 50）；attachment_dir（可选，传了落盘附件）；account_name（可选，传了走断点增量） | list[dict]（从新到旧）；只读打开不改邮箱 |
| `move_emails(account_cfg, folder, message_ids, target_folder="TEST_AUTO")` | 按 Message-ID 把邮件移到另一文件夹（归档） | account_cfg；folder；message_ids: list[str]；target_folder（可选，默认 TEST_AUTO） | int（移动条数）；**copy+删除，不可逆** |

### mime_parse（`mime_parse.py`，解析）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `parse_message(msg, attachment_dir=None)` | 把一封邮件一站式解析成结构化 dict | msg: email.message.Message；attachment_dir（可选，传了落盘附件） | dict：subject/from/to/cc/date/message_id/body/html_body/attachments |
| `decode_str(s)` | 解码邮件头（主题/发件人等乱码） | s: str｜None | str；None→`""` |
| `html_to_text(html)` | 把 HTML 正文转纯文本（剥 style/script） | html: str | str |
| `get_body(msg)` | 取邮件正文 | msg | (纯文本 str, html str) |
| `get_attachments(msg)` | 列出附件信息（不落盘） | msg | list[{filename,content_type,size}] |
| `save_attachments(msg, output_dir)` | 把附件存到磁盘 | msg；output_dir: str | list[str]（落盘路径） |
| `parse_email_date(msg)` | 把邮件日期头转 ISO 字符串 | msg | str |
| `parse_address_list(header_value)` | 把收件人/抄送头拆成地址列表 | header_value: str｜None | list[str] |

### checkpoint（`checkpoint.py`，增量去重）

| 函数 | 作用 | 输入 | 返回 / 副作用 |
|---|---|---|---|
| `set_checkpoint_path(path)` | 指定断点文件位置 | path: str | 无 |
| `filter_new_emails(emails, account, folder)` | 过滤掉已处理过的，只留新邮件 | emails: list[dict]；account；folder | list[dict] |
| `update_checkpoint(account, folder, emails)` | 处理完后记录已处理的邮件 | account；folder；emails: list[dict] | 无（写断点，最多留 2000 条 ID） |
| `get_checkpoint(account, folder)` | 读某账号+文件夹的断点 | account；folder | dict |
| `load_checkpoint()` / `save_checkpoint(data)` | 读 / 写整个断点文件 | 无 / dict | dict / 无 |

### smtp_client（`smtp_client.py`，发信）

| 函数 | 作用 | 输入 | 返回 / 副作用 |
|---|---|---|---|
| `send_html(subject, html, recipients, account_cfg, cc_addrs=None)` | 发一封 HTML 邮件（便捷封装） | subject；html；recipients: list[str]；account_cfg；cc_addrs（可选） | 无（发信，失败抛异常） |
| `send_smtp(msg, account_cfg, recipients, cc_addrs=None)` | 发送已构造好的邮件对象 | msg: MIMEMultipart；account_cfg；recipients；cc_addrs（可选） | 无（发信，失败抛异常；会重写 From/To/Cc） |
| `get_smtp_oauth2_token(account_cfg)` | 换 SMTP 用的 OAuth2 令牌 | account_cfg: dict | token str；未启用/失败→None |

## 使用示例

### 端到端：读邮件 → 记断点 → 归档 → 发信

```python
from email_core import config, read_emails, move_emails, send_html
from email_core.checkpoint import update_checkpoint

acc = config.get_account_config("scripts/email_config.json", "docketing")
mails = read_emails(acc, folder="INBOX", count=10, account_name="docketing")  # 只取新邮件
for m in mails:
    print(m["subject"], m["from"], len(m["attachments"]))
update_checkpoint("docketing", "INBOX", mails)
move_emails(acc, "INBOX", [m["message_id"] for m in mails], target_folder="TEST_AUTO")

pa = config.get_account_config("scripts/email_config.json", "pa")
send_html("主题", "<b>正文</b>", ["to@x.com"], pa, cc_addrs=["cc@x.com"])
```

### 只解析一封原始邮件（离线）

```python
import email
from email_core import parse_message
d = parse_message(email.message_from_bytes(raw_bytes))
# d == {'subject':'测试邮件','from':'张三 <zhang@example.com>','to':[...],'cc':[...],
#       'date':'2026-02-02T10:00:00+08:00','message_id':'<abc123@example.com>',
#       'body':'正文第一行。','html_body':'','attachments':[]}
```

## 来源与差异

| 本模块 | 抽自 |
|---|---|
| imap_client / mime_parse / checkpoint / get_smtp_oauth2_token | `oa/read_email.py`（与 `report/read_email.py` 逐字相同） |
| smtp_client.send_smtp / send_html | `report/submission_mailer.py` |

差异：`get_account_config` 缺账号时抛 KeyError（原 read_email 版是 sys.exit，库不宜退进程）；其余逻辑与源一致。
