"""doc_utils —— 可复用文档处理工具集。

抽自 report/submission/common.py、run_uspto_upload.py、oa/oa_report_ai.py、oa/parse_us_refs.py，
逻辑不变，零业务耦合。目前为纯新增资产，未迁移原调用方。

子模块：
  pdf_form   fill_pdf_form           本地 AcroForm 表单填充（PyMuPDF）
  pdfa       gs_bin/to_pdfa/others_to_pdfa   PDF→PDF/A-2b（Ghostscript）
  doc_text   pdf_text/docx_text/split_spec/pick_latest_docx   文档→文本 + 说明书切分

不含：flatten_pdf（耦合 pdfRest 云）、OCR（耦合大模型，用 llm_client.vision 组合）。

用法：
    from doc_utils import fill_pdf_form, to_pdfa, docx_text, pdf_text, split_spec
"""
from . import pdf_form, pdfa, doc_text
from .pdf_form import fill_pdf_form
from .pdfa import gs_bin, to_pdfa, others_to_pdfa
from .doc_text import pdf_text, docx_text, split_spec, pick_latest_docx

__all__ = [
    "pdf_form", "pdfa", "doc_text",
    "fill_pdf_form",
    "gs_bin", "to_pdfa", "others_to_pdfa",
    "pdf_text", "docx_text", "split_spec", "pick_latest_docx",
]
