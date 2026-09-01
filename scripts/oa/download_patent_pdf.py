#!/usr/bin/env python3
"""按专利公开号/专利号从 freepatentsonline (FPO) 下载 PDF。

FPO 直链规则：https://www.freepatentsonline.com/{纯数字号}.pdf
支持多种输入写法：US20250150762A1 / 20250150762 / "US 2025/0150762 A1" / CN110693604A（取其中数字部分）。

用法:
  python download_patent_pdf.py US20250150762A1 [输出路径.pdf]
  python download_patent_pdf.py 20250150762
  python download_patent_pdf.py 20250150762 20070083192 110693604   # 批量

依赖: pip install requests
"""
import re
import sys
import os

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def _digits(raw):
    """取号里的纯数字部分：先去分隔符/国别前缀(开头2字母)/末尾 kind code(A1/B2/A/U…)，再留数字。
    US20250150762A1 → 20250150762；CN110693604A → 110693604；20250150762 → 20250150762。"""
    s = re.sub(r"[\s,/.\-]", "", (raw or "").strip().upper())
    if len(s) >= 2 and s[:2].isalpha():      # 去国别前缀
        s = s[2:]
    s = re.sub(r"[A-Z]\d?$", "", s)          # 去末尾 kind code
    return re.sub(r"[^0-9]", "", s)


def _download(url, out_path, session):
    """下载 url 到 out_path，校验开头是 %PDF。成功返回 True，否则删掉文件返回 False。"""
    try:
        r = session.get(url, timeout=120, stream=True)
    except Exception as e:
        print(f"  下载异常: {e}", file=sys.stderr)
        return False
    if r.status_code != 200:
        print(f"  下载返回 HTTP {r.status_code}", file=sys.stderr)
        return False
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    with open(out_path, "rb") as f:
        head = f.read(5)
    if not head.startswith(b"%PDF"):
        print(f"  下到的不是 PDF（开头={head!r}），可能被 Cloudflare/登录页拦截", file=sys.stderr)
        os.remove(out_path)
        return False
    return True


def download_patent_pdf(raw_no, out_path=None, session=None):
    """从 FPO 下载一件专利 PDF。返回本地路径或 None。"""
    session = session or requests.Session()
    session.headers.update({"User-Agent": UA,
                            "Referer": "https://www.freepatentsonline.com/"})
    num = _digits(raw_no)
    if not num:
        print(f"[跳过] 取不到数字号: {raw_no!r}", file=sys.stderr)
        return None
    out_path = out_path or f"{num}.pdf"
    url = f"https://www.freepatentsonline.com/{num}.pdf"
    print(f"[{raw_no} → {num}] {url}", file=sys.stderr)
    if _download(url, out_path, session):
        print(f"  ✓ 成功: {out_path}")
        return out_path
    print(f"  ✗ 失败: {raw_no}", file=sys.stderr)
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python download_patent_pdf.py <公开号/专利号> [更多号... 或 输出.pdf]")
        sys.exit(1)
    args = sys.argv[1:]
    if len(args) == 2 and args[1].lower().endswith(".pdf"):
        sys.exit(0 if download_patent_pdf(args[0], args[1]) else 1)
    sess = requests.Session()
    fail = sum(1 for a in args if not download_patent_pdf(a, session=sess))
    sys.exit(1 if fail else 0)
