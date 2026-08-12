#!/usr/bin/env python3
"""用流水线里的 AI 提示词从文件提取答复期限日期（诊断/人工核对用，直接调 filter_oa_email / parse_us_pdf 的现有函数）。

用法：
  # EP：文件是邮件正文文本 → 调 _ai_parse_ep_deadline（抽 issue_date + deadline）
  python3 extract_deadline_cli.py <text_file> --region EP [--issue-date 2026-08-05]

  # CN：文件是邮件正文文本 → 用 CN_DEADLINE_RE 抠「答复期限」再调 _ai_parse_cn_deadline
  python3 extract_deadline_cli.py <text_file> --region CN --issue-date 2026-08-05 [--pre-exam] [--deadline-text "五个工作日"]

  # US：文件是官文 PDF → 调 extract_us_deadline（正则/DeepSeek/OCR 抽月数 + 代码算日期）
  python3 extract_deadline_cli.py <oa.pdf> --region US --issue-date 2026-07-29
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser(description="用流水线提示词从文件提取答复期限")
    ap.add_argument("file", help="EP/CN=邮件正文文本文件；US=官文 PDF")
    ap.add_argument("--region", choices=["EP", "CN", "US"], default="EP")
    ap.add_argument("--issue-date", default="", help="发文日 YYYY-MM-DD（US 必填=邮戳日；CN 必填；EP 选填作提示）")
    ap.add_argument("--deadline-text", default="", help="CN：直接指定期限文字，不从文件抠")
    ap.add_argument("--pre-exam", action="store_true", help="CN：按预审案件（否则看正文是否含“预审案件”）")
    ap.add_argument("--show-text", action="store_true", help="打印从文件抽到的文字(诊断用)")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print(f"文件不存在: {args.file}", file=sys.stderr)
        sys.exit(2)

    if args.region == "US":
        from parse_us_pdf import extract_us_deadline
        if not args.issue_date:
            print("US 需要 --issue-date（邮戳/发文日）", file=sys.stderr)
            sys.exit(2)
        result = extract_us_deadline(args.file, mailing_date=args.issue_date)
        print(result)
        return

    # EP / CN 读文本（PDF 自动抽文字层）
    if args.file.lower().endswith(".pdf"):
        from parse_us_pdf import _pdf_to_text
        text, is_scanned = _pdf_to_text(args.file, max_pages=10)
        if not (text or "").strip():
            print("PDF 无文字层（可能是扫描件），EP/CN 文本提示词无法处理；"
                  "请改用带文字层的 PDF 或直接给文本文件。", file=sys.stderr)
            sys.exit(3)
    else:
        with open(args.file, encoding="utf-8", errors="replace") as f:
            text = f.read()

    # 诊断：抽到的文字长度 + 关键短语位置（EP 提示词只取正文前 3000 字）
    _low = (text or "").lower()
    _idx4 = _low.find("four months")
    _idxinv = _low.find("you are invited")
    print(f"[diag] 抽到文字 {len(text)} 字；'four months'@{_idx4}；'you are invited'@{_idxinv}"
          f"（EP 提示词只截前 3000 字）", file=sys.stderr)
    if args.show_text:
        print("=" * 20 + " 抽到的文字 " + "=" * 20, file=sys.stderr)
        print(text, file=sys.stderr)
        print("=" * 52, file=sys.stderr)

    if args.region == "EP":
        from filter_oa_email import _ai_parse_ep_deadline
        result = _ai_parse_ep_deadline(text, args.issue_date)
        print(result)
    else:  # CN
        from filter_oa_email import _ai_parse_cn_deadline, CN_DEADLINE_RE
        if not args.issue_date:
            print("CN 需要 --issue-date（发文日）", file=sys.stderr)
            sys.exit(2)
        dtext = args.deadline_text
        if not dtext:
            m = CN_DEADLINE_RE.search(text)
            dtext = m.group(1).strip() if m else ""
        if not dtext:
            print("CN 未从文件抠到「答复期限」，请用 --deadline-text 指定", file=sys.stderr)
            sys.exit(2)
        pre = args.pre_exam or ("预审案件" in text)
        deadline = _ai_parse_cn_deadline(dtext, args.issue_date, pre)
        print({"deadline_text": dtext, "is_pre_exam": pre, "deadline": deadline})


if __name__ == "__main__":
    main()
