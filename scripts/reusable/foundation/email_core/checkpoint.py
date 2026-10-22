"""邮件增量去重断点（可复用，仅标准库）。

抽自 oa/read_email.py 的 load/save/get/update_checkpoint + filter_new_emails，逻辑不变。
以 `account:folder` 为键，把已处理 Message-ID + last_time 存 JSON，实现增量拉取与去重
（超过 2000 条时清理最早的 1000 条 ID，并记录原始主题）。零业务耦合。

断点文件路径默认 email_core/checkpoint.json，可用 set_checkpoint_path() 覆盖。
"""
import json
import os
import sys
from datetime import datetime

_CHECKPOINT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "checkpoint.json")


def set_checkpoint_path(path):
    """覆盖断点文件路径（默认 email_core/checkpoint.json）。"""
    global _CHECKPOINT_PATH
    _CHECKPOINT_PATH = path


def load_checkpoint():
    """加载断点记录 dict（文件不存在返回 {}）。"""
    if os.path.exists(_CHECKPOINT_PATH):
        with open(_CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_checkpoint(data):
    """写回断点记录 dict。"""
    with open(_CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_checkpoint(account, folder):
    """取某 account+folder 的断点信息 dict。"""
    cp = load_checkpoint()
    return cp.get(f"{account}:{folder}", {})


def update_checkpoint(account, folder, emails):
    """处理完成后更新断点：记录最新 date、已处理 Message-ID 与原始主题。

    输入：account(str)、folder(str)、emails(list[dict]，含 message_id/date/subject)
    输出：无（副作用：写断点文件）
    """
    if not emails:
        return
    cp = load_checkpoint()
    key = f"{account}:{folder}"
    existing = cp.get(key, {})
    old_ids = existing.get("processed_ids", [])

    new_ids = []
    new_subjects = {}
    latest_time = existing.get("last_time", "")
    for em in emails:
        msg_id = em.get("message_id", "")
        if msg_id:
            new_ids.append(msg_id)
            if em.get("subject"):
                new_subjects[msg_id] = em["subject"]
        em_date = em.get("date", "")
        if em_date > latest_time:
            latest_time = em_date

    refreshed = set(new_ids)
    all_ids = list(dict.fromkeys(msg_id for msg_id in old_ids if msg_id not in refreshed))
    all_ids.extend(dict.fromkeys(reversed(new_ids)))
    if len(all_ids) > 2000:
        all_ids = all_ids[1000:]
    old_subjects = existing.get("processed_subjects") or {}
    subjects = {msg_id: new_subjects.get(msg_id) or old_subjects.get(msg_id, "")
                for msg_id in all_ids}

    cp[key] = {
        "last_time": latest_time,
        "updated_at": datetime.now().isoformat(),
        "processed_ids": all_ids,
        "processed_subjects": subjects,
    }
    save_checkpoint(cp)
    print(f"断点已更新: {key} | 最新时间: {latest_time} | 已记录 {len(all_ids)} 条 ID", file=sys.stderr)


def filter_new_emails(emails, account, folder):
    """过滤掉已处理过的邮件，返回新邮件列表（按 message_id 比对断点）。

    输入：emails(list[dict])、account、folder
    输出：list[dict]（去掉 message_id 命中断点的）
    """
    processed_ids = set(get_checkpoint(account, folder).get("processed_ids", []))
    if not processed_ids:
        return emails

    new_emails = []
    duplicates = 0
    for em in emails:
        msg_id = em.get("message_id", "")
        if msg_id and msg_id in processed_ids:
            duplicates += 1
            continue
        new_emails.append(em)
    if duplicates:
        print(f"跳过 {duplicates} 封已处理邮件", file=sys.stderr)
    return new_emails
