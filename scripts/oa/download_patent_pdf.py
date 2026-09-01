#!/usr/bin/env python3
"""按专利公开号/专利号从 freepatentsonline (FPO) 下载 PDF。

FPO 直链规则：https://www.freepatentsonline.com/{纯数字号}.pdf
支持多种输入写法：US20250150762A1 / 20250150762 / "US 2025/0150762 A1" / CN110693604A（取其中数字部分）。

FPO 有 Cloudflare 反爬（会在 TLS 层直接 reset 掉普通 Python 请求）。
本脚本**优先用 curl_cffi 模拟 Chrome 的 TLS 指纹**绕过，装不上时回退 requests（多半会被 reset）：
  pip install curl_cffi        # 强烈建议装这个，否则大概率下不下来
  pip install requests         # 回退用

用法:
  python download_patent_pdf.py US20250150762A1 [输出路径.pdf]
  python download_patent_pdf.py 20250150762
  python download_patent_pdf.py 20250150762 20070083192 110693604   # 批量
"""
import re
import sys
import os

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
_BROWSER_HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.freepatentsonline.com/",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}


def _new_session():
    """优先 curl_cffi(模拟 Chrome TLS 指纹，绕 Cloudflare)，否则回退 requests。返回 (session, is_cffi)。"""
    try:
        from curl_cffi import requests as cffi
        s = cffi.Session(impersonate="chrome", headers=_BROWSER_HEADERS)
        return s, True
    except Exception:
        import requests
        s = requests.Session()
        s.headers.update(_BROWSER_HEADERS)
        print("  [提示] 未装 curl_cffi，回退 requests，FPO 可能仍被 reset。"
              "建议: pip install curl_cffi", file=sys.stderr)
        return s, False


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
    if session is None:
        session, _ = _new_session()
    num = _digits(raw_no)
    if not num:
        print(f"[跳过] 取不到数字号: {raw_no!r}", file=sys.stderr)
        return None
    out_path = out_path or f"{num}.pdf"
    # 先访问首页拿 cookie（过 Cloudflare 一次性校验），失败不阻断
    try:
        session.get("https://www.freepatentsonline.com/", timeout=40)
    except Exception:
        pass
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
    sess, _ = _new_session()
    fail = sum(1 for a in args if not download_patent_pdf(a, session=sess))
    sys.exit(1 if fail else 0)
