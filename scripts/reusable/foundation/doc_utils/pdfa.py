"""PDF → PDF/A-2b 转换（可复用，基于 Ghostscript）。

抽自 run_uspto_upload.py 的 _gs_bin/_to_pdfa/_others_to_pdfa，逻辑不变。零业务耦合。

依赖：系统安装的 Ghostscript（Windows gswin64c/gswin32c、Linux gs）。
"""
import glob
import os
import shutil
import subprocess


def gs_bin():
    """定位 Ghostscript 可执行文件（Windows gswin64c/gswin32c、Linux gs）。找不到返回 None。"""
    for name in ("gswin64c", "gswin32c", "gs"):
        p = shutil.which(name)
        if p:
            return p
    for pat in (r"C:\Program Files\gs\gs*\bin\gswin64c.exe",
                r"C:\Program Files (x86)\gs\gs*\bin\gswin32c.exe"):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def to_pdfa(src, out_dir, timeout=300):
    """把单个 PDF 转成 PDF/A-2b，输出到 out_dir（同名）。返回输出路径；失败抛异常。

    输入：src(PDF 路径)、out_dir(输出目录)、timeout(秒)
    输出：str（输出 PDF 路径）
    """
    gs = gs_bin()
    if not gs:
        raise RuntimeError("未找到 Ghostscript（gswin64c/gs），无法转 PDF/A；请先安装 Ghostscript。")
    out = os.path.join(out_dir, os.path.basename(src))
    cmd = [gs, "-dPDFA=2", "-dPDFACompatibilityPolicy=1", "-dBATCH", "-dNOPAUSE",
           "-sColorConversionStrategy=RGB", "-sDEVICE=pdfwrite",
           f"-sOutputFile={out}", src]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0 or not os.path.isfile(out):
        raise RuntimeError(f"PDF/A 转换失败（{os.path.basename(src)}）：{(r.stderr or r.stdout)[-300:]}")
    return out


def others_to_pdfa(others, out_dir):
    """把一批文件里的 PDF 逐个转 PDF/A-2b（临时副本，同名）；非 PDF 原样返回。失败抛异常。

    输入：others(路径列表)、out_dir → 输出：list[str]（转换后/原路径）
    """
    res = []
    for p in others:
        if p.lower().endswith(".pdf"):
            res.append(to_pdfa(p, out_dir))
        else:
            res.append(p)
    return res
