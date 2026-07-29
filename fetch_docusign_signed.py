#!/usr/bin/env python3
"""环节6（DocuSign 线）：用 envelope_id 经 DocuSign API 取回签署版，落到案号目录并销账。

与 `fetch_uspto_upload_attachments.py`（Outlook 线）**并列、解耦**：两者各自定时跑、
互不依赖，把签署版都落到**同一个案号目录** `uspto_upload/{案号}/`；销账函数
`_settle_agent_followup` 扫该目录里现有全部文件比对，谁把最后一件补齐谁把该案置 done。

做的事：
  1. 查 atw.submission_tasks 里未 done 且带 envelope_id 的 agent_followup（环节5 发美代理时插）；
  2. 对每个信封 `get_status`：`completed` 才 `download_signed(which='separate')` 把**逐份**签署版
     PDF 下到 `uspto_upload/{案号}/`（文件名含原件名 → 与发出清单 %原名% 子串匹配）；
     未完成(sent/delivered)跳过留待下次；declined/voided 打警告待人工；
  3. 调 `_settle_agent_followup` 销账（扫目录比对，全齐→done，否则 received）。

用法：
  python3 fetch_docusign_signed.py            # 扫所有未 done 且有 envelope_id 的 agent_followup

⚠️ 连真实 DocuSign + 写库（agent_followup 可能置 done），非只读；请在受控环境运行。
best-effort：无 pymysql / 无 DocuSign 配置 / 连不上都跳过，不影响另一条线。
"""
import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ROOT = os.path.join(SCRIPT_DIR, "uspto_upload")

# 复用 Outlook 线的销账（扫目录比对）与 DB 句柄，避免重复实现、保证两线一致。
sys.path.insert(0, SCRIPT_DIR)
from fetch_uspto_upload_attachments import _settle_agent_followup, _db_exec, _SETTLE_OK

# DocuSign 客户端（get_status / download_signed / load_config / get_access_token）
try:
    sys.path.insert(0, os.path.join(SCRIPT_DIR, "scripts", "report"))
    from submission import docusign_client as _ds
    _DS_OK = True
except Exception as exc:  # noqa: BLE001
    print(f"[docusign-fetch] 无法加载 docusign_client：{exc}", file=sys.stderr)
    _DS_OK = False


def _envelope_id_of(fields_json):
    try:
        return (json.loads(fields_json or "{}") or {}).get("envelope_id")
    except Exception:
        return None


def fetch():
    if not _DS_OK:
        print("[docusign-fetch] DocuSign 客户端不可用，跳过。")
        return
    if not _SETTLE_OK:
        print("[docusign-fetch] DB(db_query) 不可用，无法查 agent_followup，跳过。")
        return

    rows = _db_exec(
        "SELECT id, case_volume, fields_json, status FROM submission_tasks "
        "WHERE task_type='agent_followup' AND status <> 'done'") or []
    targets = [(r, _envelope_id_of(r.get("fields_json"))) for r in rows]
    targets = [(r, eid) for r, eid in targets if eid]
    print(f"待取回签署版的 agent_followup：{len(targets)} 个（未 done 且有 envelope_id）")
    if not targets:
        return

    cfg = _ds.load_config()
    auth = _ds.get_access_token(cfg)

    for row, eid in targets:
        case = row["case_volume"]
        try:
            status = _ds.get_status(cfg, auth, eid)
        except Exception as exc:  # noqa: BLE001
            print(f"  {case}: 查信封状态失败 envelope={eid}：{exc}")
            continue
        if status != "completed":
            note = "，需人工（拒签/作废）" if status in ("declined", "voided") else "，留待下次"
            print(f"  {case}: 信封 {status}{note}（envelope={eid}）")
            continue
        case_dir = os.path.join(OUTPUT_ROOT, case)
        os.makedirs(case_dir, exist_ok=True)
        try:
            saved = _ds.download_signed(cfg, auth, eid, case_dir, which="separate")
        except Exception as exc:  # noqa: BLE001
            print(f"  {case}: 下载签署版失败 envelope={eid}：{exc}")
            continue
        names = [os.path.basename(p) for p in saved]
        print(f"  {case}: 信封 completed，取回 {len(names)} 份 → {case_dir}")
        note = _settle_agent_followup(case, case_dir, names)
        print(f"    销账：{note}")


if __name__ == "__main__":
    fetch()
