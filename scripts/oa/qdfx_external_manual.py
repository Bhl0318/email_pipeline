#!/usr/bin/env python3
"""将已经准备好的 Markdown 文件直接上传至外部前端分析接口。

填写下方案号和文件路径后运行：python scripts/oa/qdfx_external_manual.py
接口地址及令牌从 QDFX_API_BASE_URL、QDFX_API_TOKEN 读取；
未配置地址时使用正式环境 http://10.10.70.88:8088/assist。
"""

import json
import sys
from contextlib import ExitStack
from pathlib import Path

import requests

from qdfx_external import _connection_config


CASE_NO = ""
OA_MD = ""
APPLICATION_MD = ""
REFERENCE_MDS = []


def submit_markdown_files(case_no, oa_md, application_md, reference_mds, *, post=requests.post):
    """仅上传指定文件并返回接口的 data；不解析、改写或下载文件。"""
    token, base = _connection_config()
    if not token:
        raise ValueError("未配置 QDFX_API_TOKEN")
    if not case_no or not oa_md or not application_md or not reference_mds:
        raise ValueError("请填写案号、审查意见、申请文件和至少一份对比文件")

    paths = [("scyj", Path(oa_md)), ("sqwj", Path(application_md))]
    paths.extend(("dbwj", Path(path)) for path in reference_mds)
    for _, path in paths:
        if path.suffix.lower() != ".md" or not path.is_file():
            raise ValueError(f"Markdown 文件不存在：{path}")

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
        data = submit_markdown_files(CASE_NO, OA_MD, APPLICATION_MD, REFERENCE_MDS)
    except Exception as exc:
        print(f"提交失败：{exc}", file=sys.stderr)
        return 1
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
