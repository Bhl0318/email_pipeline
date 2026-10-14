#!/usr/bin/env python3
"""调用 VPS 的对比文件接口（FPO 优先，Google Patents 回退），保存返回的 Markdown。

用法：
    python scripts/oa/check_fpo_remote.py US20250150762A1
    python scripts/oa/check_fpo_remote.py CN110693604A --output outputs/fpo_check/CN110693604A.md

服务地址与密钥沿用 MISTRAL_OCR_URL / MISTRAL_OCR_KEY，未设置时读取
scripts/pipeline_config.json 的 mistral_ocr.base / mistral_ocr.api_key。
此脚本不在本机下载 PDF，也不提交前端分析。
"""

import argparse
import sys
from pathlib import Path

from mistral_ocr import _config
from qdfx_external import _publication_number


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "fpo_check"


def fetch_reference(raw_number, output_path=None):
    """把公开号交给 OCR VPS 下载、识别；成功后保存 Markdown。"""
    number = _publication_number(raw_number)
    if not number:
        raise ValueError("请输入完整公开号，例如 US20250150762A1")
    base, key = _config()
    if not key:
        raise ValueError("未配置 MISTRAL_OCR_KEY 或 scripts/pipeline_config.json 中的 mistral_ocr.api_key")

    import requests
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.post(
        f"{base}/fpo-reference",
        headers={"X-API-Key": key},
        json={"publication_number": number},
        verify=False,  # 当前 VPS 使用自签证书，与现有 OCR 客户端一致
        timeout=420,
    )
    if not response.ok:
        try:
            detail = response.json().get("detail") or response.text[:300]
        except ValueError:
            detail = response.text[:300]
        raise RuntimeError(f"接口返回 HTTP {response.status_code}: {detail}")
    payload = response.json()
    if payload.get("publication_number") != number:
        raise ValueError("服务端返回的公开号与请求不符")
    markdown = (payload.get("markdown") or "").strip()
    if not markdown:
        raise ValueError("服务端没有返回 Markdown 正文")

    target = Path(output_path) if output_path else DEFAULT_OUTPUT_DIR / f"{number}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markdown + "\n", encoding="utf-8")
    print(f"公开号：{number}")
    print(f"PDF 来源：{payload.get('source', '')}")
    print(f"PDF 页数：{payload.get('pages', '未知')}；服务耗时：{payload.get('elapsed', '未知')} 秒")
    print(f"Markdown：{target.resolve()}（{len(markdown)} 字符）")
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description="调用 OCR VPS 的专利 PDF 下载及 Markdown 转换接口")
    parser.add_argument("publication_number", help="完整专利公开号，例如 US20250150762A1")
    parser.add_argument("--output", help="输出 .md 路径，默认 outputs/fpo_check/<公开号>.md")
    args = parser.parse_args(argv)
    try:
        fetch_reference(args.publication_number, args.output)
    except Exception as exc:
        print(f"对比文件远程解析失败：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
