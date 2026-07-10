#!/usr/bin/env python3
"""
CN 审查意见通知书 PDF 解析工具 — 提取「本通知书引用下列对比文件」表 + OA 次数。

策略（对齐 parse_us_pdf 的三级降级）：
  1. PyMuPDF 提取文本 → 正则锁定「本通知书引用下列对比文件(其编号续前…)」块 → 逐行取三元组
  2. 正则拿不到 → 文本发 DeepSeek 提取
  3. 文本为空（扫描件）→ 渲染前 3 页图片发 qwen-vl-max 提取

只取正式引用表（编号 / 文件号或名称 / 公开日期），不收评述正文里提到的文件；
「编号续前」是历史沿用，本次表里列什么就取什么。

用法:
  python3 parse_cn_pdf.py <PDF路径>

Python 调用:
  from parse_cn_pdf import extract_cn_ref_docs
  r = extract_cn_ref_docs("/path/to/oa.pdf")
  # r = {"ref_docs": [{"no":"3","doc_no":"CN216192880U","pub_date":"2022-04-05"}, ...],
  #      "oa_seq": 2, "notice_title": "第二次审查意见通知书"}
"""
import sys
import os
import json
import re
import base64

from openai import OpenAI

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# DeepSeek 配置（文本模式，复用 parse_us_pdf 的密钥）
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "REDACTED_API_KEY")
DEEPSEEK_MODEL = "deepseek-chat"

# Qwen VL 配置（图片模式，扫描件降级用）
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "REDACTED_API_KEY")
QWEN_VL_MODEL = "qwen-vl-max"

# 中文数字 → 阿拉伯数字（覆盖到二十几，够 OA 次数用）
_CN_DIGIT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
             "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

# 引用对比文件表的三元组：编号 / 文件号 / 公开日期（\s+ 跨越 PDF 抽出的换行）
_TRIPLE_RE = re.compile(r'(\d+)\s+([A-Z]{2}[0-9A-Z]{4,})\s+(\d{4}-\d{2}-\d{2})')


def _cn2int(cn):
    """中文数字串 → int（支持 一~九、十、十一~十九、二十~二十九）。失败返回 None。"""
    if not cn:
        return None
    if cn.isdigit():
        return int(cn)
    if cn == "十":
        return 10
    if "十" in cn:
        left, _, right = cn.partition("十")
        tens = _CN_DIGIT.get(left, 1) if left else 1
        ones = _CN_DIGIT.get(right, 0) if right else 0
        return tens * 10 + ones
    return _CN_DIGIT.get(cn)


def _pdf_to_text(pdf_path, max_pages=5):
    """用 PyMuPDF 提取 PDF 文本，返回 (text, is_scanned)。对齐 parse_us_pdf。"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for i in range(min(max_pages, len(doc))):
            page_text = doc[i].get_text()
            if page_text.strip():
                text += page_text + "\n"
        doc.close()
        return text, not bool(text.strip())
    except ImportError:
        print("需要 PyMuPDF: pip install pymupdf", file=sys.stderr)
        return "", True


def _slice_ref_block(text):
    """从全文里切出「本通知书引用下列对比文件」到「审查的结论性意见 / 5.」之间的块。
    切不出来时退回全文（让三元组正则自己找，风险低因为格式很特异）。"""
    start = text.find("本通知书引用下列对比文件")
    if start == -1:
        return text
    rest = text[start:]
    cut = re.search(r'审查的结论性意见|\n\s*5\s*[.．、]', rest)
    return rest[:cut.start()] if cut else rest


def _regex_extract_ref_docs(text):
    """正则从「引用对比文件」块里取三元组，返回 list[dict]。"""
    block = _slice_ref_block(text)
    docs = []
    seen = set()
    for no, doc_no, pub in _TRIPLE_RE.findall(block):
        key = (no, doc_no)
        if key in seen:
            continue
        seen.add(key)
        docs.append({"no": no, "doc_no": doc_no, "pub_date": pub})
    return docs


def _ai_extract_ref_docs_from_text(text):
    """DeepSeek 兜底：从文本里抽引用对比文件表。"""
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    block = _slice_ref_block(text)
    prompt = (
        "以下是中国专利审查意见通知书里「本通知书引用下列对比文件（其编号续前…）」那张表的文本。\n"
        "请只提取该表里的对比文件（不要提取正文评述里提到的文件）。\n"
        "每条含：编号(no)、文件号或名称(doc_no)、公开日期(pub_date, YYYY-MM-DD)。\n"
        '仅返回 JSON：{"ref_docs":[{"no":"3","doc_no":"CN216192880U","pub_date":"2022-04-05"}]}\n'
        '若本通知书未引用新的对比文件，返回：{"ref_docs":[]}\n'
        f"\n---\n{block[:3000]}\n---"
    )
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL, max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.choices[0].message.content.strip()
        m = re.search(r'\{.*\}', content, re.DOTALL)
        if m:
            return json.loads(m.group()).get("ref_docs", []) or []
    except Exception as e:
        print(f"DeepSeek 对比文件解析失败: {e}", file=sys.stderr)
    return []


def _ai_extract_ref_docs_from_images(pdf_path, max_pages=3):
    """扫描件降级：渲染前 N 页图片发 qwen-vl-max 抽引用对比文件表。"""
    try:
        import fitz
    except ImportError:
        return []
    doc = fitz.open(pdf_path)
    images_b64 = []
    for i in range(min(max_pages, len(doc))):
        pix = doc[i].get_pixmap(dpi=200)
        images_b64.append(base64.b64encode(pix.tobytes("png")).decode("utf-8"))
    doc.close()
    if not images_b64:
        return []
    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    content = [{
        "type": "text",
        "text": ('这是中国专利审查意见通知书。找到「本通知书引用下列对比文件」那张表，只提取该表里的对比文件。'
                 '仅返回 JSON：{"ref_docs":[{"no":"3","doc_no":"CN216192880U","pub_date":"2022-04-05"}]}')
    }]
    for b64 in images_b64:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
    try:
        resp = client.chat.completions.create(
            model=QWEN_VL_MODEL, max_tokens=400,
            messages=[{"role": "user", "content": content}],
        )
        rt = resp.choices[0].message.content.strip()
        m = re.search(r'\{.*\}', rt, re.DOTALL)
        if m:
            return json.loads(m.group()).get("ref_docs", []) or []
    except Exception as e:
        print(f"qwen-vl-max 对比文件解析失败: {e}", file=sys.stderr)
    return []


def parse_oa_seq(text):
    """从文本里取审查意见次数（第N次审查意见通知书 → N）。取不到返回 None。"""
    m = re.search(r'第([一二三四五六七八九十\d]+)次审查意见', text)
    return _cn2int(m.group(1)) if m else None


def _notice_title(text):
    m = re.search(r'第[一二三四五六七八九十\d]+次审查意见通知书', text)
    return m.group(0) if m else ""


def extract_cn_ref_docs(pdf_path):
    """从 CN 审查意见通知书 PDF 提取引用对比文件 + OA 次数。

    Returns:
        dict: {"ref_docs": list[dict], "oa_seq": int|None, "notice_title": str}
        ref_docs 每项：{"no","doc_no","pub_date"}；无引用/解析失败时为 []。
    """
    result = {"ref_docs": [], "oa_seq": None, "notice_title": ""}
    if not os.path.exists(pdf_path):
        print(f"PDF 文件不存在: {pdf_path}", file=sys.stderr)
        return result

    text, is_scanned = _pdf_to_text(pdf_path, max_pages=9)

    if text.strip():
        result["oa_seq"] = parse_oa_seq(text)
        result["notice_title"] = _notice_title(text)
        # 1. 正则
        docs = _regex_extract_ref_docs(text)
        if docs:
            print(f"[正则] 提取到 {len(docs)} 条对比文件", file=sys.stderr)
        else:
            # 2. DeepSeek 兜底（正则空可能是版式异常，也可能真无引用；交给模型判断）
            docs = _ai_extract_ref_docs_from_text(text)
            if docs:
                print(f"[DeepSeek] 提取到 {len(docs)} 条对比文件", file=sys.stderr)
        result["ref_docs"] = docs

    # 3. 扫描件图片降级
    if not result["ref_docs"] and is_scanned:
        print("PDF 为扫描件，使用图片识别...", file=sys.stderr)
        docs = _ai_extract_ref_docs_from_images(pdf_path, max_pages=3)
        if docs:
            print(f"[qwen-vl-max] 提取到 {len(docs)} 条对比文件", file=sys.stderr)
        result["ref_docs"] = docs

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 parse_cn_pdf.py <PDF路径>")
        sys.exit(1)
    r = extract_cn_ref_docs(sys.argv[1])
    print(json.dumps(r, ensure_ascii=False, indent=2))
