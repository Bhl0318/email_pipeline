"""net_clients —— 网络与服务调用客户端（基础通用层）。

- uspto.USPTOApplication  按申请号从 USPTO 官方 API 下官文
- patent_pdf.download_patent_pdf  按号从 FreePatentsOnline 下专利 PDF
"""
from .uspto import USPTOApplication, log_download
from .patent_pdf import download_patent_pdf

__all__ = ["USPTOApplication", "log_download", "download_patent_pdf"]
