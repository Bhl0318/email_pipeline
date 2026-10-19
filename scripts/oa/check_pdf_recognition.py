#!/usr/bin/env python3
"""独立比较 OA 官文 PDF 的三种识别方法，逐项打印全文和耗时。

用法：
    python scripts/oa/check_pdf_recognition.py /path/to/审查意见.pdf
    python scripts/oa/check_pdf_recognition.py /path/to/审查意见.pdf --output-dir outputs/pdf_check

默认运行文字层提取、Mistral OCR、qwen-vl-max，三者互不作为兜底。
文字层默认读前 8 页，qwen-vl-max 默认看前 6 页，Mistral OCR 处理整份 PDF；
此页数与当前 OA 报告识别流程一致。需在已配置相应服务的环境运行远程方法。
"""
import argparse
import base64
from pathlib import Path
import sys
from time import perf_counter


def extract_text_layer(pdf_path, max_pages):
    """复用正式 OA 报告的文字层提取：PyMuPDF，空时再试 pypdf。"""
    from parse_us_pdf import _pdf_to_text

    text, _is_scanned = _pdf_to_text(str(pdf_path), max_pages=max_pages)
    return text or ""


def extract_mistral(pdf_path):
    """直接调用 Mistral OCR，不受文字层是否存在影响。"""
    from mistral_ocr import pdf_to_markdown

    return pdf_to_markdown(str(pdf_path)) or ""


def extract_qwen(pdf_path, max_pages):
    """直接将 PDF 页面图片交给视觉模型，不先尝试 Mistral OCR。"""
    import fitz
    from openai import OpenAI
    from parse_us_pdf import QWEN_API_KEY, QWEN_BASE_URL, QWEN_VL_MODEL

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
    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL,
                    timeout=180.0, max_retries=0)
    response = client.chat.completions.create(
        model=QWEN_VL_MODEL, max_tokens=4000,
        messages=[{"role": "user", "content": content}])
    if not response.choices or not response.choices[0].message:
        return ""
    return (response.choices[0].message.content or "").strip()


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
    elif result.strip():
        print(result)
        if output_path is not None:
            output_path.write_text(result, encoding="utf-8")
            print(f"完整结果已保存：{output_path}")
    else:
        print("未识别出文字（或服务未配置、未返回结果）；详情见上方日志。")
    print(f"字符数：{len(result)}；耗时：{elapsed:.2f} 秒", flush=True)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="比较 PDF 文字层、Mistral OCR、qwen-vl-max 的识别结果及耗时")
    parser.add_argument("pdf", type=Path, help="待识别的 PDF 文件")
    parser.add_argument("--text-pages", type=int, default=8, help="文字层提取页数，默认 8")
    parser.add_argument("--qwen-pages", type=int, default=6, help="qwen-vl-max 识别页数，默认 6")
    parser.add_argument("--output-dir", type=Path, help="额外将三种识别全文分别保存到此目录")
    args = parser.parse_args(argv)
    if not args.pdf.is_file() or args.pdf.suffix.lower() != ".pdf":
        parser.error(f"不是可读取的 PDF 文件：{args.pdf}")
    if args.text_pages < 1 or args.qwen_pages < 1:
        parser.error("页数必须大于 0")
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    pdf = args.pdf.resolve()
    print(f"文件：{pdf}", flush=True)
    methods = (
        ("文字层（PyMuPDF / pypdf）", "text", lambda: extract_text_layer(pdf, args.text_pages)),
        ("Mistral OCR", "mistral", lambda: extract_mistral(pdf)),
        ("qwen-vl-max 视觉识别", "qwen", lambda: extract_qwen(pdf, args.qwen_pages)),
    )
    for label, filename, func in methods:
        output_path = args.output_dir / f"{pdf.stem}.{filename}.md" if args.output_dir else None
        run_method(label, func, output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
