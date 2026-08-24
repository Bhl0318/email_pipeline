#!/usr/bin/env python3
"""OA 白名单 → Confluence：把 atw oa_assign_whitelist 全量回渲染成表格，写回指定 Wiki 页。

由维护页「同步到 Wiki」按钮触发（report/oa_whitelist.py 的 /api/whitelist/sync-wiki）。
真源是 atw；该 Wiki 页是给人看的镜像，每次同步整页重渲染（人请勿直接在 Wiki 上改）。
"""
import html
import sys

WHITELIST_WIKI_PAGE_ID = "241276196"   # 目标 Wiki 页

# 实质：列 = 档位×领域；行 = 梯队
SUB_GRADES = [("普及", "普及档（授权为目标，含普及档国内OA+海外OA）"),
              ("标准", "标准档（保护目的-CN）"), ("海外", "海外OA（保护目的）")]
SUB_FIELDS = ["通用", "结构", "生化"]
SUB_TIERS = ["QC", "梯队1", "梯队2", "梯队3"]
# 形式：列 = (档位, 领域, 表头)
FORM_COLS = [("CN", "通用/结构/生化", "CN形式（一般没分配了）·通用/结构/生化"),
             ("海外", "通用/结构", "海外OA·通用/结构"), ("海外", "生化", "海外OA·生化")]
FORM_TIERS = ["梯队1", "梯队2", "梯队3"]


def _esc(s):
    return html.escape(str(s or ""))


def _cell(rows, biz, tier, grade, field):
    items = [r for r in rows if r.get("biz_type") == biz and r.get("tier") == tier
             and r.get("grade") == grade and r.get("field") == field]
    if not items:
        return "<td><br/></td>"
    lis = []
    for r in items:
        name = _esc(r.get("name_raw") or r.get("username_zn"))
        flag = (r.get("flag") or "").strip()
        if flag == "blue":
            name = f'<span style="color: rgb(0,0,255);">{name}</span>'
        elif flag == "red":
            name = f'<span style="color: rgb(255,0,0);">{name}</span>'
        note = r.get("note")
        note_html = f' <span style="color: rgb(107,114,128);">（{_esc(note)}）</span>' if note else ""
        lis.append(f"<li>{name}{note_html}</li>")
    return "<td><ul>" + "".join(lis) + "</ul></td>"


def render_storage(rows, tier_desc):
    """rows: oa_assign_whitelist 全量；tier_desc: {(biz,tier): description}。返回 Confluence storage HTML。"""
    def desc(biz, tier):
        return _esc(tier_desc.get((biz, tier), ""))

    h = ['<p><strong>OA 分配白名单</strong>（由系统按 atw <code>oa_assign_whitelist</code> 自动生成，'
         '请通过维护页增删，勿直接在本页编辑）</p>']

    # 一、实质
    h.append("<h2>OA 实质部分</h2>")
    h.append('<table><tbody>')
    h.append("<tr><th>梯队</th><th>梯队说明</th>"
             + "".join(f'<th colspan="3">{_esc(t)}</th>' for _, t in SUB_GRADES) + "</tr>")
    h.append("<tr><th></th><th></th>"
             + "".join("".join(f"<th>{f}</th>" for f in SUB_FIELDS) for _ in SUB_GRADES) + "</tr>")
    for tier in SUB_TIERS:
        h.append(f"<tr><td>{_esc(tier)}</td><td>{desc('OA实质', tier)}</td>"
                 + "".join(_cell(rows, "OA实质", tier, g, f) for g, _ in SUB_GRADES for f in SUB_FIELDS)
                 + "</tr>")
    h.append("</tbody></table>")

    # 二、形式
    h.append("<h2>OA 形式部分</h2>")
    h.append('<table><tbody>')
    h.append("<tr><th>梯队</th><th>梯队说明</th>"
             + "".join(f"<th>{_esc(c[2])}</th>" for c in FORM_COLS) + "</tr>")
    for tier in FORM_TIERS:
        h.append(f"<tr><td>{_esc(tier)}</td><td>{desc('OA形式', tier)}</td>"
                 + "".join(_cell(rows, "OA形式", tier, c[0], c[1]) for c in FORM_COLS)
                 + "</tr>")
    h.append("</tbody></table>")
    h.append("<p>备注：目前 EP 答复案件都需要安排形式答复（除非本案负责人提出由于期限较近直接处理之外）。</p>")
    return "".join(h)


def sync_to_wiki(page_id=None, execute=None):
    """从 atw 读白名单 → 回渲染 → 写回 Wiki 页。返回 {ok, msg}。"""
    page_id = page_id or WHITELIST_WIKI_PAGE_ID
    try:
        from oa_whitelist_store import list_all
        rows = list_all(execute=execute)
        # 梯队说明
        ex = execute
        if ex is None:
            from db_query import execute as ex
        td = {}
        try:
            for r in (ex("SELECT biz_type, tier, description FROM oa_assign_tier_desc") or []):
                td[(r.get("biz_type"), r.get("tier"))] = r.get("description")
        except Exception:
            pass
        content = render_storage(rows, td)
        from oainfo_cli import WikiClient
        wiki = WikiClient()
        page = wiki.get_page_by_id(page_id)
        if not page:
            return {"ok": False, "msg": f"取 Wiki 页失败(pageId={page_id})"}
        code = wiki.update_page(page_id, page["title"], content, page["version"])
        ok = code == 200
        return {"ok": ok, "msg": f"{'已同步' if ok else '写入失败'} {len(rows)} 条 → 《{page['title']}》(HTTP {code})"}
    except Exception as e:
        print(f"[oa_whitelist_wiki] 同步失败: {e}", file=sys.stderr)
        return {"ok": False, "msg": f"同步异常: {e}"}


if __name__ == "__main__":
    print(sync_to_wiki())
