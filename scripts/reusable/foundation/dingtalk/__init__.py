"""dingtalk —— 钉钉收发消息（基础通用层 · 网络与服务调用）。

- send    发消息：get_access_token / get_users / send_to_user / send_message(按姓名一站式)
- receive 收消息：wait_for_reply(用机器人 Stream Mode 收用户回复，matcher 命中即返回)
凭据走 参数 > 环境变量 > email_config.json 的 dingtalk 段。
"""
from .send import (get_access_token, get_users, send_to_user, send_message, resolve_creds)
from .receive import wait_for_reply

__all__ = ["get_access_token", "get_users", "send_to_user", "send_message",
           "resolve_creds", "wait_for_reply"]
