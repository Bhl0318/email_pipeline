#!/usr/bin/env python3
"""独立诊断：给案号，打印 AI 人员分配的推荐组合 + 诊断信息，排查"为什么没首推某组合"。

打印四段：
  1) 档位（_grade：5/6→普及、US/EP→海外、CN→标准）
  2) 候选人库（collect_candidates：本案撰写/本案历史OA/同族OA 承办人；含在职状态）
  3) 该档位白名单（oa_assign_whitelist：biz=OA实质 × 档位，按领域/梯队）
  4) AI 推荐组合（build_assignment_schemes）

用法：
  python3 diag_schemes.py <案号> [region] [报告md文件]
  # region 省略则按案号推；报告 md 省略则尝试 build_case_report 生成（判技术领域用）
在能连 atw(MySQL) + DeepSeek 的机器上运行。
"""
import sys
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)


def _print_candidates(project):
    print("【候选人库 collect_candidates】（连续性来源 + 在职状态）")
    try:
        from oa_personnel import collect_candidates
        cands = collect_candidates(project)
    except Exception as e:
        print(f"  查候选人失败：{e}\n")
        return
    if not cands:
        print("  (空 —— 该案 projects 里没查到本案撰写/历史OA/同族承办人)")
    for c in cands:
        attr = "/".join(x for x in (c.get("duty"), c.get("level")) if x) or "职务职级未知"
        print(f"  - {c['name']}  [{attr}]  {c.get('status') or '在职状态未知'}  "
              f"来源:{'/'.join(c.get('sources', []))}")
    print()


def _print_whitelist(grade):
    print(f"【白名单 oa_assign_whitelist  biz=OA实质 × 档位={grade or '(无)'}】")
    if not grade:
        print("  (无档位，取不到白名单 → 会退回候选池模式)\n")
        return
    try:
        from oa_whitelist_store import list_for
        wl = list_for("OA实质", grade)
    except Exception as e:
        print(f"  查白名单失败：{e}\n")
        return
    if not wl:
        print("  (空 —— 该档位白名单没有人 → 会退回候选池模式)")
    byf = {}
    for w in wl:
        byf.setdefault(w.get("field") or "(未分领域)", []).append(w)
    for fld, ws in byf.items():
        names = "、".join(f"{w['name']}({w.get('tier', '')})"
                          for w in sorted(ws, key=lambda x: x.get("tier_level", 99)))
        print(f"  领域【{fld}】：{names}")
    print()


def main():
    if len(sys.argv) < 2:
        print("用法: python3 diag_schemes.py <案号> [region] [报告md文件]")
        return
    project = sys.argv[1].strip()
    region = ""
    report_md = ""
    for a in sys.argv[2:]:
        if a.endswith(".md") and os.path.exists(a):
            report_md = open(a, encoding="utf-8").read()
        elif a.upper() in ("US", "EP", "CN", "WO", "JP", "KR"):
            region = a.upper()

    from oa_schemes import _grade, build_assignment_schemes
    grade = _grade(project, region)
    print(f"\n=== 案号 {project}  region={region or '(按案号推)'}  档位={grade or '未知'} ===\n")

    _print_candidates(project)
    _print_whitelist(grade)

    # 报告（判技术领域用）：优先入参 md，否则尝试 build_case_report
    if not report_md:
        try:
            from oa_report_ai import build_case_report
            report_md = build_case_report({"project": project, "region": region},
                                          with_personnel=False)
            print("（已用 build_case_report 生成报告供 DeepSeek 判技术领域）\n")
        except Exception as e:
            print(f"（无报告 md，技术领域判定可能不准：{e}）\n")

    print("【AI 推荐组合 build_assignment_schemes】")
    try:
        schemes = build_assignment_schemes(project, region=region, report_md=report_md)
    except Exception as e:
        print(f"  生成失败：{e}")
        return
    if not schemes:
        print("  (无方案 —— DeepSeek 失败/欠费，或无白名单且无候选人)")
    for s in schemes:
        print(f"  {s.get('label', '方案')}：答复负责人 = {s.get('responder') or '—'}   "
              f"QC = {s.get('qc') or '—'}")
        if s.get("note"):
            print(f"       理由：{s['note']}")


if __name__ == "__main__":
    main()
