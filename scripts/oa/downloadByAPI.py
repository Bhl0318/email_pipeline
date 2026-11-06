"""兼容旧导入名；USPTO 下载实现统一使用公用客户端。"""

import os
import sys

_FOUNDATION_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "reusable", "foundation")
)
if _FOUNDATION_DIR not in sys.path:
    sys.path.insert(0, _FOUNDATION_DIR)

from net_clients.uspto import LOG_FILENAME, USPTOApplication, log_download  # noqa: E402,F401

__all__ = ["LOG_FILENAME", "USPTOApplication", "log_download"]
