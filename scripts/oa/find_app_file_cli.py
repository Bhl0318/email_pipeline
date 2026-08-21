#!/usr/bin/env python3
"""按案号解析「最终选中的申请文件」—— 独立测试脚本（NAS 路径规则）。

只做定位、不生成报告；打印每一步：-H 判定 / 客户简称 / 定位目录 / 目录下 docx 清单 / 最终命中文件。
强制走 NAS 模式（MATCH_BY_CASE_NO=True），不受 oa_report_ai 当前测试开关影响。

用法：
  python3 find_app_file_cli.py 20618-1492US00
  python3 find_app_file_cli.py 6C301-H002CS00 --region US
  python3 find_app_file_cli.py 20243-0005CN00 --base "D:\\本地测试根" --zhuohui "D:\\本地测试众慧"

参数：
  案号（必填）
  --region US|CN|EP   不给则按案号自动推（含 US/EP/CN 字样）
  --base    覆盖普通案号 NAS 根（默认 Z:\\）
  --zhuohui 覆盖含 -H 案号根（默认 Z:\\众慧优创知识产权）
"""
import argparse
import glob
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

import oa_report_ai as m  # noqa: E402


def _derive_region(project):
    p = (project or "").upper()
    for r in ("US", "EP", "CN", "WO", "JP", "KR"):
        if r in p:
            return r
    return ""


def main():
    ap = argparse.ArgumentParser(description="按案号解析最终申请文件（NAS 规则，测试用）")
    ap.add_argument("project", help="案号，如 20618-1492US00")
    ap.add_argument("--region", default="", help="US/CN/EP；不给按案号自动推")
    ap.add_argument("--base", default=None, help="覆盖普通案号 NAS 根（默认 Z:\\）")
    ap.add_argument("--zhuohui", default=None, help="覆盖含 -H 案号根")
    args = ap.parse_args()

    project = args.project.strip()
    region = args.region.strip().upper() or _derive_region(project)

    # 强制 NAS 模式；可覆盖根目录用于本地测
    m.MATCH_BY_CASE_NO = True
    if args.base:
        m.NAS_BASE_DIR = args.base
    if args.zhuohui:
        m.NAS_ZHUOHUI_DIR = args.zhuohui

    is_h = "-H" in project
    print(f"案号：{project}")
    print(f"地区：{region or '(推不出)'}")
    print(f"含 -H：{'是 → 走 众慧优创知识产权' if is_h else '否 → 普通客户路径'}")
    if not is_h:
        code = project[:5]
        sn = m._customer_shortname(code)
        toplevel = code in m.NAS_TOPLEVEL_CUSTOMERS
        print(f"客户简称（atw customer_code={code}）：{sn or '(查不到→跳过)'}")
        print(f"客户位置：{'列出客户，在根目录' if toplevel else '其他客户，在 其他客户\\ 下'}")
        print(f"组内号：{project[:10]}")
    print(f"NAS 根：base={m.NAS_BASE_DIR}  zhuohui={m.NAS_ZHUOHUI_DIR}")

    # 定位目录
    d = m._resolve_app_dir(project, region)
    print(f"\n定位到的「递交文件」目录：{d or '(未找到——目录不存在/简称查不到)'}")
    if d:
        docs = sorted(glob.glob(os.path.join(d, "*.docx")))
        print(f"该目录下 .docx（本层，{len(docs)} 个）：")
        for f in docs:
            print(f"   - {os.path.basename(f)}  (mtime={os.path.getmtime(f):.0f})")
        if not docs:
            subs = sorted(glob.glob(os.path.join(d, "**", "*.docx"), recursive=True))
            print(f"   本层无 docx，递归子目录找到 {len(subs)} 个")
            for f in subs:
                print(f"   - {os.path.relpath(f, d)}")

    kw = m.APP_FILE_KEYWORDS.get(region)
    print(f"\n选取规则（{region}）：最新 .docx" + (f"，文件名含 {kw}" if kw else "（无关键词）"))
    files = m.find_application_files(project, region=region)
    spec = files.get("spec")
    print(f"\n★ 最终命中申请文件：{spec or '(无——未匹配到符合条件的 docx)'}")


if __name__ == "__main__":
    main()
