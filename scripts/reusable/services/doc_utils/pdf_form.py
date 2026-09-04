"""PDF AcroForm 表单填充（可复用，本地）。

抽自 report/submission/common.py 的 fill_pdf_form，逻辑不变。零业务耦合。
不含 flatten_pdf（那个耦合 pdfRest 云服务与模块级凭据，不属通用工具）。

依赖：PyMuPDF (fitz)。
"""
from pathlib import Path

import fitz


def fill_pdf_form(template_pdf, output_pdf, field_updates: dict) -> None:
    """填写 PDF AcroForm 表单字段并另存。

    checkbox(field_type==2) 命中即勾选 'Yes'，其余按字符串写入；模板里没有的字段名忽略。

    输入：
      template_pdf  模板 PDF 路径（须存在，否则抛 FileNotFoundError）
      output_pdf    输出 PDF 路径
      field_updates {字段名: 值}
    输出：无（副作用：写出 output_pdf）
    示例：fill_pdf_form("POA.pdf", "out.pdf", {"applicant_name": "张三", "checkbox_a": True})
    """
    template_pdf = Path(template_pdf)
    if not template_pdf.is_file():
        raise FileNotFoundError(f"PDF 模板不存在: {template_pdf}")
    doc = fitz.open(str(template_pdf))
    doc.need_appearances(False)
    for page in doc:
        widgets = page.widgets()
        if not widgets:
            continue
        for field in widgets:
            if field.field_name in field_updates:
                if field.field_type == 2:  # checkbox
                    field.field_value = "Yes"
                else:
                    field.field_value = str(field_updates[field.field_name])
                field.update()
    doc.save(str(output_pdf))
    doc.close()
