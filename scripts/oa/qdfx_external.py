"""将完整的 OA 材料提交到外部前端分析服务。

在运行邮件流程的服务器上配置 QDFX_API_TOKEN。对比文件从 FreePatentsOnline 下载；
只有 PDF 中的公开号完全匹配，且说明书和权利要求均可读取时，才会使用该文件。
QDFX_API_BASE_URL 默认指向正式环境的 /assist 接口。
"""

import os
import re
import sys
import tempfile
from urllib.parse import urlsplit

import requests


DEFAULT_BASE_URL = "http://10.10.70.88:8088/assist"
_PUBLICATION_RE = re.compile(r"^(?:CN|US|EP|WO|JP|KR|DE|GB|FR|CA|AU)\d{5,15}[A-Z]\d?$", re.I)


def _publication_number(raw):
    number = re.sub(r"[\s,./-]", "", str(raw or "").upper())
    return number if _PUBLICATION_RE.fullmatch(number) else ""


def _fpo_pdf(number, session=None):
    """从 FPO 下载对比文件，查询时保留非美国文献的国别代码。"""
    from download_patent_pdf import _extract_pdf_url, _new_session

    fpo = session or _new_session()[0]
    digits = re.search(r"\d+", number).group()
    slug = digits if number.startswith("US") else number[:2] + digits
    page_url = f"https://www.freepatentsonline.com/{slug}.pdf"
    page = fpo.get(page_url, timeout=30)
    page.raise_for_status()
    url = _extract_pdf_url(page.text)
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "s3.amazonaws.com" or not parsed.path.startswith("/pdf.sumobrain.com/"):
        raise ValueError("FPO 未提供可信的PDF下载地址")
    pdf = fpo.get(url, timeout=60)
    pdf.raise_for_status()
    return pdf.content, page_url


def _reference_markdown(raw_number, session=None):
    """下载 FPO 文献 PDF，校验后转换为 Markdown 正文。"""
    number = _publication_number(raw_number)
    if not number:
        return ""
    pdf_data, url = _fpo_pdf(number, session)
    description, claims = _reference_pdf_text(number, pdf_data)
    return f"# {number}\n\n来源：{url}\n\n## 说明书\n\n{description}\n\n## 权利要求\n\n{claims}\n"


def _reference_pdf_text(number, pdf_data):
    """使用或保存 PDF 前，核对公开号及说明书、权利要求正文。"""
    import fitz

    if not pdf_data.startswith(b"%PDF-") or len(pdf_data) > 32_000_000:
        raise ValueError("文献响应不是有效大小的PDF")
    with fitz.open(stream=pdf_data, filetype="pdf") as pdf:
        text = "\n".join(page.get_text() for page in pdf)
    if len(text.strip()) < 1000:
        from mistral_ocr import pdf_to_markdown
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            tmp.write(pdf_data)
            tmp.flush()
            text = pdf_to_markdown(tmp.name)
    compact = re.sub(r"[^A-Z0-9]", "", text.upper())
    if number not in compact:
        raise ValueError("文献正文中的公开号与请求不符")
    from oa_report_ai import _split_spec
    description, claims = _split_spec(text)
    if len(description.strip()) < 500 or len(claims.strip()) < 100:
        raise ValueError("文献缺少说明书或权利要求全文")
    return description, claims


def _ep_reference_numbers(oa_text):
    """只提取带 D 编号的引用行，避免误取本案公开号。"""
    pattern = r"\b(?:EP|WO|US|CN|JP|KR)\s*[0-9][0-9\s,./-]{4,17}\s*[A-C]\s*[0-9]?\b"
    lines = (line for line in (oa_text or "").splitlines() if re.search(r"\bD\d+\b", line, re.I))
    return [{"doc_no": n} for line in lines for raw in re.findall(pattern, line, re.I)
            if (n := _publication_number(raw))]


def submit_oa_analysis(item, oa_text, ref_docs, session=None):
    """提交一件新立项 OA 的材料；返回状态字典，不向调用方抛异常。"""
    token = os.environ.get("QDFX_API_TOKEN", "").strip()
    if not token:
        return {"status": "skipped", "reason": "QDFX_API_TOKEN 未配置"}
    project = (item.get("project") or "").strip()
    if not re.search(r"(?:CN|US|EP)\d{2}$", project):
        return {"status": "skipped", "reason": "案号地区格式不支持"}
    if not (oa_text or "").strip():
        return {"status": "skipped", "reason": "缺审查意见正文"}

    from oa_report_ai import find_application_files, _docx_text

    app_path = find_application_files(project, region=item.get("region", "")).get("spec")
    app_text = _docx_text(app_path)
    if not app_text.strip():
        return {"status": "skipped", "reason": "未找到可读取的申请文件"}
    refs = list(ref_docs or [])
    if item.get("region") == "EP" and not refs:
        refs = _ep_reference_numbers(oa_text)
    unrecognized = [str(d.get("doc_no")) for d in refs
                    if d.get("doc_no") and not _publication_number(d.get("doc_no"))]
    if unrecognized:
        return {"status": "skipped", "reason": f"存在无法自动获取的对比文件: {', '.join(unrecognized)}"}
    numbers = list(dict.fromkeys(n for d in refs
                                 if (n := _publication_number(d.get("doc_no")))))
    if not numbers:
        return {"status": "skipped", "reason": "未提取到专利对比文件号"}
    session = session or requests.Session()
    files = [
        ("scyj", ("审查意见.md", oa_text.encode("utf-8"), "text/markdown")),
        ("sqwj", ("申请文件.md", app_text.encode("utf-8"), "text/markdown")),
    ]
    failed = []
    for number in numbers:
        try:
            md = _reference_markdown(number)
            if md:
                files.append(("dbwj", (f"{number}.md", md.encode("utf-8"), "text/markdown")))
            else:
                failed.append(number)
        except Exception as exc:
            failed.append(number)
            print(f"[前端分析] {project} 对比文件 {number} 获取失败: {exc}", file=sys.stderr)
    # 对比文件必须齐全；缺件时跳过，避免评分漏掉审查意见引用的证据。
    if failed or len(files) == 2:
        return {"status": "skipped", "reason": f"对比文件正文不齐: {', '.join(failed or numbers)}"}

    base = os.environ.get("QDFX_API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    try:
        response = session.post(
            f"{base}/qdfx/external/parse",
            headers={"X-Api-Token": token},
            data={"caseNo": project, "createdBy": "email_pipeline"},
            files=files,
            timeout=90,
        )
        payload = response.json()
        code = payload.get("code")
        if response.status_code == 409 and code == 409:
            return {"status": "processing", "parseId": (payload.get("data") or {}).get("parseId")}
        if response.status_code != 202 or code != 202:
            return {"status": "failed", "reason": f"HTTP {response.status_code}/code {code}: {payload.get('msg', '')}"}
        data = payload.get("data") or {}
        return {"status": "submitted", "parseId": data.get("parseId"), "version": data.get("version")}
    except Exception as exc:
        return {"status": "failed", "reason": str(exc)}
