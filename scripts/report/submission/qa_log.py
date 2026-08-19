"""QA 操作留痕 JSONL 日志：修改痕迹 + 操作时长（+ 埋点结果，后续接）。

每次「确认发送 / 发美代理」追加一条 JSONL。append-only、best-effort（写失败只记 stderr、不抛，
绝不影响正常发送流程）。日志路径缺省 <report_dir>/logs/qa_seed.jsonl，可配
email_config.json 的 submission.qa_log_path。
"""
import os
import sys
import json
import datetime

_REPORT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # submission 的上一级 = report 目录


def _log_path():
    try:
        with open(os.path.join(_REPORT_DIR, "email_config.json"), encoding="utf-8") as f:
            p = (json.load(f).get("submission") or {}).get("qa_log_path")
            if p:
                return p
    except Exception:
        pass
    return os.path.join(_REPORT_DIR, "logs", "qa_seed.jsonl")


def append(record: dict):
    """追加一条记录（自动加 ts）。best-effort。"""
    try:
        rec = {"ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **(record or {})}
        p = _log_path()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:  # noqa: BLE001
        print(f"[qa_log] 写日志失败(忽略): {e}", file=sys.stderr)


def build_op_record(stage, case_volume, reviewer, qa, seeds=None):
    """组装留痕记录：stage(confirmation/filing) + 案号 + 责任人邮箱 + 前端来的 qa(opened_at/duration_sec/changed)。
    对前端来的 changed 做长度/结构裁剪，防超大或怪结构。seeds 供 env2 埋点结果(后续接)。"""
    qa = qa or {}
    raw = qa.get("changed") or []
    changed = [{"path": str(c.get("path", ""))[:200],
                "old": str(c.get("old", ""))[:500],
                "new": str(c.get("new", ""))[:500]}
               for c in raw if isinstance(c, dict)][:200]
    rec = {
        "stage": stage,
        "case": case_volume,
        "reviewer": reviewer or "",
        "opened_at": str(qa.get("opened_at") or "")[:32],
        "duration_sec": qa.get("duration_sec"),
        "changed": changed,
        "changed_count": len(changed),
    }
    if seeds is not None:
        rec["seeds"] = seeds
    return rec
