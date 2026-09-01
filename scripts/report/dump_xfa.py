#!/usr/bin/env python3
"""导出 XFA 表单 PDF 的 XML 结构（XFA 就是一组 XML 包：template/datasets/form/config…）。

用法：
  python dump_xfa.py <input.pdf>              # 各包打印到 stdout（带分隔标题）
  python dump_xfa.py <input.pdf> <out_dir>    # 各包分别写成 out_dir/<包名>.xml
  python dump_xfa.py <input.pdf> --packet template   # 只输出某个包到 stdout

XFA 存在 /Root/AcroForm/XFA：可能是单个流，或 [名, 流, 名, 流, …] 的数组。
"""
import sys
from pathlib import Path

import pikepdf


def iter_packets(pdf_path):
    """产出 (包名, bytes)。单流 XFA → 包名为 'xfa'。"""
    pdf = pikepdf.open(str(pdf_path))
    acro = pdf.Root.get("/AcroForm")
    if acro is None or "/XFA" not in acro:
        raise SystemExit(f"{pdf_path} 不含 XFA 表单（/AcroForm/XFA）")
    xfa = acro.XFA
    if not isinstance(xfa, pikepdf.Array):
        yield "xfa", bytes(xfa.read_bytes())
        return
    i = 0
    while i < len(xfa):
        o = xfa[i]
        if i + 1 < len(xfa):
            nxt = xfa[i + 1]
            try:
                yield str(o), bytes(nxt.read_bytes())
                i += 2
                continue
            except Exception:
                pass
        i += 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return
    pdf_path = argv[1]
    # 只输出某个包
    if len(argv) >= 4 and argv[2] == "--packet":
        want = argv[3]
        for name, data in iter_packets(pdf_path):
            if name == want:
                sys.stdout.write(data.decode("utf-8", "replace"))
                return
        raise SystemExit(f"未找到包：{want}")
    out_dir = argv[2] if len(argv) > 2 else None
    if out_dir:
        d = Path(out_dir)
        d.mkdir(parents=True, exist_ok=True)
        for name, data in iter_packets(pdf_path):
            safe = name.replace(":", "_").replace("/", "_").strip("<>") or "xfa"
            p = d / f"{safe}.xml"
            p.write_bytes(data)
            print(f"{p}  ({len(data)} bytes)")
    else:
        for name, data in iter_packets(pdf_path):
            print(f"\n===================== {name} ({len(data)} bytes) =====================")
            sys.stdout.write(data.decode("utf-8", "replace"))
            print()


if __name__ == "__main__":
    main(sys.argv)
