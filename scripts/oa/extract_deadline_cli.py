#!/usr/bin/env python3
"""用流水线里的 AI 提示词从文件提取答复期限日期（诊断/人工核对用，直接调 filter_oa_email / parse_us_pdf 的现有函数）。

输入文件可为：.txt 文本 / .pdf 官文(自动抽文字层) / .msg 邮件(extract_msg 取正文，主题里的日期兜底作发文日)。

用法：
  # EP：邮件正文文本/PDF/.msg → 调 _ai_parse_ep_deadline（抽 issue_date + deadline）
  python3 extract_deadline_cli.py <file.txt|.pdf|.msg> --region EP [--issue-date 2026-08-05]

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

    # EP / CN 读文本（.pdf 抽文字层；.msg 用 extract_msg 取正文；否则按文本读）
    low = args.file.lower()
    if low.endswith(".pdf"):
        from parse_us_pdf import _pdf_to_text
        text, is_scanned = _pdf_to_text(args.file, max_pages=10)
        if not (text or "").strip():
            print("PDF 无文字层（可能是扫描件），EP/CN 文本提示词无法处理；"
                  "请改用带文字层的 PDF 或直接给文本文件。", file=sys.stderr)
            sys.exit(3)
    elif low.endswith(".msg"):
        try:
            import extract_msg
        except ImportError:
            print("读 .msg 需要 extract_msg 库：pip install extract-msg", file=sys.stderr)
            sys.exit(2)
        m = extract_msg.Message(args.file)
        text = m.body or ""
        html = m.htmlBody
        if html:
            if isinstance(html, bytes):
                html = html.decode("utf-8", errors="replace")
            import re as _re
            import html as _htmlmod
            # 去标签转纯文本，否则「答复期限：<span…>」会被 CN 正则抓成 "<span"
            _plain = _re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', html)
            _plain = _re.sub(r'(?i)<br\s*/?>|</p>|</div>', '\n', _plain)
            _plain = _htmlmod.unescape(_re.sub(r'<[^>]+>', '', _plain))
            text = f"{text}\n{_plain}"
        if not args.issue_date and m.subject:  # 主题里常带 日期-类型-案号，兜底作发文日提示
            import re as _re
            _dm = _re.search(r'(\d{4}-\d{2}-\d{2})', m.subject)
            if _dm:
                args.issue_date = _dm.group(1)
        m.close()
    else:
        with open(args.file, encoding="utf-8", errors="replace") as f:
            text = f.read()

    # 诊断：按 region 显示（EP 找英文期限句 / CN 找答复期限·预审案件）
    print(f"[diag] region={args.region}  抽到文字 {len(text)} 字  发文日={args.issue_date or '(未定)'}", file=sys.stderr)
    if args.region == "EP":
        _low = (text or "").lower()
        print(f"       'four months'@{_low.find('four months')}  "
              f"'you are invited'@{_low.find('you are invited')}  (EP提示词截前12000字)", file=sys.stderr)
    else:
        print(f"       '答复期限'@{text.find('答复期限')}  '预审案件'@{text.find('预审案件')}", file=sys.stderr)
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
        print({"issue_date": args.issue_date, "deadline_text": dtext,
               "is_pre_exam": pre, "deadline": deadline})


if __name__ == "__main__":
    main()
