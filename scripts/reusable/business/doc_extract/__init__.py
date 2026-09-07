"""doc_extract —— 分级文档抽取组件（业务支撑层 · 数据处理组件）。

一个入口 extract_from_pdf：给 PDF + 你自己文档的正则/提示词，
按"正则 → 大模型文本 → 图片OCR"三级自动兜底抽结构化数据。
"""
from .extractor import extract_from_pdf

__all__ = ["extract_from_pdf"]
