"""账号配置读取（可复用）。

从 email_config.json 读账号 dict，供 imap_client/smtp_client 使用。
与原 read_email.get_account_config 的差异：缺账号时抛 KeyError（库不应 sys.exit）。
"""
import json


def load_config(path):
    """读 email_config.json 全量 dict。输入路径 → 输出 dict。"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_account_config(cfg, account_name):
    """从已加载 config（或配置文件路径）取某账号 dict。

    输入：cfg(dict 或 str 路径)、account_name
    输出：account dict；账号不存在抛 KeyError。
    """
    if isinstance(cfg, str):
        cfg = load_config(cfg)
    accounts = cfg.get("accounts", {})
    if account_name not in accounts:
        raise KeyError(f"账号 '{account_name}' 不存在。可用账号: {', '.join(accounts.keys())}")
    return accounts[account_name]
