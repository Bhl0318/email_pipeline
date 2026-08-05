#!/usr/bin/env python3
"""
US 答复期限获取 — 下载官文 PDF + 解析答复月数 + 计算绝限日。

用法:
  python3 us_deadline.py <application_no> <document_code> <oa_doc_date> <project>
  python3 us_deadline.py 19208724 CTNF 2026-01-23 20849-0319US00

Python 调用:
  from us_deadline import get_us_deadline
  result = get_us_deadline("19208724", "CTNF", "2026-01-23", "20849-0319US00")
  # result = {"months": 3, "deadline": "2026-04-23", "pdf_path": "..."}
"""
import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, "../..", "attachment")


def get_us_deadline(application_no, document_code, oa_doc_date, project):
    """
    下载 US 官文 PDF 并提取答复期限。

    Args:
        application_no: USPTO 申请号 (如 "19208724")
        document_code: 文档类型代码 (如 "CTNF")
        oa_doc_date: Mailroom Date，即 mailing date (如 "2026-01-23"，YYYY-MM-DD)
        project: 七星天案号 (如 "20849-0319US00")

    Returns:
        dict: {"months": int, "deadline": str, "pdf_path": str} 或 None
    """
    from downloadByAPI import USPTOApplication
    from parse_us_pdf import extract_us_deadline

    # oa_doc_date 格式统一为 YYYY-MM-DD
    mailing_date = oa_doc_date
    if "/" in mailing_date:
        parts = mailing_date.split("/")
        if len(parts) == 3:
            mailing_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"

    # 1. 下载 PDF
    print(f"[US] 下载官文: app={application_no} doc={document_code} date={mailing_date} project={project}", file=sys.stderr)
    try:
        uspto = USPTOApplication(download_dir=DOWNLOAD_DIR, project=project)
        doc_list = uspto.downLoad_Documents_ByAPI(application_no, document_code, mailing_date, project, "")
    except Exception as e:
        print(f"[US] 下载失败: {e}", file=sys.stderr)
        return None

    # 2. 找到 PDF 文件
    files = doc_list.get(project, [])
    pdf_path = None
    for f in files:
        if f.lower().endswith(".pdf"):
            pdf_path = f
            break

    if not pdf_path or not os.path.exists(pdf_path):
        print(f"[US] 未找到 PDF 文件: {files}", file=sys.stderr)
        return None

    # 3. 解析答复期限
    print(f"[US] 解析 PDF: {pdf_path}", file=sys.stderr)
    result = extract_us_deadline(pdf_path, mailing_date=mailing_date)
    if not result:
        # 解析不到期限（EXIN/NOA/补正等）也要保留已下载的 pdf_path，供盖章/转OA附件/Wiki/EXIN判定
        print(f"[US] PDF 期限解析失败，保留 pdf_path", file=sys.stderr)
        return {"months": None, "deadline": None, "pdf_path": pdf_path}

    result["pdf_path"] = pdf_path
    print(f"[US] 结果: months={result['months']}, deadline={result['deadline']}", file=sys.stderr)
    return result


def download_us_ref_doc(application_no, document_code, official_date, project):
    """下载同案号的文献(892/1449)PDF，返回本地文件路径列表；失败/无匹配返回 []。
    与官文走同一 USPTO documents API，按 documentCode + officialDate 精确匹配。"""
    from downloadByAPI import USPTOApplication

    mailing_date = official_date or ""
    if "/" in mailing_date:
        parts = mailing_date.split("/")
        if len(parts) == 3:
            mailing_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
    if not application_no or not document_code:
        return []
    print(f"[US-ref] 下载文献: app={application_no} doc={document_code} date={mailing_date} project={project}", file=sys.stderr)
    try:
        uspto = USPTOApplication(download_dir=DOWNLOAD_DIR, project=project)
        doc_list = uspto.downLoad_Documents_ByAPI(application_no, document_code, mailing_date, project, "")
        return [f for f in doc_list.get(project, []) if f and os.path.exists(f)]
    except Exception as e:
        print(f"[US-ref] {project} {document_code} 下载失败: {e}", file=sys.stderr)
        return []


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("用法: python3 us_deadline.py <application_no> <document_code> <oa_doc_date> <project>")
        sys.exit(1)

    result = get_us_deadline(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("获取失败")
        sys.exit(1)
