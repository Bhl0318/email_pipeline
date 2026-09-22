#!/usr/bin/env python3
"""OA 分配「只读分享页」静态化：提交/分享时把内容渲染成一份自包含 HTML 写死到磁盘，
后续打开直接返回该文件（零查库、零 API、不依赖 CDN），供 report_server 的 /oa-assign/share 路由用。

- 报告 markdown 用 python-markdown 服务端渲染成 HTML 直接嵌入（不再靠前端 marked.js）。
- 布局复刻 web/assign.html 的 shareView：单案=仅中栏；批量=左栏案件列表(原生 JS 切换)+中栏，标批次时间。
- 样式内联（.md-body 与 assign.html 保持一致），整份文件无外链，外部收件人无网也能看。

用法：
  build_share_html(cases, shared_at="2026-09-22 14:30", batch=True) -> str(HTML)
  cases = [{"oaid","caseNo","oaSeq","reportMd","submit":{responder,qc,aqc,postscript,reason,submitted_at}}]
"""

_CSS = """
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;background:#f5f7fa;color:#303133}
.pas-header{height:44px;display:flex;align-items:center;padding:0 18px;background:#1f2d3d;color:#fff;flex-shrink:0}
.pas-header__brand{font-size:14px;font-weight:600}
.wrap{display:flex;height:calc(100vh - 44px);overflow:hidden}
.case-list{width:260px;flex-shrink:0;border-right:1px solid #ebeef5;background:#fff;display:flex;flex-direction:column}
.case-list__hd{padding:10px 12px;background:#eef4ff;border-bottom:1px solid #dbe6ff;font-size:12px;color:#2b5aa0;line-height:1.7}
.case-list__body{flex:1;overflow-y:auto}
.case-item{padding:10px 12px;border-bottom:1px solid #f5f5f5;cursor:pointer;font-size:13px;color:#303133}
.case-item:hover{background:#f7f9fc}
.case-item--active{background:#eef4ff;color:#2b5aa0;font-weight:600}
.oa-badge{font-size:11px;color:#2563eb;background:#eff6ff;border:1px solid #dbeafe;border-radius:4px;padding:0 5px;margin-left:4px}
.center{flex:1;overflow-y:auto;padding:16px 0}
.card{max-width:860px;margin:0 auto;background:#fff;border:1px solid #ebeef5;border-radius:6px;padding:20px 26px}
.card__title{font-size:16px;font-weight:700;color:#262626;margin-bottom:4px}
.ppl{background:#f0f9eb;border:1px solid #e1f3d8;border-radius:5px;padding:10px 14px;margin:12px 0;font-size:13px;color:#303133;line-height:1.9}
.ppl .muted{color:#8c8c8c;font-size:12px;margin-top:2px}
.case-panel{display:none}
.case-panel--active{display:block}
.md-body{font-size:13px;color:#303133;line-height:1.8}
.md-body h1,.md-body h2{font-size:14px;font-weight:700;color:#262626;margin:18px 0 8px;padding-bottom:6px;border-bottom:1px solid #f0f0f0}
.md-body h2:first-child,.md-body h1:first-child{margin-top:0}
.md-body h3{font-size:13px;font-weight:700;color:#262626;margin:14px 0 6px}
.md-body p{margin:0 0 8px}
.md-body table{width:100%;border-collapse:collapse;font-size:12px;margin-bottom:12px}
.md-body th{background:#f7f9fc;padding:5px 10px;font-weight:600;color:#595959;border:1px solid #e4e7ed;text-align:left}
.md-body td{padding:5px 10px;border:1px solid #e4e7ed;color:#303133;vertical-align:top}
.md-body tr:nth-child(even) td{background:#fafbfc}
.md-body ul,.md-body ol{padding-left:20px;margin:0 0 10px}
.md-body li{margin-bottom:4px}
.md-body strong{font-weight:600;color:#262626}
.md-body blockquote{margin:0 0 10px;padding:6px 12px;background:#fff7e6;border-left:3px solid #ffd591;color:#8c6d1f}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-thumb{background:#dcdfe6;border-radius:3px}
"""


def _esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _md_to_html(md):
    """报告 markdown → HTML。python-markdown 缺失时降级为 <pre> 纯文本（不崩，保内容）。"""
    md = md or ""
    try:
        import markdown
        return markdown.markdown(
            md, extensions=["tables", "fenced_code", "sane_lists", "nl2br"])
    except Exception:
        return "<pre style='white-space:pre-wrap;font:inherit'>" + _esc(md) + "</pre>"


def _ppl_block(submit):
    """已选人员框（与 shareView 中栏一致）。"""
    s = submit or {}
    rows = [
        f"<div><strong>答复负责人：</strong>{_esc(s.get('responder') or '—')}</div>",
        f"<div><strong>答复 QC：</strong>{_esc(s.get('qc') or '—')}</div>",
    ]
    if s.get("aqc"):
        rows.append(f"<div><strong>AQC：</strong>{_esc(s['aqc'])}</div>")
    if s.get("postscript"):
        rows.append(f"<div><strong>分配附言：</strong>{_esc(s['postscript'])}</div>")
    if s.get("reason"):
        rows.append(f"<div><strong>分配原因：</strong>{_esc(s['reason'])}</div>")
    if s.get("submitted_at"):
        rows.append(f"<div class='muted'>分配时间：{_esc(s['submitted_at'])}</div>")
    return "<div class='ppl'>" + "".join(rows) + "</div>"


def _panel(case, active):
    """单个案件的中栏内容（报告 + 人员）。"""
    seq = case.get("oaSeq")
    title = _esc(case.get("caseNo") or "案件") + (f"（第{seq}次OA）" if seq else "") + " — 分配情况"
    report_html = _md_to_html(case.get("reportMd", ""))
    if not (case.get("reportMd") or "").strip():
        report_html = "<div style='color:#c0c4cc;font-size:13px;padding:20px 0;text-align:center'>暂无案件报告</div>"
    cls = "case-panel case-panel--active" if active else "case-panel"
    return (f"<div class='{cls}' data-oaid='{_esc(case.get('oaid'))}'>"
            f"<div class='card'>"
            f"<div class='card__title'>{title}</div>"
            f"{_ppl_block(case.get('submit'))}"
            f"<div class='md-body'>{report_html}</div>"
            f"</div></div>")


def build_share_html(cases, shared_at="", batch=False):
    """生成自包含只读分享页 HTML 字符串。
    batch=True：左栏案件列表(原生 JS 切换)+中栏，标 shared_at；False：单案仅中栏。"""
    cases = [c for c in (cases or []) if c]
    panels = "".join(_panel(c, i == 0) for i, c in enumerate(cases)) \
        or "<div class='card'><div style='color:#c0c4cc;text-align:center;padding:30px 0'>暂无内容</div></div>"

    left, script = "", ""
    if batch:
        items = "".join(
            f"<div class='case-item{(' case-item--active' if i == 0 else '')}' "
            f"data-oaid='{_esc(c.get('oaid'))}' onclick='pick(this)'>"
            f"{_esc(c.get('caseNo') or c.get('oaid'))}"
            + (f"<span class='oa-badge'>OA{c.get('oaSeq')}</span>" if c.get("oaSeq") else "")
            + "</div>"
            for i, c in enumerate(cases))
        left = (f"<div class='case-list'>"
                f"<div class='case-list__hd'>📦 分享批次：{_esc(shared_at) or '—'}<br>"
                f"共 {len(cases)} 件（点击切换查看）</div>"
                f"<div class='case-list__body'>{items}</div></div>")
        script = """
<script>
function pick(el){
  var oaid=el.getAttribute('data-oaid');
  document.querySelectorAll('.case-item').forEach(function(x){x.classList.toggle('case-item--active',x===el)});
  document.querySelectorAll('.case-panel').forEach(function(p){
    p.classList.toggle('case-panel--active',p.getAttribute('data-oaid')===oaid)});
  document.querySelector('.center').scrollTop=0;
}
</script>"""

    return (
        "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>OA 分配情况（只读）</title>"
        f"<style>{_CSS}</style></head><body>"
        "<div class='pas-header'><span class='pas-header__brand'>专利任务分配 · 只读分享</span></div>"
        f"<div class='wrap'>{left}<div class='center'>{panels}</div></div>"
        f"{script}</body></html>"
    )
