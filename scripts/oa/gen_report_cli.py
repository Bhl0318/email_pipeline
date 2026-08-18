#!/usr/bin/env python3
"""OA 案件报告 —— 独立测试脚本：读申请文件(+审意PDF) → DeepSeek → 输出 markdown。

不连邮箱/库，只做「读文档 → 生成报告」这一步，方便单独调提示词与效果。

用法：
  # 用 申请文件/ 里的样例文档生成（测试期 MATCH_BY_CASE_NO=False，任意案号都用样例）
  python3 gen_report_cli.py

  # 指定案号 / 发明名称 / 客户 / 地区，并把审意 PDF 一并喂进去（做第四大类）
  python3 gen_report_cli.py -c 20618-0424US00 -n "一种自适应放疗方法" --customer 联影 -r US \
      --oa-pdf /path/审查意见通知书.pdf -o 报告.md

  # 指定申请文件目录
  python3 gen_report_cli.py --app-dir /path/申请文件

参数全部可选；不给就用默认样例。报告打到 stdout；给 -o 时另存文件。
"""
import argparse
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

from oa_report_ai import build_case_report, find_application_files, DEFAULT_APP_DIR  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="读文档生成 OA 案件报告(markdown) —— 测试用")
    ap.add_argument("-c", "--case", default="20618-0424US00", help="案号（默认样例）")
    ap.add_argument("-n", "--name", default="(测试案件)", help="发明名称")
    ap.add_argument("--customer", default="", help="客户名称")
    ap.add_argument("-r", "--region", default="US", help="地区 US/EP/CN（默认 US）")
    ap.add_argument("--deadline", default="", help="官方答复期限 YYYY-MM-DD（可选）")
    ap.add_argument("--oa-pdf", dest="oa_pdf", default="", help="审意官文 PDF 路径（做第四大类；可给多个用逗号分隔）")
    ap.add_argument("--app-dir", dest="app_dir", default=None, help="申请文件目录（默认 申请文件/）")
    ap.add_argument("-o", "--out", default="", help="输出 markdown 文件路径（不给则只打印）")
    args = ap.parse_args()

    app_dir = args.app_dir or DEFAULT_APP_DIR
    files = find_application_files(args.case, base_dir=app_dir)
    print(f"[申请文件目录] {app_dir}", file=sys.stderr)
    print(f"[匹配到] 说明书: {files.get('spec') or '（无）'}", file=sys.stderr)
    print(f"[匹配到] 权利要求书: {files.get('claims') or '（无）'}", file=sys.stderr)

    oa_pdf = [p.strip() for p in args.oa_pdf.split(",") if p.strip()] if args.oa_pdf else None
    print(f"[审意 PDF] {oa_pdf or '（无，第四大类将标待补）'}", file=sys.stderr)
    print("[生成中] 调用 DeepSeek …", file=sys.stderr)

    item = {
        "project": args.case,
        "project_name": args.name,
        "customer": args.customer,
        "region": args.region,
        "deadline": args.deadline,
    }
    md = build_case_report(item, oa_pdf_path=oa_pdf, app_dir=app_dir)

    print(md)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"\n[已保存] {os.path.abspath(args.out)}", file=sys.stderr)


if __name__ == "__main__":
    main()
