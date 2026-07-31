#!/usr/bin/env python3
"""US 官文自动盖 DOCKETED 邮戳 — 本地 PyMuPDF 直接在 PDF 第一页画章，不上传第三方。

复刻人工登记章（样例 2026-07-29-Non-Final Rejection-20608-0055US01.PDF）：
  红色 DOCKETED 章 + 登记日；下方红色 Arial 12 日期明细块，
  所有日期 = 发文日(邮戳) + N 个月，按 P1-综合期限速查表推断。

对外只用一个函数：stamp_us_pdf(pdf_path, ntype, mailing_date, out_path=...)。
不支持的类型（无固定期限，如 CTAV/CTEQ/补正类）返回 None，调用方保持原文件不盖章。
"""
import datetime
import os
import sys

RED = (1.0, 0.0, 0.0)
BLACK = (0.0, 0.0, 0.0)

# 各 US 官文类型的盖章配置（按 P1-综合期限速查表推断）:
#   label      : 章内首行 OA 类型标签
#   ssp        : 缩短法定期限(月)，即主答复绝限
#   extendable : 是否可按月延期到 6 个月法定绝限（画 EOT 行）
#   check_ids  : 是否画 "Check IDS when filing response" 行
US_STAMP_CONFIG = {
    "CTNF": {"label": "Non Final-OA",           "ssp": 3, "extendable": True,  "check_ids": True},
    "CTFR": {"label": "Final-OA",               "ssp": 3, "extendable": True,  "check_ids": True},
    "CTRS": {"label": "Restriction Requirement", "ssp": 2, "extendable": True,  "check_ids": True},
    "NOA":  {"label": "Notice of Allowance",    "ssp": 3, "extendable": False, "check_ids": False},
}


def _iso(dt):
    return dt.strftime("%Y-%m-%d")


def build_stamp_lines(ntype, mailing_date):
    """返回 (rows, cfg)。
    rows 为章内正文行列表，每行是 (label, date_str, is_red)；date_str 为 "" 表示整行只有 label。
    默认黑字，SSP 绝限行与最终非延期绝限行标红（同人工章）。
    mailing_date: datetime（发文日）。不支持的类型返回 (None, None)。"""
    cfg = US_STAMP_CONFIG.get(ntype)
    if not cfg or not mailing_date:
        return None, None
    from filter_oa_email import _add_months

    S = cfg["ssp"]
    rows = [(cfg["label"], "", False)]                # 首行：OA 类型
    # SSP 绝限前的提醒行： "k mon from S-mon due date" = 发文日 + (S-k) 月
    for k in range(S - 1, 0, -1):
        rows.append((f"{k} mon from {S}-mon due date:", _iso(_add_months(mailing_date, S - k)), False))
    if cfg["extendable"]:
        rows.append((f"{S}-mon due date:", _iso(_add_months(mailing_date, S)), True))   # SSP 绝限标红
        for e in range(1, 6 - S + 1):                # EOT 行，累计到 6 月法定绝限
            m = S + e
            if m == 6:
                rows.append((f"Final due date w/{e}-mon EOT (non-extendable):",
                             _iso(_add_months(mailing_date, m)), True))               # 最终绝限标红
            else:
                rows.append((f"Due date w/{e}-mon EOT:", _iso(_add_months(mailing_date, m)), False))
    else:
        rows.append((f"{S}-mon due date (non-extendable):", _iso(_add_months(mailing_date, S)), True))
    if cfg["check_ids"]:
        rows.append(("Check IDS when filing response", "", False))
    rows.append(("Input by: 系统", "", False))
    rows.append(("Reviewed by:", "", False))
    return rows, cfg


# —— 版式常量（对齐样例注释坐标，页面 612x792）——
_STAMP_RECT = (256, 182, 368, 262)      # 红色 DOCKETED 章外框
_BLOCK_X = 232                          # 日期块左边距（label 起点）
_BLOCK_RIGHT = 548                      # 日期右对齐边界
_BLOCK_TOP = 400                        # 首行基线 y
_LINE_H = 14                            # 行高
_FONT = 12                              # 正文字号


def _is_cjk(ch):
    return ord(ch) > 0x2E7F


def _draw_mixed(page, x, y, text, size, color):
    """按连续中/西文分段绘制：西文用 helv，中文用 china-s（避免中文字体把英文撑成全角）。
    返回结束 x。"""
    import fitz
    seg, seg_cjk = "", None
    cur = x
    def flush(s, is_cjk):
        nonlocal cur
        if not s:
            return
        font = "china-s" if is_cjk else "helv"
        page.insert_text((cur, y), s, fontsize=size, fontname=font, color=color)
        cur += fitz.get_text_length(s, fontsize=size, fontname=font)
    for ch in text:
        c = _is_cjk(ch)
        if seg and c != seg_cjk:
            flush(seg, seg_cjk)
            seg = ""
        seg, seg_cjk = seg + ch, c
    flush(seg, seg_cjk)
    return cur


def _draw_stamp(page, rows, docketed_date):
    """在 page（第一页）画红色 DOCKETED 椭圆章 + 带红框的日期明细块。"""
    import fitz

    # 1) DOCKETED 红色椭圆章
    x0, y0, x1, y1 = _STAMP_RECT
    page.draw_oval(fitz.Rect(x0, y0, x1, y1), color=RED, width=1.5)
    cx = (x0 + x1) / 2
    for text, size, font, baseline in (("DOCKETED", 15, "hebo", y0 + 32),
                                       (docketed_date.strftime("%b %d %Y"), 12, "helv", y0 + 54)):
        w = fitz.get_text_length(text, fontsize=size, fontname=font)
        page.insert_text((cx - w / 2, baseline), text, fontsize=size, fontname=font, color=RED)

    # 2) 日期明细块（先画外框，再逐行文字）
    n = len(rows)
    top = _BLOCK_TOP - 13
    bottom = _BLOCK_TOP + _LINE_H * (n - 1) + 5
    page.draw_rect(fitz.Rect(_BLOCK_X - 4, top, _BLOCK_RIGHT + 4, bottom), color=RED, width=1.2)

    y = _BLOCK_TOP
    for label, date, is_red in rows:
        color = RED if is_red else BLACK
        _draw_mixed(page, _BLOCK_X, y, label, _FONT, color)
        if date:
            dw = fitz.get_text_length(date, fontsize=_FONT, fontname="helv")
            lw = fitz.get_text_length(label, fontsize=_FONT, fontname="helv")
            dx = _BLOCK_RIGHT - dw                     # 右对齐
            if dx < _BLOCK_X + lw + 6:                 # 与 label 冲突则紧跟其后
                dx = _BLOCK_X + lw + 6
            page.insert_text((dx, y), date, fontsize=_FONT, fontname="helv", color=color)
        y += _LINE_H


def stamp_us_pdf(pdf_path, ntype, mailing_date, out_path=None,
                 docketed_date=None, clear_existing=False):
    """在 US 官文第一页盖 DOCKETED 邮戳，另存并返回输出路径。
    mailing_date: 发文日，datetime 或 'YYYY-MM-DD' 字符串。
    ntype: notification_type（CTNF/CTFR/CTRS/NOA）。不支持类型返回 None（不生成文件）。
    clear_existing: True 时先删掉第一页已有注释（用于在已人工盖章的样例上做对比）。"""
    import fitz

    if isinstance(mailing_date, str):
        from filter_oa_email import _parse_date
        mailing_date = _parse_date(mailing_date)
    rows, cfg = build_stamp_lines(ntype, mailing_date)
    if rows is None:
        print(f"[stamp] 类型 {ntype!r} 无固定期限或缺发文日，跳过盖章", file=sys.stderr)
        return None

    doc = fitz.open(pdf_path)
    page = doc[0]
    if clear_existing:
        for a in list(page.annots() or []):
            page.delete_annot(a)
    _draw_stamp(page, rows, docketed_date or datetime.date.today())
    out = out_path or (os.path.splitext(pdf_path)[0] + "_stamped.pdf")
    doc.save(out, garbage=3, deflate=True)
    doc.close()
    return out


if __name__ == "__main__":
    # 出样张：在 Non-Final 实样上清掉人工章、盖自动章，供逐字核对
    sample = "2026-07-29-Non-Final Rejection-20608-0055US01.PDF"
    out = stamp_us_pdf(sample, "CTNF", "2026-07-29",
                       out_path="_sample_stamped_CTNF.pdf", clear_existing=True)
    print("已生成样张:", out)
    # 各类型文字预览（无实样的类型只看文字）
    for nt in ("CTNF", "CTFR", "CTRS", "NOA"):
        rows, _ = build_stamp_lines(nt, __import__("datetime").datetime(2026, 7, 29))
        print(f"\n=== {nt} ===")
        for label, date, is_red in rows:
            print(f"  {'*R ' if is_red else '   '}{label:<48}{date}")
