"""文档文本抽取（可复用）。

- pdf_text        抽自 oa/parse_us_refs.py 的 _pdf_to_text（PDF 文本层，PyMuPDF）
- docx_text       抽自 oa/oa_report_ai.py 的 _docx_text（python-docx，失败退解压 XML）
- split_spec      抽自 oa/oa_report_ai.py 的 _split_spec（说明书切分为 说明/权要）
- pick_latest_docx 抽自 oa/oa_report_ai.py 的 _pick_latest_docx（按关键词取最新 docx）

逻辑不变，零业务耦合。扫描件 OCR 不在此（耦合大模型）——用 llm_client.vision 组合。

依赖：PyMuPDF (fitz)、python-docx（均惰性导入）。
"""
import glob
import os
import re
import sys


def pdf_text(pdf_path, max_pages=6):
    """PyMuPDF 抽 PDF 文本层（前 N 页）。无文本层（扫描件）返回 ""。

    输入：pdf_path、max_pages → 输出：str
    注：扫描件需 OCR 时，另用 llm_client.vision 逐页图片识别。
    """
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for i in range(min(max_pages, len(doc))):
            pt = doc[i].get_text()
            if pt.strip():
                text += pt + "\n"
        doc.close()
        return text
    except Exception as e:
        print(f"[doc_text] PDF 读取失败 {pdf_path}: {e}", file=sys.stderr)
        return ""


def docx_text(path):
    """docx → 纯文本。优先 python-docx；失败退回裸解压 document.xml。缺文件返回 ""。

    输入：path → 输出：str
    """
    if not path or not os.path.isfile(path):
        return ""
    try:
        import docx
        d = docx.Document(path)
        return "\n".join(p.text for p in d.paragraphs if p.text.strip())
    except Exception:
        try:
            import zipfile
            z = zipfile.ZipFile(path)
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml)).strip()
        except Exception as e:
            print(f"[doc_text] docx 读取失败 {path}: {e}", file=sys.stderr)
            return ""


_CLAIMS_START_RE = re.compile(
    r"(WHAT\s+IS\s+CLAIMED\s+IS|^\s*CLAIMS\s*$|We\s+claim|I\s+claim|权\s*利\s*要\s*求\s*书?)",
    re.IGNORECASE | re.MULTILINE)
_CLAIMS_END_RE = re.compile(
    r"(^\s*ABSTRACT\s*$|说\s*明\s*书\s*摘\s*要|^\s*摘\s*要\s*$)",
    re.IGNORECASE | re.MULTILINE)


def split_spec(spec_text):
    """把说明书全文切成 (说明部分, 权利要求部分)。

    权要以「WHAT IS CLAIMED IS / CLAIMS / We claim / 权利要求」起，到「ABSTRACT / 摘要」止。
    切不出权要时 claims 返回 ""、description 返回全文。
    输入：spec_text(str) → 输出：(description, claims)
    """
    text = spec_text or ""
    ms = _CLAIMS_START_RE.search(text)
    if not ms:
        return text, ""
    desc = text[:ms.start()].strip()
    rest = text[ms.start():]
    me = _CLAIMS_END_RE.search(rest, 1)  # 从权要标题之后再找摘要
    claims = (rest[:me.start()] if me else rest).strip()
    return desc, claims


def pick_latest_docx(dirpath, keywords=None):
    """取目录下最新的 .docx（可选文件名含任一关键词，大小写不敏感）。

    先在本层找；本层无匹配时递归子目录。返回路径或 None。
    输入：dirpath、keywords(list[str]|None) → 输出：str|None
    """
    if not dirpath or not os.path.isdir(dirpath):
        return None
    kws = [k.lower() for k in keywords] if keywords else None

    def _match(pattern):
        fs = [f for f in glob.glob(pattern, recursive=True)
              if os.path.isfile(f) and f.lower().endswith(".docx")]
        if kws:
            fs = [f for f in fs if any(k in os.path.basename(f).lower() for k in kws)]
        return fs

    files = _match(os.path.join(dirpath, "*.docx"))
    if not files:
        files = _match(os.path.join(dirpath, "**", "*.docx"))
    if not files:
        return None
    return max(set(files), key=os.path.getmtime)
