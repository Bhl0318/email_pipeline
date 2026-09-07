"""wiki —— Confluence 读写客户端（基础通用层 · 网络与服务调用）。

WikiClient：搜页 / 读页(按标题或ID) / 建子页 / 更新页 / 传附件。
base_url 与账号走 参数 > 环境变量 > email_config.json 的 wiki 段。
"""
from .client import WikiClient

__all__ = ["WikiClient"]
