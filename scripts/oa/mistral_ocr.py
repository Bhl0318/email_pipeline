#!/usr/bin/env python3
"""Mistral OCR 服务客户端：上传 PDF → 返回整篇 Markdown。

服务见 projects/mistral-ocr-service（VPS，自签证书，默认 https://149.248.15.179:8445）。
配置优先级：环境变量 MISTRAL_OCR_URL / MISTRAL_OCR_KEY → pipeline_config.json 的
  "mistral_ocr": { "base": "...", "api_key": "..." }。未配 api_key 时返回 ""（调用方回退 qwen-vl）。

  from mistral_ocr import pdf_to_markdown
  md = pdf_to_markdown("/path/to/scan.pdf")   # 失败/未配置返回 ""
"""
import os
import sys
import json
import functools

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_BASE = "https://149.248.15.179:8445"


@functools.lru_cache(maxsize=1)
def _config():
    """(base, api_key)：env 优先，其次 pipeline_config.json 的 mistral_ocr。"""
    base = os.environ.get("MISTRAL_OCR_URL", "").strip()
    key = os.environ.get("MISTRAL_OCR_KEY", "").strip()
    if not base or not key:
        try:
            cfg_path = os.path.join(SCRIPT_DIR, "..", "pipeline_config.json")
            with open(cfg_path, encoding="utf-8") as f:
                m = (json.load(f).get("mistral_ocr") or {})
            base = base or (m.get("base") or "").strip()
            key = key or (m.get("api_key") or "").strip()
        except Exception:
            pass
    return (base or _DEFAULT_BASE).rstrip("/"), key


# 进程内缓存：同一份文件一次运行内只真正 OCR 一次，后续步骤直接复用首份结果。
# 键=(绝对路径, 修改时间, 大小)；只缓存成功（非空）结果，失败不缓存（免得偶发失败堵死后续步骤）。
_MD_CACHE = {}


def pdf_to_markdown(pdf_path, timeout=360, retries=3, backoff=3):
    """上传 PDF 到 Mistral OCR 服务，返回整篇 Markdown；未配置 api_key / 多次失败返回 ""。
    服务偶发非 200/超时，重试 retries 次（递增退避 backoff*次数 秒）。
    同一份文件本进程内已成功识别过的，直接返回缓存，不重复 OCR。"""
    if not pdf_path or not os.path.isfile(pdf_path):
        return ""
    try:
        st = os.stat(pdf_path)
        cache_key = (os.path.abspath(pdf_path), st.st_mtime, st.st_size)
    except OSError:
        cache_key = None
    if cache_key is not None and cache_key in _MD_CACHE:
        print(f"[mistral-ocr] {os.path.basename(pdf_path)} 命中缓存，跳过重复 OCR", file=sys.stderr)
        return _MD_CACHE[cache_key]
    base, key = _config()
    if not key:
        print("[mistral-ocr] 未配置 api_key（MISTRAL_OCR_KEY 或 pipeline_config.mistral_ocr.api_key），跳过",
              file=sys.stderr)
        return ""
    try:
        import time
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 自签证书
    except Exception as e:
        print(f"[mistral-ocr] 依赖缺失: {e}", file=sys.stderr)
        return ""
    with open(pdf_path, "rb") as f:
        data = f.read()   # 读成 bytes，便于每次重试重发
    fname = os.path.basename(pdf_path)
    last = ""
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(
                f"{base}/ocr",
                headers={"X-API-Key": key},
                files={"file": (fname, data, "application/pdf")},
                verify=False,
                timeout=timeout,
            )
            if r.status_code == 200:
                md = (r.json().get("markdown") or "").strip()
                if md:
                    print(f"[mistral-ocr] {fname} OK（第{attempt}次）", file=sys.stderr)
                    if cache_key is not None:
                        _MD_CACHE[cache_key] = md   # 只缓存成功结果，供后续步骤复用
                return md
            last = f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            last = str(e)
        print(f"[mistral-ocr] {fname} 第{attempt}/{retries}次失败: {last}", file=sys.stderr)
        if attempt < retries:
            time.sleep(backoff * attempt)   # 递增退避 3s / 6s ...
    return ""


def fpo_reference_to_markdown(publication_number, timeout=420):
    """请 OCR 服务在其所在 VPS 下载对比文件（FPO 优先），返回 OCR Markdown。"""
    base, key = _config()
    if not key:
        raise ValueError("未配置 MISTRAL_OCR_KEY 或 mistral_ocr.api_key")
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.post(
        f"{base}/fpo-reference",
        headers={"X-API-Key": key},
        json={"publication_number": publication_number},
        verify=False,
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("publication_number") != publication_number:
        raise ValueError("OCR 服务返回的公开号与请求不符")
    markdown = (payload.get("markdown") or "").strip()
    if not markdown:
        raise ValueError("OCR 服务未返回对比文件正文")
    return markdown, payload.get("source", "")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 mistral_ocr.py <pdf路径> [输出.md]")
        sys.exit(1)
    _md = pdf_to_markdown(sys.argv[1])
    if len(sys.argv) > 2 and _md:
        with open(sys.argv[2], "w", encoding="utf-8") as w:
            w.write(_md)
        print(f"已保存: {sys.argv[2]}")
    else:
        print(_md[:2000] if _md else "(空/失败)")
