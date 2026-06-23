#!/usr/bin/env python3
"""docx → PDF 转换（LibreOffice headless），审核页在线预览用。

前置：server 安装 LibreOffice
- Linux:   apt install libreoffice-writer --no-install-recommends
- Windows: winget install TheDocumentFoundation.LibreOffice（或官网 msi）
"""
import shutil
import subprocess
from pathlib import Path

_SOFFICE_CANDIDATES = ("soffice", "libreoffice")
# Windows 默认安装路径（不在 PATH 时兜底）
_SOFFICE_WIN_PATHS = (
    Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
    Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
)


def find_soffice() -> str:
    for name in _SOFFICE_CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    for path in _SOFFICE_WIN_PATHS:
        if path.exists():
            return str(path)
    raise RuntimeError(
        "未找到 LibreOffice（soffice），无法生成 PDF 预览。"
        "Linux: apt install libreoffice-writer --no-install-recommends；"
        "Windows: winget install TheDocumentFoundation.LibreOffice"
    )


def office_convert(src, to_fmt: str, out_dir=None, timeout: int = 120) -> Path:
    """用 LibreOffice 把 Office 文档转成指定格式（如 pdf、html），返回输出文件路径。
    电子表格转 html 会保留多 sheet 与表格结构，浏览效果优于 pdf。"""
    src = Path(src)
    if not src.exists():
        raise FileNotFoundError(str(src))
    out_dir = Path(out_dir) if out_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    soffice = find_soffice()
    result = subprocess.run(
        [soffice, "--headless", "--convert-to", to_fmt,
         "--outdir", str(out_dir), str(src)],
        capture_output=True, text=True, timeout=timeout,
    )
    out_path = out_dir / (src.stem + "." + to_fmt.split(":")[0])
    if result.returncode != 0 or not out_path.exists():
        raise RuntimeError(
            f"{src.suffix}→{to_fmt} 转换失败：{(result.stderr or result.stdout or '').strip()[:300]}"
        )
    return out_path


def docx_to_pdf(docx_path, out_dir=None, timeout: int = 120) -> Path:
    """单个 docx 转 PDF，返回 PDF 路径。out_dir 缺省与 docx 同目录。"""
    docx_path = Path(docx_path)
    if not docx_path.exists():
        raise FileNotFoundError(str(docx_path))
    out_dir = Path(out_dir) if out_dir else docx_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    soffice = find_soffice()
    result = subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf",
         "--outdir", str(out_dir), str(docx_path)],
        capture_output=True, text=True, timeout=timeout,
    )
    pdf_path = out_dir / (docx_path.stem + ".pdf")
    if result.returncode != 0 or not pdf_path.exists():
        raise RuntimeError(
            f"docx→PDF 转换失败：{(result.stderr or result.stdout or '').strip()[:300]}"
        )
    return pdf_path
