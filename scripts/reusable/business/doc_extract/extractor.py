"""分级文档抽取组件（业务支撑层 · 数据处理组件）。

范式抽象自 oa/parse_us_pdf.py、oa/parse_cn_pdf.py 的"正则 → 大模型文本 → 图片OCR"三级兜底：
把文档格式相关的正则与提示词交给调用方，内部负责取文本、调模型、扫描件转图片并按序兜底。

复用下层模块：doc_utils.pdf_text（取文本层）、llm_client.chat/vision（调大模型）。
依赖：PyMuPDF (fitz，用于扫描件渲染)。
"""
import base64
import os
import sys

# 让本组件能找到同库的 foundation / integration 模块
_LIB = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _d in ("foundation", "integration"):
    _p = os.path.join(_LIB, _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from doc_utils import pdf_text  # noqa: E402
import llm_client  # noqa: E402


def _pdf_pages_to_b64(pdf_path, max_pages=3, dpi=200):
    """把 PDF 前 N 页渲染成 PNG 的 base64 列表（扫描件走图片 OCR 用）。失败返回 []。"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        out = []
        for i in range(min(max_pages, len(doc))):
            pix = doc[i].get_pixmap(dpi=dpi)
            out.append(base64.b64encode(pix.tobytes("png")).decode("utf-8"))
        doc.close()
        return out
    except Exception as e:
        print(f"[doc_extract] 渲染图片失败 {pdf_path}: {e}", file=sys.stderr)
        return []


def extract_from_pdf(pdf_path, *, regex=None, text_prompt=None, image_prompt=None,
                     max_pages=6, text_profile="deepseek", image_profile="qwen",
                     extract="json"):
    """从 PDF 抽结构化数据，正则 → 大模型文本 → 图片OCR 三级自动兜底。

    调用方按自己的文档提供 regex / text_prompt / image_prompt（都可选，只给哪级就走哪级）。
    有文本层：先试 regex，失败再用大模型读文本；无文本层（扫描件）：渲染成图片用多模态模型。

    输入：
      pdf_path      PDF 路径（必填）
      regex         可选，callable(text)->结果|None，命中即返回
      text_prompt   可选，str；正则未命中时把它+正文发给大模型（llm_client.chat）
      image_prompt  可选，str；扫描件无文本层时发图片给多模态模型（llm_client.vision）
      max_pages     可选，取文本/渲染的最大页数（默认 6）
      text_profile / image_profile  可选，大模型 profile（默认 deepseek / qwen）
      extract       可选，"json"（默认，自动解析）｜"text"
    返回：结构化结果（dict/list 或 str），三级都没结果→None。
    """
    if not os.path.exists(pdf_path):
        print(f"[doc_extract] 文件不存在: {pdf_path}", file=sys.stderr)
        return None

    text = pdf_text(pdf_path, max_pages=max_pages)
    if text.strip():
        if regex:
            r = regex(text)
            if r:
                return r
        if text_prompt:
            r = llm_client.chat(f"{text_prompt}\n\n{text}", profile=text_profile, extract=extract)
            if r:
                return r
    elif image_prompt:  # 无文本层（扫描件）
        images = _pdf_pages_to_b64(pdf_path, max_pages=min(max_pages, 3))
        if images:
            r = llm_client.vision(images, image_prompt, profile=image_profile, extract=extract)
            if r:
                return r
    return None
