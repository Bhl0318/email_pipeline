"""doc_generator 用法示例（离线）：字段映射 → 选模板 → 编排生成器（含兜底）。

运行：python3 scripts/reusable/examples/doc_generator_demo.py
"""
import os
import sys
import tempfile

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "business"))
from doc_generator import map_fields, select_template, build_documents  # noqa: E402

# ① 字段映射：原始 fields_json → 生成器要的结构
RAW = {"case_volume": "64504-H006US00", "sm": "utl",
       "inv_first": "Wei", "inv_last": "LIN"}
SPEC = {
    "case_no": "case_volume",                                   # 直接取源键
    "subject": "sm",
    "inventor": lambda r: f'{r["inv_first"]} {r["inv_last"]}',  # 自定义派生
}

# ② 模板选择：按 subject 挑模板
TEMPLATES = {"utl": "Transmittal.pdf", "design": "Design-Transmittal.pdf", "371": "371-Transmittal.pdf"}


# ③ 两个玩具生成器（真实场景里用 doc_utils.fill_pdf_form / python-docx 填模板）
def gen_poa(data, output_dir=None):
    return {"file_path": f"{output_dir}/POA.pdf", "file_name": "POA.pdf", "type": "POA"}


def gen_transmittal(data, output_dir=None):
    tpl = select_template(TEMPLATES, data["subject"], default="Transmittal.pdf")
    return {"file_path": f"{output_dir}/{tpl}", "file_name": tpl, "type": "Transmittal",
            "warnings": ["371 费用项待补"] if data["subject"] == "371" else []}


def gen_broken(data, **kw):
    raise ValueError("模板缺失")


if __name__ == "__main__":
    case_info = map_fields(RAW, SPEC)
    print("① 映射结果:", case_info)
    # -> {'case_no': '64504-H006US00', 'subject': 'utl', 'inventor': 'Wei LIN'}

    print("② 选模板  :", select_template(TEMPLATES, case_info["subject"], default="Transmittal.pdf"))
    # -> 'Transmittal.pdf'

    with tempfile.TemporaryDirectory() as d:
        result = build_documents(case_info, [
            (gen_poa, {"output_dir": d}),
            (gen_transmittal, {"output_dir": d}),
            (gen_broken, {}),                       # 会抛异常 → 记 warning，不中断
        ])
    print("③ 生成文档:", [x["type"] for x in result["documents"]])
    # -> ['POA', 'Transmittal']
    print("   warnings:", result["warnings"])
    # -> ['gen_broken 生成失败: 模板缺失']
