#!/usr/bin/env python3
"""离线整理最新版结项决策矩阵；不连接数据库、不修改现有规则。

输出 outputs/结项V2规范化草表.json，保留原表地区码和模板名称，
供比对 TIP 的地区判定及模板映射后生成最终的结项域替换 SQL。
"""

import json
import re
from collections import Counter
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[2]
MATRIX_DIR = ROOT / "最新版本"
OUT = ROOT / "outputs" / "结项V2规范化草表.json"
SHEETS = ("结项通知-CN", "结项通知-US", "结项通知-PCT")
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
MD_DIR = ROOT / "scripts" / "templates" / "md" / "结项通知"


def _parts(value):
    """类型2 中逗号分隔不同项目；保留 '/'、'-' 等原词内部标点。"""
    return [x.strip() for x in re.split(r"[,，]", str(value or "")) if x.strip()]


def _customer(header):
    header = str(header or "").strip()
    if header == "其他客户":
        return "其他"
    if header == "5开头案号":
        return "5开头"
    m = re.match(r"^(\d{5})(?:\D|$)", header)
    if not m:
        raise ValueError(f"未知客户列：{header!r}")
    return m.group(1)


def _action(value):
    text = str(value or "").strip()
    if text == "不处理":
        return {"action": "ignore"}
    emails = EMAIL_RE.findall(text)
    if text.startswith("分配→") and len(emails) == 1:
        return {"action": "assign", "preparer": emails[0]}
    if text.startswith("转发→") and emails:
        # 结项场景中这些地址最终都并入原结项邮件的 CC；保留主送/抄送来源。
        return {"action": "skip", "forward": {"to": emails[:1], "cc": emails[1:]}}
    raise ValueError(f"未识别动作：{text!r}")


def _template_md(sheet_name, label):
    """按新版模板标签定位已有 MD；返回空字符串表示尚无可直接渲染的正文。"""
    if label in ("无需做", "待填模板（仅表头版）"):
        return ""
    prefix = sheet_name.rsplit("-", 1)[-1]
    tags = re.findall(r"【([^】]+)】", label)
    needle = "".join(tags).replace(" ", "").replace("_", "")
    candidates = [p.name for p in MD_DIR.glob(prefix + "_*.md")
                  if needle in p.stem.replace(" ", "").replace("_", "")]
    # 两个标签与文件名不完全同形；206 表还存在两种缴费变体，默认指向基础版。
    overrides = {
        ("PCT", "【主动撤回】撤回国际申请"): "PCT_撤回申请提交.md",
        ("PCT", "【206表补正提交】206表补正"): "PCT_206表补正提交.md",
    }
    chosen = overrides.get((prefix, label))
    if chosen:
        if not (MD_DIR / chosen).is_file():
            raise ValueError(f"模板不存在：{chosen}")
        return chosen
    if len(candidates) != 1:
        raise ValueError(f"模板映射不唯一：{sheet_name} {label!r} -> {candidates}")
    return candidates[0]


def build(path):
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    records = []
    seen = set()
    for sheet_name in SHEETS:
        rows = list(book[sheet_name].values)
        header = [str(x or "").strip() for x in rows[0]]
        columns = {name: header.index(name) for name in (
            "国别", "匹配粒度", "结项类型1", "结项类型2", "匹配键(IT比对此列)", "模板")}
        template_idx = columns["模板"]
        customer_cols = [(i, _customer(header[i])) for i in range(template_idx + 1, len(header) - 1)]
        for excel_row, row in enumerate(rows[1:], 2):
            get = lambda field: str(row[columns[field]] or "").strip()
            regions = [x.strip() for x in re.split(r"[,，;；]", get("国别")) if x.strip()]
            granularity = get("匹配粒度")
            type1 = get("结项类型1")
            type2 = _parts(get("结项类型2"))
            if granularity not in ("仅类型1", "类型1+类型2") or not type1 or not regions:
                raise ValueError(f"{sheet_name}:{excel_row} 匹配键不完整")
            if granularity == "类型1+类型2" and not type2:
                raise ValueError(f"{sheet_name}:{excel_row} 缺类型2")
            match_keys = ([type1] if granularity == "仅类型1"
                          else [f"{type1}_{x}" for x in type2])
            actions = {code: _action(row[i]) for i, code in customer_cols}
            for region in regions:
                for match_key in match_keys:
                    signature = (region, match_key)
                    if signature in seen:
                        raise ValueError(f"重复地区+匹配键：{sheet_name}:{excel_row} {signature}")
                    seen.add(signature)
            template_label = get("模板")
            records.append({
                "sheet": sheet_name,
                "excel_row": excel_row,
                "regions": regions,
                "granularity": granularity,
                "type1": type1,
                "type2": type2,
                "source_match_key": get("匹配键(IT比对此列)"),
                "match_keys": match_keys,
                "template_label": template_label,
                "template_md": _template_md(sheet_name, template_label),
                "actions": actions,
            })
    return {
        "source": str(path.relative_to(ROOT)),
        "scope": "CN/US/PCT 已审核；EP 与海外其他本轮未启用",
        "records": records,
        "summary": {
            "source_rows": len(records),
            "region_match_keys": len(seen),
            "actions": dict(Counter(a["action"] for r in records for a in r["actions"].values())),
        },
    }


def main():
    files = sorted(MATRIX_DIR.glob("结项决策矩阵-给IT版-V2-*.xlsx"))
    if len(files) != 1:
        raise RuntimeError(f"预期一份 V2 矩阵，找到 {len(files)} 份")
    data = build(files[0])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["summary"], ensure_ascii=False))
    print(OUT)


if __name__ == "__main__":
    main()
