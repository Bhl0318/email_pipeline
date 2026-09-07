"""doc_extract 用法示例：三级兜底文档抽取。

正则这级离线实跑（临时造一个带文本层的 PDF）；大模型/图片级需 key，只示范写法。

运行：python3 scripts/reusable/examples/doc_extract_demo.py
"""
import os
import re
import sys
import tempfile

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "business"))
from doc_extract import extract_from_pdf  # noqa: E402

_WORD = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "SIX": 6}


def us_months_regex(text):
    """从 US 官文正文抽答复月数：'THREE MONTHS' / '3 MONTHS'。命中返回 {'months': n}，否则 None。"""
    m = re.search(r"(\d+|ONE|TWO|THREE|FOUR|SIX)\s+MONTHS?", text, re.IGNORECASE)
    if not m:
        return None
    tok = m.group(1).upper()
    n = int(tok) if tok.isdigit() else _WORD.get(tok)
    return {"months": n} if n else None


def _make_text_pdf(path):
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "This action is made FINAL. A shortened statutory period "
                               "for reply is set to expire THREE MONTHS from the mailing date.")
    doc.save(path)
    doc.close()


if __name__ == "__main__":
    # 正则级（离线实跑）
    with tempfile.TemporaryDirectory() as d:
        pdf = os.path.join(d, "oa.pdf")
        _make_text_pdf(pdf)
        result = extract_from_pdf(pdf, regex=us_months_regex)
        print("正则级抽取:", result)          # -> {'months': 3}

    # 三级完整用法（大模型/图片级需 key，此处仅示范写法）
    print("\n完整调用写法（正则未命中→大模型读文本→扫描件转图片OCR）：")
    print('''
    extract_from_pdf(
        "oa.pdf",
        regex=us_months_regex,                                  # 一级：正则
        text_prompt='从下面官文提取答复期限月数，只输出 JSON：{"months": <int>}',  # 二级：大模型读文本
        image_prompt='这些官文页答复期限几个月？只输出 JSON：{"months": <int>}',    # 三级：扫描件图片OCR
    )
    # -> {"months": 3}
    ''')
