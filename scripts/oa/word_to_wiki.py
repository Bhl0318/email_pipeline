#!/usr/bin/env python3
"""US 官文 Word 版 → OA信息记录表页的子页（Confluence storage 格式）。

自包含于 email_pipeline：复用 oainfo_cli.WikiClient（同一 Wiki），
不依赖外部 DS/爬取专利生成wiki/word2wiki.py，也不引 pdfminer（此处只处理 Word）。

- 仅处理 .docx（python-docx）；父页为该案 OA信息记录表页，按 pageId 定位。
- 正文段落可带【0001】编号（便于按段引用），并在页顶标注编号与原文不一定一致。
- 子页标题 = Word 文件名（去扩展名）；同名已存在则更新（不重复建页）。
"""
import os
from docx import Document


def _esc(s):
    """HTML 转义（与原 word2wiki 一致：& 必须先转）。"""
    return (s.replace('&', '&amp;').replace('"', '&quot;')
             .replace("'", '&#x27;').replace('<', '&lt;').replace('>', '&gt;'))


def _paragraphs_html(doc, add_num):
    out, n = [], 0
    for p in doc.paragraphs:
        t = _esc(p.text)
        if not t:
            continue
        n += 1
        out.append(f"<p>【{n:04d}】{t}</p>" if add_num else f"<p>{t}</p>")
    return "".join(out)


def _tables_html(doc):
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
    doc = Document(docx_path)
    head = ("<div class='cell normal' data-type='normal'>"
            "<p style='color:red'>请注意：本页中的段落编号与原始文本不一定一致，"
            "如需引用请以原始文本为准。</p>") if add_num else \
           "<div class='cell normal' data-type='normal'>"
    return head + _paragraphs_html(doc, add_num) + _tables_html(doc) + "</div>"


def upload_word_subpage(wiki, parent_page_id, docx_path, add_num=True):
    """把一份 Word 官文正文转成 parent_page_id 页下的子页（已存在则更新）。

    Args:
        wiki: oainfo_cli.WikiClient 实例
        parent_page_id: 父页（案号-OA信息记录表）的 pageId
        docx_path: 本地 .docx 路径
        add_num: 段落是否加【0001】编号

    Returns:
        (status_code, page_title)；父页找不到返回 (404, "")。
    """
    parent = wiki.get_page_by_id(parent_page_id)
    if not parent:
        return 404, ""
    title = os.path.splitext(os.path.basename(docx_path))[0]
    if not add_num:
        title += "【无序号版】"
    content = docx_to_storage(docx_path, add_num)
    status = wiki.create_child_page(title, content, parent["space_key"], parent_page_id)
    if status != 200:
        # 同名子页已存在（Confluence 建重名返回 400）→ 按标题回查并更新
        existing = wiki.get_page(title)
        if existing:
            status = wiki.update_page(existing["id"], title, content, existing["version"])
    return status, title


if __name__ == "__main__":
    import sys
    from oainfo_cli import WikiClient
    if len(sys.argv) < 3:
        print("用法: python3 word_to_wiki.py <docx_path> <parent_page_id> [nonum]")
        sys.exit(1)
    _add_num = not (len(sys.argv) > 3 and sys.argv[3] == "nonum")
    st, tt = upload_word_subpage(WikiClient(), sys.argv[2], sys.argv[1], add_num=_add_num)
    print(f"HTTP {st} 子页: {tt}")
