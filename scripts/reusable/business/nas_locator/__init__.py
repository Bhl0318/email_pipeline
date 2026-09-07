"""nas_locator —— NAS 申请文件定位（业务支撑层）。

按案号+地区在 NAS 目录树里定位「递交文件」目录、取说明书 docx。
NAS 路径规则作 config、客户简称查库注入为 shortname_lookup。
"""
from .locator import resolve_app_dir, find_application_file, DEFAULT_NAS_CONFIG

__all__ = ["resolve_app_dir", "find_application_file", "DEFAULT_NAS_CONFIG"]
