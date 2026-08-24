#!/usr/bin/env python3
"""人员负荷 —— 读 Confluence 负荷页(pageId 151195467)，抽「姓名：NN%（可分配…）」饱和度 + 请假/培训。

供人员安排建议参考：负荷低(饱和度%小)、未请假/不在培训 的人优先。名字是口语简称，
交给 DeepSeek 与白名单做模糊关联，本模块只负责取页+抽取+格式化文本块。
读页失败/连不上返回空串（不阻断方案生成）。带短缓存避免每次请求。
"""
import re
import sys
import time

WORKLOAD_PAGE_ID = "151195467"
_CACHE = {"ts": 0, "block": None}
_TTL = 600   # 秒


def _strip(html):
    t = re.sub(r"<[^>]+>", " ", html or "")
    t = t.replace("&nbsp;", " ").replace("&ldquo;", "").replace("&rdquo;", "")
    return t


def parse_workload(html):
    """→ {name: load_int}, [请假/培训原文行]。抽全文 '姓名：NN%'。"""
    text = _strip(html)
    loads = {}
    for m in re.finditer(r"([一-龥A-Za-z·]{2,6})\s*[：:]\s*(\d{1,3})\s*%", text):
        name, pct = m.group(1).strip(), int(m.group(2))
        # 同名多处取较大值（更保守，倾向认为更忙）
        if name not in loads or pct > loads[name]:
            loads[name] = pct
    # 请假/培训/休假 相关短句（供避让）
    absents = []
    for m in re.finditer(r"([^。\n]{0,40}(?:请假|休假|培训)[^。\n]{0,30})", text):
        s = re.sub(r"\s+", " ", m.group(1)).strip()
        if s and s not in absents:
            absents.append(s)
    return loads, absents


def format_block(loads, absents):
    if not loads and not absents:
        return ""
    lines = ["【人员负荷（饱和度%；越小越空闲，100%=满负荷，优先安排低负荷者）】"]
    for name, pct in sorted(loads.items(), key=lambda x: x[1]):
        lines.append(f"  - {name}：{pct}%")
    if absents:
        lines.append("【请假/培训（尽量避开）】")
        lines += [f"  - {a}" for a in absents[:20]]
    return "\n".join(lines)


def workload_block(page_id=None, force=False):
    """取负荷页 → 文本块（供塞进 schemes 提示词）。带缓存；失败返回空串。"""
    now = time.time()
    if not force and _CACHE["block"] is not None and now - _CACHE["ts"] < _TTL:
        return _CACHE["block"]
    block = ""
    try:
        from oainfo_cli import WikiClient
        p = WikiClient().get_page_by_id(page_id or WORKLOAD_PAGE_ID)
        if p:
            loads, absents = parse_workload(p.get("body", ""))
            block = format_block(loads, absents)
    except Exception as e:
        print(f"[oa_workload] 取负荷页失败: {e}", file=sys.stderr)
    _CACHE["ts"], _CACHE["block"] = now, block
    return block


if __name__ == "__main__":
    import os
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):   # 本地 HTML 测试
        loads, absents = parse_workload(open(sys.argv[1], encoding="utf-8").read())
        print(f"抽到 {len(loads)} 人饱和度、{len(absents)} 条请假/培训\n")
        print(format_block(loads, absents))
    else:
        print(workload_block())
