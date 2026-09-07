"""doc_generator —— 文档生成器骨架（业务支撑层）。

"字段映射 ↔ 生成器分离"的三步骨架：map_fields（映射）、select_template（选模板）、
build_documents（编排一组生成器、统一结果契约、逐个兜底、汇总）。
"""
from .skeleton import map_fields, select_template, build_documents

__all__ = ["map_fields", "select_template", "build_documents"]
