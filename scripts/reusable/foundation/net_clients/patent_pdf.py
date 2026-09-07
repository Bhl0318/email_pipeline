"""按公开号/专利号从 FreePatentsOnline (FPO) 下载专利 PDF（基础通用层 · 网络与服务调用）。

抽自 oa/download_patent_pdf.py，逻辑不变。零业务耦合。
FPO 有 Cloudflare 反爬：优先用 curl_cffi 模拟 Chrome TLS 指纹绕过，装不上回退 requests。
  pip install curl_cffi   # 强烈建议；否则大概率被 reset
支持多种号写法：US20250150762A1 / 20250150762 / "US 2025/0150762 A1" / CN110693604A（取数字部分）。
"""
import os
import re
import sys

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
        return cffi.Session(impersonate="chrome", headers=_BROWSER_HEADERS), True
    except Exception:
        import requests
        s = requests.Session()
        s.headers.update(_BROWSER_HEADERS)
        print("  [提示] 未装 curl_cffi，回退 requests，FPO 可能仍被 reset。建议: pip install curl_cffi",
              file=sys.stderr)
        return s, False


def _digits(raw):
    """取号里的纯数字部分：去分隔符/开头国别前缀/末尾 kind code，只留数字。
    US20250150762A1 → 20250150762；CN110693604A → 110693604。"""
    s = re.sub(r"[\s,/.\-]", "", (raw or "").strip().upper())
    if len(s) >= 2 and s[:2].isalpha():
        s = s[2:]
    s = re.sub(r"[A-Z]\d?$", "", s)
    return re.sub(r"[^0-9]", "", s)


def _extract_pdf_url(page_html):
    """从 FPO 页面 HTML 取 iframe 的 S3 预签名 PDF 直链（去 HTML 转义 & 去 #fragment）。取不到返回 ""。"""
    m = re.search(r'<iframe[^>]+src=["\']([^"\']*sumobrain[^"\']*)["\']', page_html, re.I)
    if not m:
        m = re.search(r'(https?://s3\.amazonaws\.com/pdf\.sumobrain\.com/[^"\'\s]+)', page_html, re.I)
    if not m:
        return ""
    return m.group(1).replace("&amp;", "&").split("#")[0]


def _save_pdf(url, out_path, session):
    """下载 url，校验开头 %PDF。成功存盘返回 True，否则打印原因返回 False。"""
    try:
        r = session.get(url, timeout=120)
        data = r.content
    except Exception as e:
        print(f"  下载异常: {e}", file=sys.stderr)
        return False
    if not data[:5].startswith(b"%PDF"):
        print(f"  下到的不是 PDF（HTTP {r.status_code}，开头={data[:12]!r}）", file=sys.stderr)
        return False
    with open(out_path, "wb") as f:
        f.write(data)
    return True


def download_patent_pdf(raw_no, out_path=None, session=None):
    """从 FPO 下载一件专利 PDF。返回本地路径或 None。

    输入：raw_no 专利号（多种写法）；out_path（可选，默认 {数字号}.pdf）；session（可选，批量复用）。
    """
    if session is None:
        session, _ = _new_session()
    num = _digits(raw_no)
    if not num:
        print(f"[跳过] 取不到数字号: {raw_no!r}", file=sys.stderr)
        return None
    out_path = out_path or f"{num}.pdf"
    try:
        session.get("https://www.freepatentsonline.com/", timeout=40)  # 拿 cookie，失败不阻断
    except Exception:
        pass
    page_url = f"https://www.freepatentsonline.com/{num}.pdf"
    print(f"[{raw_no} → {num}] 取页面 {page_url}", file=sys.stderr)
    try:
        page = session.get(page_url, timeout=60).text
    except Exception as e:
        print(f"  打开页面失败: {e}", file=sys.stderr)
        return None
    pdf_url = _extract_pdf_url(page)
    if not pdf_url:
        dbg = out_path + ".debug.html"
        try:
            with open(dbg, "w", encoding="utf-8") as f:
                f.write(page)
        except Exception:
            dbg = "(存盘失败)"
        print(f"  页面里没找到 iframe PDF 链接（可能挑战/登录页），已存 {dbg}", file=sys.stderr)
        return None
    print(f"  PDF直链(S3签名): {pdf_url[:90]}…", file=sys.stderr)
    if _save_pdf(pdf_url, out_path, session):
        print(f"  ✓ 成功: {out_path}")
        return out_path
    print(f"  ✗ 下载 S3 直链失败: {raw_no}", file=sys.stderr)
    return None
