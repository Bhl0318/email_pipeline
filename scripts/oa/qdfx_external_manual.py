#!/usr/bin/env python3
"""将手工指定的材料转为 Markdown，再上传至外部前端分析接口。

填写下方案号和文件路径后运行：python scripts/oa/qdfx_external_manual.py
转换后的 Markdown 保存在 outputs/qdfx_manual/<案号>/；已有 .md 原样使用。
接口地址及令牌从 QDFX_API_BASE_URL、QDFX_API_TOKEN 读取；
未配置地址时使用正式环境 http://10.10.70.88:8088/assist。
"""

import json
import re
import subprocess
import sys
from contextlib import ExitStack
from pathlib import Path

import requests

from qdfx_external import _connection_config


CASE_NO = ""
OA_FILE = ""
APPLICATION_FILE = ""
REFERENCE_FILES = []
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "qdfx_manual"


def _docx_to_markdown(path):
    """按 Word 中的出现顺序保留段落和表格。"""
    from docx import Document
    from docx.table import Table

    parts = []
    for block in Document(path).iter_inner_content():
        if isinstance(block, Table):
            rows = [[cell.text.replace("\n", "<br>").replace("|", "\\|").strip()
                     for cell in row.cells] for row in block.rows]
            if rows:
                width = max(map(len, rows))
                rows = [row + [""] * (width - len(row)) for row in rows]
                parts.append("| " + " | ".join(rows[0]) + " |\n| " + " | ".join(["---"] * width) + " |"
                             + "".join("\n| " + " | ".join(row) + " |" for row in rows[1:]))
        else:
            content = block.text.strip()
            if not content:
                continue
            style = (block.style.name or "").lower()
            if style.startswith("heading") or style.startswith("标题"):
                match = re.search(r"\d+", style)
                level = min(int(match.group()) if match else 1, 6)
                content = "#" * level + " " + content
            parts.append(content)
    return "\n\n".join(parts)


def _convert_to_markdown(path):
    """把常用非 MD 文档转成 Markdown 字符串。"""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from mistral_ocr import pdf_to_markdown
        markdown = pdf_to_markdown(str(path))
        if markdown:
            return markdown
        import fitz
        with fitz.open(path) as pdf:
            return "\n\n".join(page.get_text().strip() for page in pdf if page.get_text().strip())
    if suffix == ".docx":
        return _docx_to_markdown(path)
    if suffix == ".doc":
        result = subprocess.run(["antiword", str(path)], capture_output=True, check=True)
        return result.stdout.decode("utf-8", errors="replace")
    if suffix == ".txt":
        return path.read_text(encoding="utf-8-sig")
    raise ValueError(f"不支持转换为 Markdown 的格式：{path.suffix}（支持 PDF、DOCX、DOC、TXT、MD）")


def _prepare_markdown(path, destination):
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".md":
        print(f"[材料使用] {path}")
        return path
    markdown = _convert_to_markdown(path)
    if not markdown.strip():
        raise ValueError(f"转换后无正文：{path}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(markdown, encoding="utf-8")
    print(f"[材料转换] {path} → {destination}")
    return destination


def submit_markdown_files(case_no, oa_file, application_file, reference_files, *, post=requests.post,
                          output_dir=OUTPUT_DIR):
    """准备 Markdown 并上传，返回接口的 data；不检查文献内容规范。"""
    token, base = _connection_config()
    if not token:
        raise ValueError("未配置 QDFX_API_TOKEN")
    if not case_no or not oa_file or not application_file or not reference_files:
        raise ValueError("请填写案号、审查意见、申请文件和至少一份对比文件")

    sources = [("scyj", Path(oa_file)), ("sqwj", Path(application_file))]
    sources.extend(("dbwj", Path(path)) for path in reference_files)
    case_dir = Path(output_dir) / re.sub(r"[^A-Za-z0-9_-]", "_", case_no)
    paths = []
    for index, (field, source) in enumerate(sources, 1):
        destination = case_dir / f"{field}-{index}-{source.stem}.md"
        paths.append((field, _prepare_markdown(source, destination)))

    with ExitStack() as stack:
        files = [(field, (path.name, stack.enter_context(path.open("rb")), "text/markdown"))
                 for field, path in paths]
        response = post(
            f"{base}/qdfx/external/parse",
            headers={"X-Api-Token": token},
            files=files,
            data={"caseNo": case_no, "createdBy": "writeSYS"},
            timeout=90,
        )
    payload = response.json()
    if response.status_code not in (200, 202) or payload.get("code") not in (200, 202):
        raise RuntimeError(payload.get("msg") or f"HTTP {response.status_code}")
    return payload["data"]


def main():
    try:
        data = submit_markdown_files(CASE_NO, OA_FILE, APPLICATION_FILE, REFERENCE_FILES)
    except Exception as exc:
        print(f"提交失败：{exc}", file=sys.stderr)
        return 1
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
