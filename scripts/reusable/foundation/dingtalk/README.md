# dingtalk —— 钉钉收发消息（接口说明）

**做什么用**：通过钉钉机器人收发消息——主动给某人推送文本消息（OTO）、以及用 Stream Mode（WebSocket）直接收用户回复机器人的内容（无需公网回调，常用于收验证码/审批回复）。应用凭据走配置，不写死。

抽自 `sendInfobyDing.py`（发）与 `patent_center_ui.py` 的 `_otp`（收）；发消息逻辑不变，收消息把"提取验证码"泛化成 matcher。依赖：alibabacloud_dingtalk SDK（发）、dingtalk-stream（收）——都惰性导入，未装也能 import 本模块。

可运行示例：`python3 scripts/reusable/examples/dingtalk_demo.py`。

## 如何 import + 配置

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/foundation")
from dingtalk import send_message, wait_for_reply
```

凭据优先级：参数 > 环境变量 `DINGTALK_CLIENT_ID`/`DINGTALK_CLIENT_SECRET`/`DINGTALK_ROBOT_CODE` > `scripts/email_config.json` 的 `dingtalk` 段。

## 接口

### 发消息（`send.py`）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `send_message(name, content, client_id=None, client_secret=None, robot_code=None)` | 按姓名给某人发文本（一站式：换 token→查 userId→发） | name 姓名；content 文本；凭据可选 | API 响应；取不到 token/userId→None |
| `get_access_token(client_id=None, client_secret=None)` | 用应用凭据换 access_token | 凭据可选 | token str｜None |
| `get_users(access_token)` | 列通讯录 | access_token | dict `{姓名: userId}`（翻页取全） |
| `send_to_user(robot_code, access_token, user_id, content)` | 给指定 userId 发文本 | robot_code；token；user_id；content | API 响应 |

### 收消息（`receive.py`）

| 函数 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `wait_for_reply(matcher, timeout=300, client_id=None, client_secret=None)` | 启动机器人 Stream，等用户回复，返回第一条被 matcher 命中的结果 | matcher: callable(text)->结果｜None；timeout（可选，默认 300 秒）；凭据可选 | matcher 命中的结果；超时/未装 SDK/失败→None |

## 使用示例

```python
import re
from dingtalk import send_message, wait_for_reply

# 发消息（凭据走配置）
send_message("毕海灵", "当前进展：环节3 已完成")

# 收消息：发提示 → 等对方回复机器人 → 提取验证码（matcher 由你定）
def otp_matcher(text):
    d = re.sub(r"\D", "", text or "")
    return d if len(d) >= 4 else None

send_message("毕海灵", "请回复 USPTO 验证码")
code = wait_for_reply(otp_matcher, timeout=300)   # 收到含≥4位数字的回复即返回，超时→None
```

## 来源与改动

- 抽自：`sendInfobyDing.py`（get_access_token/getAllinfos/send_to_user/DingTalkMessageSender）、`patent_center_ui.py` 的 `_otp`（Stream 收码）。
- 改动：应用凭据由硬编码改走 参数/环境变量/配置；收消息从"专收 OTP"泛化为"matcher 命中即返回"，发提示与终端回退留给调用方组合。逻辑不变。
