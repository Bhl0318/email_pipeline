#!/usr/bin/env python3
"""预览 USPTO 某申请的可下载文档「会命名成什么文件名」——只调 API 取列表+算文件名并打印，
不实际下载、不写盘。文件名逻辑与 downloadByAPI.downLoad_file 完全一致：
  {发文日officialDate}-{sanitize(documentCodeDescriptionText)}-{案号}.{ext}

用法:
  python3 uspto_docs_preview.py <USPTO申请号> [--project 案号] [--doc-code 1449] [--date 08/11/2026]
  # 不给 --doc-code/--date 则列出该申请全部文档
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from downloadByAPI import USPTOApplication  # 复用 apikey + sanitize_filename，保证与实际下载同款命名

_EXT = {"PDF": "pdf", "MS_WORD": "docx"}


def _norm_date(d):
    """MM/DD/YYYY → YYYY-MM-DD；已是 ISO 则取前10位。"""
    d = (d or "").strip()
    if "/" in d:
        p = d.split("/")
        if len(p) == 3:
            return f"{p[2]}-{p[0].zfill(2)}-{p[1].zfill(2)}"
    return d[:10]


def main():
    ap = argparse.ArgumentParser(description="预览 USPTO 文档下载文件名(不下载)")
    ap.add_argument("application", help="USPTO 申请号，如 19181318")
    ap.add_argument("--project", default="", help="案号(填进文件名；不给则用申请号占位)")
    ap.add_argument("--doc-code", default="", help="只看某文档代码，如 CTNF / 1449 / 892")
    ap.add_argument("--date", default="", help="只看某 officialDate(YYYY-MM-DD 或 MM/DD/YYYY)")
    args = ap.parse_args()

    project = args.project or args.application
    want_date = _norm_date(args.date)

    tmp = tempfile.mkdtemp(prefix="uspto_preview_")   # 只为借 apikey/sanitize，全程不往里写文件
    try:
        uspto = USPTOApplication(download_dir=tmp)
        url = f"https://api.uspto.gov/api/v1/patent/applications/{args.application}/documents"
        resp = requests.get(url, headers={"X-API-KEY": uspto.apikey}, timeout=30)
        print(f"[HTTP {resp.status_code}] {url}", file=sys.stderr)
        if resp.status_code != 200:
            print(resp.text[:500], file=sys.stderr)
            sys.exit(1)

        bag = json.loads(resp.text).get("documentBag", []) or []
        rows = []
        for doc in bag:
            code = doc.get("documentCode", "") or ""
            odate = (doc.get("officialDate", "") or "")[:10]
            if args.doc_code and code != args.doc_code:
                continue
            if want_date and odate != want_date:
                continue
            desc = doc.get("documentCodeDescriptionText", "") or ""
            safe = uspto.sanitize_filename(desc)
            for opt in (doc.get("downloadOptionBag") or []):
                ext = _EXT.get(opt.get("mimeTypeIdentifier", ""), "txt")
                rows.append((odate, code, f"{odate}-{safe}-{project}.{ext}"))

        rows.sort()
        for odate, code, fn in rows:
            print(f"{odate}  [{code:<14}] {fn}")
        print(f"\n共 {len(rows)} 个可下载文件（仅预览，未下载/未写盘）", file=sys.stderr)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
