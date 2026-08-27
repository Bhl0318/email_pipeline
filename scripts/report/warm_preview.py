#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""热生成 US 递交三件预览（确认函 / Assignment / Declaration）。

定时扫 submission_tasks 里待审案件（task_type='filing_confirmation'，status ∈ pending/skipped），
逐案检查 output/submission/{task_id}/preview/ 下三件成品，**缺哪件就现生成哪件**（热生成），
使审核员打开确认函页时文件已就绪、直接展示（配套 report_server 的 preview-existing 接口）。

与 report_server 的 /preview 用**同一套生成器 + 同一输出目录/文件名**，产物可被 preview-existing
直接认到。**只生成缺失的，不覆盖已存在的**（内容更新交由页面「刷新预览」）。用 DB 里的 fields_json
生成（无页面编辑）。

用法：
  python3 warm_preview.py             # 单次
  python3 warm_preview.py --loop      # 常驻，默认每 300s
  python3 warm_preview.py --loop 600  # 常驻，600s

⚠ 需与 report_server **同机**运行（docx→PDF 依赖 LibreOffice）；连真实库、写文件，非只读。
"""
import sys
import os
import json
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent                                  # 与 report_server 同源
SUBMISSION_OUTPUT_DIR = ROOT / "output" / "submission"    # 与 report_server 同一输出根

sys.path.insert(0, str(SCRIPT_DIR))
from db_query import execute_params                                    # noqa: E402
from submission.common import infer_subject_matter, normalize_parents  # noqa: E402
from submission.confirmation_sheet import generate_confirmation_sheet  # noqa: E402
from submission.assignment_generator import generate_assignments       # noqa: E402
from submission.declaration_generator import generate_declarations     # noqa: E402
from submission.preview import docx_to_pdf                             # noqa: E402

# 预热的任务状态（业务确认 2026-08-27：待审 pending + 跳过 skipped 都预热）
WARM_STATUSES = ("pending", "skipped")
# 三件文档 target → 已存在判定用的文件名 token（与 report_server preview-existing 完全一致）
TOKENS = {"confirmation": "Application Information Sheet",
          "assignment": "Assignment", "declaration": "Declaration"}
TARGETS = ("confirmation", "assignment", "declaration")


def _has_existing(preview_dir, target):
    """preview_dir 里是否已有该 target 的 PDF 成品（按 token 匹配，与 preview-existing 同口径）。"""
    if not preview_dir.is_dir():
        return False
    token = TOKENS[target].lower()
    return any(token in p.name.lower() for p in preview_dir.glob("*.pdf"))


def _gen_confirmation(fields, preview_dir):
    r = generate_confirmation_sheet(fields, preview_dir)
    docx_to_pdf(r["file_path"], preview_dir)


def _gen_assignment(fields, preview_dir):
    for it in generate_assignments(fields, preview_dir):   # 可能多段转让 → 多份
        docx_to_pdf(it["file_path"], preview_dir)


def _gen_declaration(fields, preview_dir):
    generate_declarations(fields, preview_dir)             # 直接产 PDF（无 docx）


_GEN = {"confirmation": _gen_confirmation,
        "assignment": _gen_assignment,
        "declaration": _gen_declaration}


def _applicable(target, fields):
    """该案是否适用生成此件：Assignment 需有转让安排、Declaration 需有发明人；确认函恒适用。
    不适用则直接跳过、不生成也不算失败（否则每轮都会对无转让/无发明人的案件报错重试）。"""
    if target == "assignment":
        return bool(fields.get("assignments"))
    if target == "declaration":
        return bool(fields.get("inventors"))
    return True


def warm_task(task_id, fields):
    """检查并生成该案缺失的三件预览。已存在/不适用跳过、缺失现生成。best-effort：单件失败不影响其余。
    :return: (made, skipped, failed) 三个列表。"""
    fields = dict(fields or {})
    # 与 /preview 一致的预处理（推断 subject_matter、规范母案）
    fields["subject_matter"] = infer_subject_matter(fields)
    normalize_parents(fields)
    preview_dir = SUBMISSION_OUTPUT_DIR / task_id / "preview"
    made, skipped, failed = [], [], []
    for target in TARGETS:
        if _has_existing(preview_dir, target):
            skipped.append(target)
            continue
        if not _applicable(target, fields):
            skipped.append(target)   # 无转让安排→Assignment / 无发明人→Declaration：直接跳过
            continue
        try:
            preview_dir.mkdir(parents=True, exist_ok=True)
            _GEN[target](fields, preview_dir)
            made.append(target)
        except Exception as exc:   # noqa: BLE001（无转让安排/无发明人等 → 跳过该件，下轮再试）
            failed.append(f"{target}({type(exc).__name__}: {exc})")
    return made, skipped, failed


def run_once():
    """扫一轮：预热所有待审案件缺失的三件预览。"""
    try:
        rows = execute_params(
            "SELECT id, case_volume, fields_json FROM submission_tasks "
            "WHERE task_type='filing_confirmation' AND status IN (%s, %s) "
            "ORDER BY updated_at DESC",
            WARM_STATUSES) or []
    except Exception as exc:   # noqa: BLE001
        print(f"[warm-preview] 查库失败：{exc}", file=sys.stderr)
        return
    print(f"[warm-preview] 待审案件 {len(rows)} 个（status ∈ {WARM_STATUSES}）")
    n_made = n_skip = n_fail = 0
    for r in rows:
        tid = r["id"]
        cv = r.get("case_volume") or tid
        try:
            fields = json.loads(r.get("fields_json") or "{}")
        except Exception as exc:   # noqa: BLE001
            print(f"  [{cv}] fields_json 解析失败，跳过：{exc}", file=sys.stderr)
            continue
        made, skipped, failed = warm_task(tid, fields)
        n_made += len(made); n_skip += len(skipped); n_fail += len(failed)
        if made or failed:   # 全跳过（已就绪）的不刷屏
            print(f"  [{cv}] 生成={made or '-'} 已存在={skipped or '-'} 失败={failed or '-'}")
    print(f"[warm-preview] 本轮：生成 {n_made} 件，已存在跳过 {n_skip} 件，失败 {n_fail} 件")


def run_loop(interval):
    """常驻轮询：每 interval 秒扫一轮。单轮异常不退整体，continue 下一轮。Ctrl+C 退出。"""
    print(f"[warm-preview] 轮询启动：每 {interval}s 预热一次待审案件的三件预览（Ctrl+C 退出）")
    while True:
        try:
            run_once()
        except KeyboardInterrupt:
            print("\n[warm-preview] 收到中断，退出。")
            return
        except Exception as exc:   # noqa: BLE001
            print(f"[warm-preview] 本轮异常（忽略，继续下一轮）：{exc}", file=sys.stderr)
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[warm-preview] 收到中断，退出。")
            return


def _parse_interval(argv, default=300):
    """--loop 后紧跟秒数（默认 300=5min，下限 5s）；无 --loop 返回 (False, default)。"""
    if "--loop" not in argv:
        return False, default
    i = argv.index("--loop")
    if i + 1 < len(argv):
        try:
            return True, max(5, int(argv[i + 1]))
        except ValueError:
            pass
    return True, default


if __name__ == "__main__":
    _loop, _interval = _parse_interval(sys.argv)
    if _loop:
        run_loop(_interval)
    else:
        run_once()
