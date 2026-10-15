#!/usr/bin/env python3
"""官文正文（Word/PDF）→ OA信息记录表页的子页（Confluence storage 格式）。

自包含于 email_pipeline：复用 oainfo_cli.WikiClient（同一 Wiki），
不依赖外部 DS/爬取专利生成wiki/word2wiki.py。

- 按扩展名自动选：`.docx` 用 python-docx，`.pdf` 用 PyMuPDF（有 Word 用 Word、没 Word 用 PDF）。
- 正文段落可带【0001】编号（便于按段引用），并在页顶标注编号与原文不一定一致。
- 父页为该案 OA信息记录表页，按 pageId 定位；子页标题 = 文件名（去扩展名）。
- 同名子页已存在则更新（不重复建页）。
"""
import os
import sys

# qwen-vl（扫描/图片型 PDF 无文本层时 OCR，复用 parse_cn_pdf 同一密钥）
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "REDACTED_API_KEY")
QWEN_VL_MODEL = "qwen-vl-max"
OCR_MAX_PAGES = 10   # 扫描件 OCR 页数上限（官文一般几页；防超长/超费）


def _esc(s):
    """移除 XML 1.0 不允许的控制字符，再做 HTML 转义。"""
    s = "".join(ch for ch in s if ch in "\t\n\r" or
                0x20 <= ord(ch) <= 0xD7FF or
                0xE000 <= ord(ch) <= 0xFFFD or
                0x10000 <= ord(ch) <= 0x10FFFF)
    return (s.replace('&', '&amp;').replace('"', '&quot;')
             .replace("'", '&#x27;').replace('<', '&lt;').replace('>', '&gt;'))


def _wrap(body, add_num):
    head = ("<div class='cell normal' data-type='normal'>"
            "<p style='color:red'>请注意：本页中的段落编号与原始文本不一定一致，"
            "如需引用请以原始文本为准。</p>") if add_num else \
           "<div class='cell normal' data-type='normal'>"
    return head + body + "</div>"


# ── Word(.docx) ──
def _docx_paragraphs_html(doc, add_num):
    out, n = [], 0
    for p in doc.paragraphs:
        t = _esc(p.text)
        if not t:
            continue
        n += 1
        out.append(f"<p>【{n:04d}】{t}</p>" if add_num else f"<p>{t}</p>")
    return "".join(out)


def _docx_tables_html(doc):
    out = []
    for tb in doc.tables:
        h = '<table class="confluenceTable"><tbody>'
        for row in tb.rows:
            h += '<tr>'
            for cell in row.cells:
                h += f"<td class='confluenceTd'>{_esc(cell.text)}</td>"
            h += '</tr>'
        h += '</tbody></table>'
        out.append(h)
    return "".join(out)


def docx_to_storage(docx_path, add_num=True):
    """把 .docx 转成 Confluence storage HTML（段落 + 表格）。"""
    from docx import Document
    doc = Document(docx_path)
    return _wrap(_docx_paragraphs_html(doc, add_num) + _docx_tables_html(doc), add_num)


# ── PDF(.pdf) ──
def _paras_to_html(paras, add_num):
    out = []
    for i, t in enumerate(paras, 1):
        t = _esc(t)
        out.append(f"<p>【{i:04d}】{t}</p>" if add_num else f"<p>{t}</p>")
    return "".join(out)


def _pdf_text_paragraphs(pdf_path):
    """PyMuPDF 抽文本层，返回段落列表；无文本层（扫描/图片型 PDF）返回 []。"""
    import fitz
    doc = fitz.open(pdf_path)
    paras = []
    for page in doc:
        for block in page.get_text("blocks"):
            # block: (x0,y0,x1,y1, text, block_no, block_type)；block_type=1 为图片
            if len(block) > 6 and block[6] != 0:
                continue
            t = " ".join((block[4] or "").split())   # 段内换行并成一段
            if t:
                paras.append(t)
    doc.close()
    return paras


def _ocr_pdf_paragraphs(pdf_path, max_pages=OCR_MAX_PAGES):
    """扫描/图片型 PDF → OCR 段落列表。先用 mistral-ocr 服务(整份→md)，失败回退 qwen-vl 逐页。空返回 []。"""
    try:
        from mistral_ocr import pdf_to_markdown
        md = pdf_to_markdown(pdf_path)
        if md:
            return [ln.strip() for ln in md.split("\n") if ln.strip()]
    except Exception as e:
        print(f"[官文OCR] mistral-ocr 失败，回退 qwen-vl: {e}", file=sys.stderr)
    try:
        import base64
        import fitz
        from openai import OpenAI
    except Exception as e:
        print(f"[官文OCR] 依赖缺失，跳过 OCR: {e}", file=sys.stderr)
        return []
    doc = fitz.open(pdf_path)
    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    paras = []
    for i in range(min(max_pages, len(doc))):
        pix = doc[i].get_pixmap(dpi=200)
        b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
        content = [
            {"type": "text", "text": (
                "这是专利官方文件的一页扫描件。请按阅读顺序输出该页的纯文本，"
                "保留自然段落、逐段换行；不要额外解释、不要 markdown、不要页码页眉页脚。")},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ]
        try:
            resp = client.chat.completions.create(
                model=QWEN_VL_MODEL, max_tokens=4000,
                messages=[{"role": "user", "content": content}])
            txt = (resp.choices[0].message.content or "").strip()
        except Exception as e:
            print(f"[官文OCR] 第{i+1}页失败: {e}", file=sys.stderr)
            txt = ""
        for line in txt.split("\n"):
            line = line.strip()
            if line:
                paras.append(line)
    doc.close()
    return paras


def pdf_to_storage(pdf_path, add_num=True, ocr_max_pages=OCR_MAX_PAGES):
    """把 .pdf 正文转成 storage HTML（段落级编号）。
    有文本层走 PyMuPDF；无文本层（扫描件）走 qwen-vl OCR；都拿不到返回 None（供上层不建空页）。"""
    paras = _pdf_text_paragraphs(pdf_path)
    if not paras:
        paras = _ocr_pdf_paragraphs(pdf_path, max_pages=ocr_max_pages)
        if paras:
            print(f"[官文OCR] {os.path.basename(pdf_path)} OCR 出 {len(paras)} 段", file=sys.stderr)
    if not paras:
        return None
    return _wrap(_paras_to_html(paras, add_num), add_num)


def doc_to_storage(path, add_num=True):
    """按扩展名把官文转成 storage HTML：.docx→python-docx，.pdf→PyMuPDF(+扫描件 OCR)。
    PDF 无可提取正文时返回 None。"""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return docx_to_storage(path, add_num)
    if ext == ".pdf":
        return pdf_to_storage(path, add_num)
    raise ValueError(f"不支持的官文格式（仅 .docx/.pdf）: {path}")


def _content_pieces(path):
    """抽一次正文，返回 (paras, tables_html)——供渲染有序号/无序号两版复用（避免扫描件 OCR 跑两遍）。
    .docx→段落原文列表 + 表格HTML；.pdf→段落列表(文本层或 OCR) + ''；PDF 无正文→([], '')。"""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        from docx import Document
        doc = Document(path)
        paras = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        return paras, _docx_tables_html(doc)
    if ext == ".pdf":
        paras = _pdf_text_paragraphs(path)
        if not paras:
            paras = _ocr_pdf_paragraphs(path)
            if paras:
                print(f"[官文OCR] {os.path.basename(path)} OCR 出 {len(paras)} 段", file=sys.stderr)
        return paras, ""
    raise ValueError(f"不支持的官文格式（仅 .docx/.pdf）: {path}")


def _render_storage(paras, tables_html, add_num):
    return _wrap(_paras_to_html(paras, add_num) + (tables_html or ""), add_num)


def _put_subpage(wiki, parent, base_title, content, add_num):
    """建一个子页（有序号版=base_title；无序号版=base_title【无序号版】）；同名已存在则更新。"""
    title = base_title if add_num else base_title + "【无序号版】"
    status = wiki.create_child_page(title, content, parent["space_key"], parent["id"])
    if status != 200:
        # 同名子页已存在（Confluence 建重名返回 400）→ 按标题回查并更新
        existing = wiki.get_page(title)
        if existing:
            status = wiki.update_page(existing["id"], title, content, existing["version"])
    return status, title


def upload_doc_subpages(wiki, parent_page_id, doc_path, versions=(True, False), base_title=None):
    """把一份官文（Word/PDF）正文转成 parent_page_id 页下的子页，默认建**有序号 + 无序号两版**。
    正文只抽一次（扫描件只 OCR 一次），渲染两版分别建/更新。

    base_title：指定子页标题（去扩展名版），用于统一命名（如 EP 传 `发文日-类型-案号`）；
    不传则沿用官文文件名（US 下载名本就是 `发文日-描述-案号`、CN 附件名已规范）。

    Returns:
        list[(status_code, page_title)]；父页找不到返回 [(404, "")]；无可提取正文返回 []（不建空页）。
    """
    parent = wiki.get_page_by_id(parent_page_id)
    if not parent:
        return [(404, "")]
    paras, tables_html = _content_pieces(doc_path)
    if not paras and not tables_html:
        print(f"[官文转Wiki] 无可提取正文，跳过建页: {os.path.basename(doc_path)}", file=sys.stderr)
        return []
    base = (base_title or "").strip() or os.path.splitext(os.path.basename(doc_path))[0]
    out = []
    for add_num in versions:
        content = _render_storage(paras, tables_html, add_num)
        out.append(_put_subpage(wiki, parent, base, content, add_num))
    return out


def upload_doc_subpage(wiki, parent_page_id, doc_path, add_num=True):
    """单版本入口（向后兼容）：只建一个子页（默认有序号版）。"""
    res = upload_doc_subpages(wiki, parent_page_id, doc_path, versions=(add_num,))
    return res[0] if res else (0, os.path.splitext(os.path.basename(doc_path))[0])


# 向后兼容别名（原只支持 Word）
upload_word_subpage = upload_doc_subpage


if __name__ == "__main__":
    from oainfo_cli import WikiClient
    if len(sys.argv) < 3:
        print("用法: python3 word_to_wiki.py <官文.docx|官文.pdf> <parent_page_id> [num|nonum]")
        sys.exit(1)
    # 默认建两版；给 num 只建有序号、nonum 只建无序号
    _arg = sys.argv[3] if len(sys.argv) > 3 else ""
    _versions = (True,) if _arg == "num" else (False,) if _arg == "nonum" else (True, False)
    for st, tt in upload_doc_subpages(WikiClient(), sys.argv[2], sys.argv[1], versions=_versions):
        print(f"HTTP {st} 子页: {tt}")
