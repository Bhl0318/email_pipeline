#!/usr/bin/env python3
"""US 官文对比文件抽取 — 从 PTO-892(Notice of References Cited) 或主官文正文，
提取审查员引用的对比文件（US/外国 专利号·公开号），归一化成 Google Patents 号，
输出与 parse_cn_pdf 相同的 ref_docs 形状，供 oainfo_cli.fill_ref_docs_in_oa_row 复用。

数据源优先级：PTO-892（审查员正式引用清单）> 主官文 PDF 正文。
仅取审查员引用（892），不取申请人 IDS（1449）。

用法:
  from parse_us_refs import extract_us_ref_docs, normalize_pub_no
  r = extract_us_ref_docs("/path/to/892.pdf")
  # r = {"ref_docs": [{"no":"1","doc_no":"US20150123456A1","pub_date":"2015-05-07"}, ...]}
"""
import sys
import os
import json
import re

from openai import OpenAI

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# DeepSeek 配置（与 parse_cn_pdf 一致，复用同一密钥）
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "REDACTED_API_KEY")
DEEPSEEK_MODEL = "deepseek-chat"

# Google Patents 认的国别/地区前缀
_COUNTRIES = ("US", "CN", "JP", "EP", "WO", "KR", "DE", "GB", "FR", "TW",
              "CA", "AU", "IN", "RU", "BR", "ES", "IT", "NL", "SE", "CH")

# PTO-892 文件号列的规范形：US-2019/0123456-A1 / US-9,123,456-B2 / CN-216192880-U
_REF_RE = re.compile(r'\b([A-Z]{2})[\-\s]?([0-9][0-9,/]{4,15}[0-9])[\-\s]?([A-Z]\d?)\b')


def normalize_pub_no(raw, default_country="US"):
    """把官文里的对比文件号归一化成 Google Patents 号（去逗号/空格/斜杠/连字符/点）。
    e.g. 'US 9,123,456 B2'->'US9123456B2'；'US 2015/0123456 A1'->'US20150123456A1'；
         'US-2015/0123456-A1'->'US20150123456A1'；'CN 216192880 U'->'CN216192880U'；
         '2015/0123456 A1'->'US20150123456A1'（无前缀默认美国）。"""
    if not raw:
        return ""
    s = re.sub(r'[\s,/.\-]', '', str(raw).strip().upper())
    if not s:
        return ""
    if s[:2] in _COUNTRIES:
        return s
    if s[0].isdigit():
        return default_country + s
    return s


def _pdf_to_text(pdf_path, max_pages=6):
    """PyMuPDF 提取 PDF 文本（前 N 页够 892/官文引用段）。"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for i in range(min(max_pages, len(doc))):
            pt = doc[i].get_text()
            if pt.strip():
                text += pt + "\n"
        doc.close()
        return text
    except Exception as e:
        print(f"[US-ref] PDF 读取失败 {pdf_path}: {e}", file=sys.stderr)
        return ""


def _regex_extract(text):
    """正则抽 892 规范文件号（带国别前缀 + kind code，降低把申请号/分类号误判）。"""
    docs, seen = [], set()
    for cc, num, kind in _REF_RE.findall(text):
        if cc not in _COUNTRIES:
            continue
        doc_no = normalize_pub_no(f"{cc}{num}{kind}")
        if not doc_no or doc_no in seen:
            continue
        seen.add(doc_no)
        docs.append({"no": str(len(docs) + 1), "doc_no": doc_no, "pub_date": ""})
    return docs


def _ai_extract(text):
    """DeepSeek 兜底：正则抽不到时，从 892/官文文本抽审查员引用的对比文件。"""
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    prompt = (
        "以下是美国专利审查意见(Office Action)或其 PTO-892 (Notice of References Cited) 的文本。\n"
        "请只提取审查员引用的对比文件（专利文献/公开号），忽略申请人 IDS(1449)、申请号(application no)、"
        "分类号(CPC/USPC)、以及正文论述里非对比文件的内容。\n"
        "每条含：doc_no（专利号或公开号）、pub_date（YYYY-MM-DD，取不到留空）。\n"
        "doc_no 请去掉逗号/空格/斜杠/连字符，带国别前缀（美国默认 US），"
        "如 US20150123456A1 / US9123456B2 / CN216192880U。\n"
        '仅返回 JSON：{"ref_docs":[{"doc_no":"US20150123456A1","pub_date":""}]}\n'
        '未引用任何对比文件返回：{"ref_docs":[]}\n'
        f"\n---\n{text[:4000]}\n---"
    )
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL, max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.choices[0].message.content.strip()
        m = re.search(r'\{.*\}', content, re.DOTALL)
        if not m:
            return []
        raw = json.loads(m.group()).get("ref_docs", []) or []
        out, seen = [], set()
        for d in raw:
            dn = normalize_pub_no(d.get("doc_no", ""))
            if not dn or dn in seen:
                continue
            seen.add(dn)
            out.append({"no": str(len(out) + 1), "doc_no": dn,
                        "pub_date": (d.get("pub_date") or "").strip()})
        return out
    except Exception as e:
        print(f"[US-ref] DeepSeek 解析失败: {e}", file=sys.stderr)
        return []


def extract_us_ref_docs(pdf_path):
    """从 US 官文/892 PDF 提取审查员引用对比文件。
    Returns: {"ref_docs": [{"no","doc_no","pub_date"}, ...]}；无引用/失败时 ref_docs=[]。"""
    result = {"ref_docs": []}
    if not pdf_path or not os.path.exists(pdf_path):
        return result
    text = _pdf_to_text(pdf_path)
    if not text.strip():
        print(f"[US-ref] 无文本层（可能是扫描件），跳过: {pdf_path}", file=sys.stderr)
        return result
    docs = _regex_extract(text)
    if docs:
        print(f"[US-ref][正则] 提取到 {len(docs)} 条对比文件", file=sys.stderr)
    else:
        docs = _ai_extract(text)
        if docs:
            print(f"[US-ref][DeepSeek] 提取到 {len(docs)} 条对比文件", file=sys.stderr)
    result["ref_docs"] = docs
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 parse_us_refs.py <892或官文.pdf>")
        sys.exit(1)
    print(json.dumps(extract_us_ref_docs(sys.argv[1]), ensure_ascii=False, indent=2))
