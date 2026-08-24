#!/usr/bin/env python3
"""按 pageId 打印某 Confluence 页的 storage HTML（供分析结构，如人员负荷页）。

用法（在能连 10.10.70.90 的机器上）：
  python3 dump_wiki_page.py 151195467
  python3 dump_wiki_page.py 151195467 > page.html
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    page_id = sys.argv[1] if len(sys.argv) > 1 else "151195467"
    from oainfo_cli import WikiClient
    p = WikiClient().get_page_by_id(page_id)
    if not p:
        print(f"[取页失败] pageId={page_id}", file=sys.stderr)
        return
    print(f"[标题] {p['title']}  [版本] {p['version']}  [空间] {p['space_key']}", file=sys.stderr)
    print(p["body"])


if __name__ == "__main__":
    main()
