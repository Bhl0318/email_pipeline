#!/usr/bin/env python3
"""按 id 把已选人员(submit_json)补写到 Wiki 新增OA 人员分配格（独立脚本）。

用途：分配/分享时 Wiki 回写是 best-effort，偶发静默失败（前端仍显示成功）。
本脚本按 id 重新回写：读 oa_assign_report.submit_json（与 oa_assign_task 同一 id=projects.id）
里的 责任人/QC/AQC/附言/原因，调用 oainfo_cli.write_oa_assignment 写回 Wiki，并**打印明确结果**
（成功 / 未找到行 / HTTP 失败），便于定位为何之前没写进去。

用法：
  python3 rewrite_wiki_assignment.py <id> [<id> ...]
  python3 rewrite_wiki_assignment.py --from-json reassign_oaids.json      # 值为 id 的 {案号:id} 映射
  python3 rewrite_wiki_assignment.py <id> --dry-run                       # 只打印将写什么，不动 Wiki

说明：
  * 只写 Wiki 人员分配格（含分配人/分配时间/分配人历史页），不改 projects/绩效/待分配状态。
  * write_oa_assignment 按 oa_id + 案号比对定位行；定位不到会返回明确 msg（class 被洗掉 / 案号对不上）。
  * 会真实改 Wiki 页面，请在受控环境运行。
"""
import os
import sys
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def _ids_from_json(path):
    """读 JSON → id 列表。支持 {案号: id} 映射（取值）或 ["id", ...] 列表。"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return [str(v).strip() for v in data.values() if str(v or "").strip()]
    if isinstance(data, list):
        return [str(v).strip() for v in data if str(v or "").strip()]
    return []


def rewrite_one(oa_id, dry_run=False):
    """读该 id 的 submit_json → 回写 Wiki。返回 (ok, msg)。"""
    from oa_assign_store import get_report
    from oainfo_cli import write_oa_assignment, format_oa_person
    rep = None
    try:
        rep = get_report(oa_id)
    except Exception as e:
        return False, f"读 submit_json 失败: {e}"
    submit = (rep or {}).get("submit") or {}
    responder = (submit.get("responder") or "").strip()
    qc = (submit.get("qc") or "").strip()
    aqc = (submit.get("aqc") or "").strip()
    postscript = (submit.get("postscript") or "").strip()
    reason = (submit.get("reason") or "").strip()      # submit_json 里叫 reason（=分配原因/custom_note）
    if not (responder or qc):
        return False, "submit_json 无人员（responder/qc 均空），跳过"
    text = format_oa_person(responder, qc, aqc)
    if dry_run:
        return True, f"[dry-run] 将写：{text}" + (f"（附言：{postscript}）" if postscript else "")
    try:
        r = write_oa_assignment(oa_id, responder, qc,
                                postscript=postscript, custom_note=reason, aqc=aqc)
        return (r.get("code") == 0), r.get("msg", "")
    except Exception as e:
        return False, f"write_oa_assignment 异常: {e}"


def main():
    ap = argparse.ArgumentParser(description="按 id 把 submit_json 已选人员补写到 Wiki 人员分配格")
    ap.add_argument("ids", nargs="*", help="oa_id（=oa_assign_task.id=projects.id），可多个")
    ap.add_argument("--from-json", default="", help="从 JSON 取 id（{案号:id} 映射取值，或 id 列表）")
    ap.add_argument("--dry-run", action="store_true", help="只打印将写什么，不改 Wiki")
    args = ap.parse_args()

    ids = list(args.ids)
    if args.from_json:
        ids = _ids_from_json(args.from_json) + ids
    # 去重保序
    seen, uniq = set(), []
    for i in ids:
        i = (i or "").strip()
        if i and i not in seen:
            seen.add(i); uniq.append(i)
    if not uniq:
        ap.error("需给出 id，或用 --from-json 指定 JSON")

    ok_n = 0
    for oa_id in uniq:
        ok, msg = rewrite_one(oa_id, dry_run=args.dry_run)
        ok_n += 1 if ok else 0
        print(f"[{'OK' if ok else '×'}] {oa_id}: {msg}", file=sys.stderr)
    print(f"\n完成：{ok_n}/{len(uniq)} 成功"
          + ("（dry-run，未改 Wiki）" if args.dry_run else ""), file=sys.stderr)


if __name__ == "__main__":
    main()
