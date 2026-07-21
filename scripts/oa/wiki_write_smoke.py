#!/usr/bin/env python3
"""Wiki 写入冒烟测试 —— 只测「新增OA登记页」写入，不连邮箱/数据库。

复用真实写入路径：get_page → _insert_rows_by_month(按月折叠 + 置顶) → update_page。

用法（在能连内网 Wiki 10.10.70.90 的机器上跑）:
  # ① dry：只拉页面 + 本地拼装 + 打印，不改页面（先跑这个确认能连上、结构对）
  python3 wiki_write_smoke.py

  # ② 真正写一行测试数据到页面（写完记得手动删掉那行）
  python3 wiki_write_smoke.py --live

  # 指定别的页面标题（默认用 oainfo_cli 里的 OA_LIST_PAGE_TITLE）
  python3 wiki_write_smoke.py --title "某测试页"
"""
import os
import sys
import argparse
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from oainfo_cli import (
    WikiClient, OA_LIST_PAGE_TITLE, FOLLOWUP_ROTATION,
    _build_table_row, _month_title, _insert_rows_by_month,
)


def main():
    ap = argparse.ArgumentParser(description="Wiki 写入冒烟测试")
    ap.add_argument("--live", action="store_true",
                    help="真正写入页面；不加则只读+本地拼装+打印")
    ap.add_argument("--title", default=OA_LIST_PAGE_TITLE,
                    help=f"目标页面标题（默认: {OA_LIST_PAGE_TITLE}）")
    args = ap.parse_args()

    # 醒目的测试数据（写完手动删）
    results = [{
        "project": "TEST-0001CN00",
        "oa_remark": "WIKI写入测试",
        "entrust_date": "2026-07-21",
        "oa_doc_date": "2026-07-20",
        "project_deadline": "2026-09-20",
        "project_name": "第一次审查意见答复【冒烟测试-可删】",
    }]

    wiki = WikiClient()
    print(f"目标页面: {args.title}")
    page = wiki.get_page(args.title)
    if not page:
        print("❌ 未找到页面（检查标题 / 网络 / Wiki 凭据）")
        sys.exit(1)
    print(f"✓ 拉到页面: id={page['id']} version={page['version']} body长度={len(page['body'])}")

    rows = ""
    for i, item in enumerate(results):
        rows += _build_table_row(item, FOLLOWUP_ROTATION[i % len(FOLLOWUP_ROTATION)])

    month = _month_title(datetime.now())
    new_body, created = _insert_rows_by_month(page["body"], rows, month)
    print(f"目标月份折叠块: {month}  （新建={created}）")
    print(f"新行已进 body: {'TEST-0001CN00' in new_body}")
    print(f"body 长度: {len(page['body'])} → {len(new_body)}")

    if not args.live:
        print("\n[dry] 未写入页面。确认无误后加 --live 真正写入。")
        return

    code = wiki.update_page(page["id"], args.title, new_body, page["version"])
    if code == 200:
        print(f"\n✓ 写入成功 (HTTP {code})。请到页面核对 TEST-0001CN00 是否在 {month} 块顶部，核对后删掉该测试行。")
    else:
        print(f"\n❌ 写入失败 (HTTP {code})")
        sys.exit(1)


if __name__ == "__main__":
    main()
