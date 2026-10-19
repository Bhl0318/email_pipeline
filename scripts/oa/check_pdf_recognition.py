#!/usr/bin/env python3
"""独立比较 OA 官文 PDF 的四种识别方法，逐项打印全文和耗时。

用法：
    python scripts/oa/check_pdf_recognition.py /path/to/审查意见.pdf
    python scripts/oa/check_pdf_recognition.py /path/to/审查意见.pdf --qwen-model qwen3-vl-plus
    python scripts/oa/check_pdf_recognition.py /path/to/审查意见.pdf --output-dir outputs/pdf_check

默认运行文字层提取、Mistral OCR、qwen3-vl-plus 和 pdfRest，四者互不作为兜底。
文字层默认读前 8 页，qwen3-vl-plus 默认看前 6 页，其余处理整份 PDF；
此页数与当前 OA 报告识别流程一致。需在已配置相应服务的环境运行远程方法。
pdfRest 会把 PDF 上传到云端；可通过 PDFREST_API_KEY 覆盖项目已有密钥。
"""
import argparse
import base64
import os
from pathlib import Path
import sys
from time import perf_counter
import unicodedata


def extract_text_layer(pdf_path, max_pages):
    """复用正式 OA 报告的文字层提取：PyMuPDF，空时再试 pypdf。"""
    from parse_us_pdf import _pdf_to_text

    text, _is_scanned = _pdf_to_text(str(pdf_path), max_pages=max_pages)
    return text or ""


def extract_mistral(pdf_path):
    """直接调用 Mistral OCR，不受文字层是否存在影响。"""
    from mistral_ocr import pdf_to_markdown

    return pdf_to_markdown(str(pdf_path)) or ""


def extract_qwen(pdf_path, max_pages, model=None, base_url=None):
    """直接将 PDF 页面图片交给视觉模型，不先尝试 Mistral OCR。"""
    import fitz
    from openai import OpenAI
    from parse_us_pdf import QWEN_API_KEY, QWEN_BASE_URL

    content = [{"type": "text", "text":
                "这些是专利审查意见通知书/官方文件的扫描页。请逐字识别其中全部文字，"
                "按阅读顺序输出为纯文本，保留条目/编号；不要总结、不要翻译、不要加任何解释。"}]
    with fitz.open(str(pdf_path)) as pdf:
        for page_number in range(min(max_pages, len(pdf))):
            image = pdf[page_number].get_pixmap(dpi=150).tobytes("png")
            encoded = base64.b64encode(image).decode("ascii")
            content.append({"type": "image_url", "image_url":
                            {"url": f"data:image/png;base64,{encoded}"}})
    if len(content) == 1:
        return ""
    client = OpenAI(api_key=QWEN_API_KEY, base_url=base_url or QWEN_BASE_URL,
                    timeout=180.0, max_retries=0)
    response = client.chat.completions.create(
        model=model or "qwen3-vl-plus", max_tokens=4000,
        messages=[{"role": "user", "content": content}])
    if not response.choices or not response.choices[0].message:
        return ""
    return (response.choices[0].message.content or "").strip()


def extract_pdfrest(pdf_path, base_url="https://api.pdfrest.com", languages="chi_sim,eng"):
    """pdfRest 先 OCR 生成文字层，再从生成的 PDF 提取全文。"""
    import requests

    api_key = os.environ.get("PDFREST_API_KEY")
    if not api_key:
        report_dir = Path(__file__).resolve().parents[1] / "report"
        sys.path.insert(0, str(report_dir))
        from submission.common import PDFREST_API_KEY
        api_key = PDFREST_API_KEY
    if not api_key:
        raise RuntimeError("未配置 PDFREST_API_KEY")

    root = base_url.rstrip("/")
    headers = {"Api-Key": api_key, "Accept": "application/json"}
    with pdf_path.open("rb") as source:
        ocr = requests.post(
            f"{root}/pdf-with-ocr-text", headers=headers,
            files={"file": (pdf_path.name, source, "application/pdf")},
            data={"languages": languages}, timeout=300)
    ocr.raise_for_status()
    ocr_data = ocr.json()
    if ocr_data.get("warning"):
        print(f"[pdfRest] OCR 警告：{ocr_data['warning']}", flush=True)
    output_id = ocr_data.get("outputId")
    if not output_id:
        raise RuntimeError(f"pdfRest OCR 未返回 outputId：{ocr_data}")

    extracted = requests.post(
        f"{root}/extracted-text", headers=headers, data={"id": output_id},
        timeout=300)
    extracted.raise_for_status()
    result = extracted.json()
    full_text = result.get("fullText")
    if isinstance(full_text, dict):
        full_text = full_text.get("text") or full_text.get("document")
    if not isinstance(full_text, str):
        raise RuntimeError(f"pdfRest 未返回文字内容：{result}")
    return full_text.strip()


def run_method(label, func, output_path=None):
    """一次方法失败仍继续测试其他方法；打印结果、字数和本次耗时。"""
    print(f"\n{'=' * 24} {label} {'=' * 24}", flush=True)
    start = perf_counter()
    error = None
    try:
        result = func()
    except Exception as exc:
        result = ""
        error = f"{type(exc).__name__}: {exc}"
    elapsed = perf_counter() - start

    if error:
        print(f"识别失败：{error}")
        if "model_not_found" in error or "Model not exist" in error:
            print("模型不存在或当前账号/地域不可用。可用 --qwen-model 指定其他视觉模型，"
                  "并确认 --qwen-base-url 与 API Key 属于同一地域。")
    elif result.strip():
        print(result)
        if output_path is not None:
            output_path.write_text(result, encoding="utf-8")
            print(f"完整结果已保存：{output_path}")
    else:
        print("未识别出文字（或服务未配置、未返回结果）；详情见上方日志。")
    print(f"字符数：{len(result)}；耗时：{elapsed:.2f} 秒", flush=True)
    return result, error, elapsed


def _display_width(value):
    """计算中英文混排时的终端显示宽度。"""
    return sum(2 if unicodedata.east_asian_width(char) in "FW" else 1 for char in value)


def _cell(value, width):
    """按终端显示宽度补空格，保持三列表格对齐。"""
    return value + " " * max(0, width - _display_width(value))


def print_summary(summary):
    """汇总实际识别状态；不根据字数推断准确度。"""
    rows = [("方法", "耗时", "结果")]
    names = {"text": "PDF 文字层", "qwen": "Qwen 视觉识别",
             "pdfrest": "pdfRest OCR", "mistral": "Mistral OCR"}
    for filename in ("text", "qwen", "pdfrest", "mistral"):
        result, error, elapsed = summary[filename]
        if error:
            detail = "识别失败（详见上方错误）"
        elif result:
            detail = f"提取 {len(result)} 字符"
        else:
            detail = "无文字（服务未配置或未返回内容）"
        duration = "—" if not error and not result else f"{elapsed:.2f} 秒"
        rows.append((names[filename], duration, detail))

    widths = [max(_display_width(row[col]) for row in rows) for col in range(3)]
    line_width = sum(widths) + 4
    print("\n识别汇总（字数不代表准确度，请对照原 PDF 检查）：", flush=True)
    for index, row in enumerate(rows):
        print("  " + "  ".join(_cell(value, widths[col]) for col, value in enumerate(row)), flush=True)
        if index == 0:
            print("  " + "━" * line_width, flush=True)
        elif index < len(rows) - 1:
            print("  " + "─" * line_width, flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="比较 PDF 文字层、Mistral OCR、qwen3-vl-plus、pdfRest 的识别结果及耗时")
    parser.add_argument("pdf", type=Path, help="待识别的 PDF 文件")
    parser.add_argument("--text-pages", type=int, default=8, help="文字层提取页数，默认 8")
    parser.add_argument("--qwen-pages", type=int, default=6, help="视觉模型识别页数，默认 6")
    parser.add_argument("--qwen-model", default=os.environ.get("QWEN_VL_MODEL") or "qwen3-vl-plus",
                        help="视觉模型名；默认 qwen3-vl-plus")
    parser.add_argument("--qwen-base-url", default=os.environ.get("QWEN_BASE_URL", ""),
                        help="视觉模型接口地址；默认沿用正式 OA 流程的北京地址")
    parser.add_argument("--pdfrest-base-url", default=os.environ.get("PDFREST_BASE_URL", "https://api.pdfrest.com"),
                        help="pdfRest 接口地址，默认美国云端")
    parser.add_argument("--pdfrest-languages", default="chi_sim,eng",
                        help="pdfRest OCR 语言，默认简体中文和英文")
    parser.add_argument("--output-dir", type=Path, help="额外将四种识别全文分别保存到此目录")
    args = parser.parse_args(argv)
    if not args.pdf.is_file() or args.pdf.suffix.lower() != ".pdf":
        parser.error(f"不是可读取的 PDF 文件：{args.pdf}")
    if args.text_pages < 1 or args.qwen_pages < 1:
        parser.error("页数必须大于 0")
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    pdf = args.pdf.resolve()
    print(f"文件：{pdf}", flush=True)
    from parse_us_pdf import QWEN_BASE_URL
    qwen_model = args.qwen_model
    qwen_base_url = args.qwen_base_url or QWEN_BASE_URL
    print(f"Qwen 模型：{qwen_model}；接口：{qwen_base_url}", flush=True)
    methods = (
        ("文字层（PyMuPDF / pypdf）", "text", lambda: extract_text_layer(pdf, args.text_pages)),
        ("Mistral OCR", "mistral", lambda: extract_mistral(pdf)),
        (f"{qwen_model} 视觉识别", "qwen",
         lambda: extract_qwen(pdf, args.qwen_pages, qwen_model, qwen_base_url)),
        ("pdfRest OCR + 文字提取（全文）", "pdfrest",
         lambda: extract_pdfrest(pdf, args.pdfrest_base_url, args.pdfrest_languages)),
    )
    summary = {}
    for label, filename, func in methods:
        output_path = args.output_dir / f"{pdf.stem}.{filename}.md" if args.output_dir else None
        summary[filename] = run_method(label, func, output_path)
    print_summary(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
