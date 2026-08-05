#!/usr/bin/env python3
"""
US 官文 PDF 解析工具 — 提取答复期限（months）。

策略：
  1. PyMuPDF 提取文本 → 正则匹配 "expire X MONTHS"
  2. 正则失败 → 文本发 DeepSeek 提取
  3. 文本为空（扫描件）→ 渲染前3页图片发 qwen-vl-max 提取

用法:
  python3 parse_us_pdf.py <PDF路径> [mailing_date]
  python3 parse_us_pdf.py ../attachment/xxx.pdf 2026-01-23

Python 调用:
  from parse_us_pdf import extract_us_deadline
  result = extract_us_deadline("/path/to/oa.pdf", mailing_date="2026-03-30")
  # result = {"months": 3, "deadline": "2026-06-30", "mailing_date": "2026-03-30"}
"""
import sys
import os
import json
import re
import base64
from datetime import datetime

from openai import OpenAI

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# DeepSeek 配置（文本模式）
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "REDACTED_API_KEY")
DEEPSEEK_MODEL = "deepseek-chat"

# Qwen VL 配置（图片模式，扫描件降级用）
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "REDACTED_API_KEY")
QWEN_VL_MODEL = "qwen-vl-max"

# 英文数词 → 数字映射
WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12,
}


def _add_months(dt, months):
    """日期加 N 个月。"""
    month = dt.month + months
    year = dt.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                        31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return dt.replace(year=year, month=month, day=day)


def _pdf_to_text(pdf_path, max_pages=5):
    """用 PyMuPDF 提取 PDF 文本，返回文本和是否为扫描件标记。"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for i in range(min(max_pages, len(doc))):
            page_text = doc[i].get_text()
            if page_text.strip():
                text += page_text + "\n"
        doc.close()
        if text.strip():
            return text, False

        # PyMuPDF 无文本，尝试 pypdf
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            for i in range(min(max_pages, len(reader.pages))):
                text += (reader.pages[i].extract_text() or "") + "\n"
        except Exception:
            pass

        return text, not bool(text.strip())
    except ImportError:
        print("需要 PyMuPDF: pip install pymupdf", file=sys.stderr)
        return "", True


def _regex_extract_months(text):
    """用正则从文本中提取 expire X MONTHS 的月数。"""
    # 匹配 "expire THREE MONTHS" 或 "expire 3 months"
    m = re.search(r'expire[sd]?\s+(\w+)\s+months?\b', text, re.IGNORECASE)
    if m:
        word = m.group(1).lower()
        if word.isdigit():
            return int(word)
        return WORD_TO_NUM.get(word)
    return None


def _ai_extract_months_from_text(text):
    """用 DeepSeek 从文本中提取答复月数。"""
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    prompt = f"""This is text from a USPTO Office Action. Find the statutory period for reply.
Look for text like "expire THREE MONTHS from the mailing date".
Return ONLY JSON: {{"months": <integer>}}
If not found, return: {{"months": null}}

---
{text[:4000]}
---"""

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        m = re.search(r'\{.*?\}', content, re.DOTALL)
        if m:
            result = json.loads(m.group())
            return result.get("months")
    except Exception as e:
        print(f"DeepSeek 解析失败: {e}", file=sys.stderr)
    return None


def _ai_extract_months_from_images(pdf_path, max_pages=3):
    """扫描件降级：渲染前 N 页为图片，发 qwen-vl-max 提取月数。"""
    try:
        import fitz
    except ImportError:
        print("需要 PyMuPDF: pip install pymupdf", file=sys.stderr)
        return None

    doc = fitz.open(pdf_path)
    images_b64 = []
    for i in range(min(max_pages, len(doc))):
        pix = doc[i].get_pixmap(dpi=200)
        b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
        images_b64.append(b64)
    doc.close()

    if not images_b64:
        return None

    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)

    content = [{
        "type": "text",
        "text": 'Find "expire X MONTHS from the mailing date" in these USPTO Office Action pages. Return ONLY JSON: {"months": <integer>}'
    }]
    for b64 in images_b64:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})

    try:
        response = client.chat.completions.create(
            model=QWEN_VL_MODEL,
            max_tokens=50,
            messages=[{"role": "user", "content": content}]
        )
        resp_text = response.choices[0].message.content.strip()
        m = re.search(r'\{.*?\}', resp_text, re.DOTALL)
        if m:
            result = json.loads(m.group())
            months = result.get("months")
            if months and months > 0:
                return months
    except Exception as e:
        print(f"qwen-vl-max 解析失败: {e}", file=sys.stderr)
    return None


def _ai_pph_decision_from_images(pdf_path, max_pages=3):
    """扫描件降级：渲染前 N 页发 qwen-vl-max 判断 PPH 决定是 dismissed 还是 granted。"""
    try:
        import fitz
    except ImportError:
        return ""
    doc = fitz.open(pdf_path)
    images_b64 = []
    for i in range(min(max_pages, len(doc))):
        pix = doc[i].get_pixmap(dpi=200)
        images_b64.append(base64.b64encode(pix.tobytes("png")).decode("utf-8"))
    doc.close()
    if not images_b64:
        return ""
    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    content = [{
        "type": "text",
        "text": ('These are pages of a USPTO PPH (Patent Prosecution Highway) decision. '
                 'Is the PPH request/petition DISMISSED or GRANTED? '
                 'Return ONLY JSON: {"decision": "dismissed"} or {"decision": "granted"}.')
    }]
    for b64 in images_b64:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
    try:
        resp = client.chat.completions.create(
            model=QWEN_VL_MODEL, max_tokens=30,
            messages=[{"role": "user", "content": content}])
        m = re.search(r'\{.*?\}', resp.choices[0].message.content.strip(), re.DOTALL)
        if m:
            d = (json.loads(m.group()).get("decision") or "").lower()
            if "dismiss" in d:
                return "dismissed"
            if "grant" in d:
                return "granted"
    except Exception as e:
        print(f"qwen-vl-max PPH 判断失败: {e}", file=sys.stderr)
    return ""


def parse_pph_decision(pdf_path):
    """判断 PPH 决定：返回 'dismissed' / 'granted' / ''（无法判断）。
    先读文字层（封面或文字版官文，命中 dismiss/grant 即返回）；读不到再 OCR 前几页。"""
    if not pdf_path or not os.path.exists(pdf_path):
        return ""
    text, _is_scanned = _pdf_to_text(pdf_path, max_pages=5)
    low = (text or "").lower()
    # 官文正文关键句 "the request and petition are dismissed/granted"；封面 "PPH Dismissed/Granted"
    if "dismiss" in low:
        return "dismissed"
    if "grant" in low:
        return "granted"
    return _ai_pph_decision_from_images(pdf_path, max_pages=3)


# Examiner Interview Summary 无需答复的关键句
_INTERVIEW_NO_ACTION_PHRASE = "it is not necessary for applicant"


def _ai_interview_no_action_from_images(pdf_path, max_pages=3):
    """扫描件降级：渲染前 N 页发 qwen-vl-max 判断是否含 'It is not necessary for applicant'。"""
    try:
        import fitz
    except ImportError:
        return False
    doc = fitz.open(pdf_path)
    images_b64 = []
    for i in range(min(max_pages, len(doc))):
        pix = doc[i].get_pixmap(dpi=200)
        images_b64.append(base64.b64encode(pix.tobytes("png")).decode("utf-8"))
    doc.close()
    if not images_b64:
        return False
    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    content = [{
        "type": "text",
        "text": ('This is a USPTO Examiner Interview Summary. Does it contain the statement '
                 '"It is not necessary for applicant to provide a separate record ...\" '
                 '(i.e. no separate reply is required)? '
                 'Return ONLY JSON: {"present": true} or {"present": false}.')
    }]
    for b64 in images_b64:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
    try:
        resp = client.chat.completions.create(
            model=QWEN_VL_MODEL, max_tokens=30,
            messages=[{"role": "user", "content": content}])
        m = re.search(r'\{.*?\}', resp.choices[0].message.content.strip(), re.DOTALL)
        if m:
            return bool(json.loads(m.group()).get("present"))
    except Exception as e:
        print(f"qwen-vl-max Interview 判断失败: {e}", file=sys.stderr)
    return False


def interview_no_action_needed(pdf_path):
    """Examiner Interview Summary：官文含 'It is not necessary for applicant' → 无需答复，返回 True（不立项）。
    先读文字层命中即 True；有文字但未命中 → False；无文字（扫描件）→ OCR 判定。
    文件不存在/无法判定 → False（默认仍立项，避免误跳过）。"""
    if not pdf_path or not os.path.exists(pdf_path):
        return False
    text, _is_scanned = _pdf_to_text(pdf_path, max_pages=5)
    low = (text or "").lower()
    if _INTERVIEW_NO_ACTION_PHRASE in low:
        return True
    if low.strip():
        return False   # 有文字层但未命中 → 仍立项
    return _ai_interview_no_action_from_images(pdf_path, max_pages=3)


def extract_us_deadline(pdf_path, mailing_date=None):
    """
    从 US 官文 PDF 提取答复期限。

    策略：正则 → DeepSeek文本 → qwen-vl-max图片

    Args:
        pdf_path: PDF 文件路径
        mailing_date: mailing date 字符串（YYYY-MM-DD 或 MM/DD/YYYY）

    Returns:
        dict: {months, deadline, mailing_date} 或 None
    """
    if not os.path.exists(pdf_path):
        print(f"PDF 文件不存在: {pdf_path}", file=sys.stderr)
        return None

    months = None

    # 第一步：提取文本
    text, is_scanned = _pdf_to_text(pdf_path, max_pages=5)

    if text.strip():
        # 第二步：正则匹配
        months = _regex_extract_months(text)
        if months:
            print(f"[正则] 提取到答复期限: {months} 个月", file=sys.stderr)

        # 第三步：正则失败，用 DeepSeek
        if not months:
            months = _ai_extract_months_from_text(text)
            if months:
                print(f"[DeepSeek] 提取到答复期限: {months} 个月", file=sys.stderr)

    # 第四步：扫描件，用 qwen-vl-max 图片识别
    if not months and is_scanned:
        print("PDF 为扫描件，使用图片识别...", file=sys.stderr)
        months = _ai_extract_months_from_images(pdf_path, max_pages=3)
        if months:
            print(f"[qwen-vl-max] 提取到答复期限: {months} 个月", file=sys.stderr)

    if not months:
        print("无法提取答复期限", file=sys.stderr)
        return None

    # 计算绝限日期
    deadline = ""
    final_mailing = mailing_date or ""
    if final_mailing:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
            try:
                dt = datetime.strptime(str(final_mailing).strip()[:10], fmt)
                deadline = _add_months(dt, months).strftime("%Y-%m-%d")
                final_mailing = dt.strftime("%Y-%m-%d")
                break
            except ValueError:
                continue

    return {
        "months": months,
        "deadline": deadline,
        "mailing_date": final_mailing,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 parse_us_pdf.py <PDF路径> [mailing_date]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    mailing = sys.argv[2] if len(sys.argv) > 2 else None
    result = extract_us_deadline(pdf_path, mailing_date=mailing)
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("解析失败")
        sys.exit(1)
