#!/usr/bin/env python3
"""预热 OA 分配报告 —— 扫待分配案件，提前把 AI 报告(md)+方案(schemes)生成并写入 oa_assign_report。

分配页原本"首次打开才现算"(DeepSeek 慢)。本脚本后台提前生成，分配页打开即命中缓存、秒开。
只处理"待分配表里、oa_assign_report 里还没有报告"的案子（--force 则全部重生成）。
建议定时运行（如每 10 分钟；与 main.py 类似）。有副作用(写库/调 DeepSeek)，请在受控环境跑。

用法：
  python3 prewarm_oa_reports.py               # 只补没有报告的
  python3 prewarm_oa_reports.py --force        # 全部重生成
  python3 prewarm_oa_reports.py --limit 5      # 本轮最多处理 5 件
  python3 prewarm_oa_reports.py --interval 10  # 每 10 分钟循环一次
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _derive_region(project):
    p = (project or "").upper()
    for r in ("US", "EP", "CN", "WO", "JP", "KR"):
        if r in p:
            return r
    return ""


def _row_to_item(row):
    proj = row.get("case_volume", "") or ""
    return {"project": proj, "project_name": row.get("project_name", ""),
            "customer": row.get("customer", ""), "region": _derive_region(proj),
            "deadline": row.get("project_deadline", "")}


def prewarm_once(force=False, limit=0):
    import oa_assign_store as store
    from oa_report_ai import build_case_report
    try:
        from oa_schemes import build_assignment_schemes, render_schemes_md
    except Exception:
        build_assignment_schemes = None
        render_schemes_md = None

    rows = store.list_pending()
    todo = []
    for r in rows:
        cid = r.get("id")
        if not cid:
            continue
        if not force:
            rep = store.get_report(cid)
            if rep and (rep.get("report_md") or "").strip():
                continue   # 已有报告，跳过
        todo.append(r)
    if limit and limit > 0:
        todo = todo[:limit]

    print(f"[预热] 待分配 {len(rows)} 件，需生成 {len(todo)} 件"
          + ("（--force 全量）" if force else "（补缺）"), file=sys.stderr)
    done = 0
    for r in todo:
        cid = r.get("id")
        item = _row_to_item(r)
        proj = item["project"]
        try:
            md = build_case_report(item)
            schemes = []
            if build_assignment_schemes:
                try:
                    schemes = build_assignment_schemes(proj, region=item["region"], report_md=md)
                    if render_schemes_md:
                        sec = render_schemes_md(schemes)
                        if sec:
                            md = md.rstrip() + "\n\n" + sec
                except Exception as e:
                    print(f"[预热] {proj} 方案生成失败: {e}", file=sys.stderr)
            store.save_report(cid, md, schemes)
            done += 1
            print(f"[预热] {proj} 已生成并落库 ({done}/{len(todo)})", file=sys.stderr)
        except Exception as e:
            print(f"[预热] {proj} 生成失败: {e}", file=sys.stderr)
    print(f"[预热] 完成：{done}/{len(todo)}", file=sys.stderr)
    return done


def main():
    ap = argparse.ArgumentParser(description="预热 OA 分配报告到 oa_assign_report")
    ap.add_argument("--force", action="store_true", help="全部重生成（含已有报告的）")
    ap.add_argument("--limit", type=int, default=0, help="本轮最多处理件数（0=不限）")
    ap.add_argument("--interval", type=int, default=0, metavar="MIN", help="循环间隔分钟（0=只跑一次）")
    args = ap.parse_args()
    if args.interval and args.interval > 0:
        print(f"[预热] 循环模式：每 {args.interval} 分钟一次（Ctrl+C 退出）", file=sys.stderr)
        while True:
            try:
                prewarm_once(force=args.force, limit=args.limit)
            except Exception as e:
                print(f"[预热] 本轮异常，继续: {e}", file=sys.stderr)
            time.sleep(args.interval * 60)
    else:
        prewarm_once(force=args.force, limit=args.limit)


if __name__ == "__main__":
    main()
