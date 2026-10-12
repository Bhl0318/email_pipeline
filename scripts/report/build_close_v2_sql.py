#!/usr/bin/env python3
"""离线生成结项 V2 规则替换 SQL 草案；不会连接数据库。

本脚本替换三个规则表的 close 域，并为结项 V2 名称补齐 report_template 正文；
不触及 OA、report_tasks 或已有同名模板正文。
生成文件默认以 ROLLBACK 结束。国别码从案号地区位提取；上线前需确认 TIP 的类型1回退匹配，
并完成 V2 Word 正文转换与审核，随后再决定是否提交事务。
"""

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs" / "结项V2规范化草表.json"
OUT = ROOT / "outputs" / "结项V2规则替换草案.sql"
CN_MD_DIR = ROOT / "scripts" / "templates" / "md" / "结项通知"
V2_MD_DIR = ROOT / "outputs" / "结项V2模板草稿"


def q(value):
    """MySQL 单引号字面量；所有值均来自受控离线矩阵。"""
    value = str(value if value is not None else "")
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def _template(record):
    """结项模板键使用 Excel「模板」原文，并由 report_template.name 关联正文。"""
    label = record["template_label"].strip()
    if label == "无需做":
        return ""
    if not label or len(label) > 128:
        raise ValueError(f"模板键为空或超出 128 字符：{record['sheet']} 第{record['excel_row']}行")
    return label


def _template_source(record):
    """把 Excel 模板名称对应到已整理的 Markdown 正文。"""
    label = _template(record)
    if not label:
        return None
    if label == "待填模板（仅表头版）":
        return V2_MD_DIR / "结项_待填模板_V2.md"
    filename = record["template_md"]
    if not filename:
        raise ValueError(f"模板未找到对应 MD：{record['sheet']} 第{record['excel_row']}行 {label}")
    if record["sheet"] == "结项通知-CN":
        return CN_MD_DIR / filename
    return V2_MD_DIR / (filename[:-3] + "_V2.md")


def build(data):
    lines = [
        "-- 结项 V2 替换草案（仅 close 域）；本文件默认 ROLLBACK，不会实际替换。",
        "-- 无需修改现有表结构：rule_key 最长 128 字符，多项匹配键使用 类型1｜等多项 及必要的区分词。",
        "-- 结项模板键取 Excel「模板」原文；「无需做」不分配汇报信，只随结项邮件抄送。",
        "-- 「待填模板（仅表头版）」正文来自 待填模板-仅表头版-示例.docx。",
        "-- 本草案先为 Excel 模板名补 report_template 正文，再替换 close 域规则。",
        "-- 正文仍需校对：CN 复审请求旧 MD 措辞有误，部分 US 草稿含固定日期。",
        "-- 地区码取自案号；完整 Excel 原键在规范化草表中；仍需确认 TIP 类型1回退匹配和模板正文。",
        "-- 规则表清理范围：report_rule / report_rule_map / report_rule_template 的 close 域。",
        "-- 不删除或覆盖已有 report_template、report_tasks 或 OA 域数据。",
        "START TRANSACTION;",
    ]
    counts = Counter()
    templates = {}
    for record in data["records"]:
        name = _template(record)
        if not name:
            continue
        source = _template_source(record)
        if not source.is_file():
            raise ValueError(f"模板正文文件不存在：{name} -> {source}")
        if name in templates and templates[name] != source:
            raise ValueError(f"同名模板对应不同正文：{name}")
        templates[name] = source
    for name, source in sorted(templates.items()):
        content = source.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(f"模板正文为空：{source}")
        lines.append(
            "INSERT INTO report_template (name, content, format, status, remark) "
            f"SELECT {q(name)}, {q(content)}, 'md', 1, "
            f"{q('结项V2；来源 ' + str(source.relative_to(ROOT)) + '；待校对')} "
            f"WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name={q(name)});"
        )
        counts["report_template"] += 1
    lines += [
        "DELETE FROM report_rule WHERE rule_domain='close';",
        "DELETE FROM report_rule_map WHERE rule_domain='close';",
        "DELETE FROM report_rule_template WHERE rule_domain='close';",
    ]
    used = set()
    for record in data["records"]:
        # 多项匹配行用短关联键；完整组合逐项见 map.match_key。
        rule_key = record["rule_key"]
        template = _template(record)
        for region in record["regions"]:
            signature = (region, rule_key)
            if signature in used:
                raise ValueError(f"重复规则键：{signature}")
            used.add(signature)
            remark = f"V2 {record['sheet']} 第{record['excel_row']}行；{record['template_label']}"
            lines.append(
                "INSERT INTO report_rule_template "
                "(rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES "
                f"('close', {q(region)}, {q(rule_key)}, {q(template)}, 0, 1, {q(remark)});"
            )
            counts["report_rule_template"] += 1
            for match_key in record["match_keys"]:
                if len(match_key) > 255:
                    raise ValueError(f"匹配键超过 255 字符：{signature} {match_key}")
                lines.append(
                    "INSERT INTO report_rule_map "
                    "(rule_domain, region, match_key, rule_key, status, remark) VALUES "
                    f"('close', {q(region)}, {q(match_key)}, {q(rule_key)}, 1, {q(remark)});"
                )
                counts["report_rule_map"] += 1
            # 精确客户优先于 5开头与 其他；与现有规则查询顺序一致。
            ordered = sorted(record["actions"].items(),
                             key=lambda item: (item[0] == "其他", item[0] == "5开头"))
            for seq, (customer, action) in enumerate(ordered):
                kind = action["action"]
                preparer = action.get("preparer", "")
                forward = action.get("forward") or {}
                if record["template_label"] == "无需做" and kind == "assign":
                    # 矩阵中 CN 20615 的三行写了「分配→胡梅」；业务确认
                    # 「无需做」只转发结项邮件，因此将原准备人转成抄送目标。
                    kind = "skip"
                    forward = {"to": [preparer], "cc": []}
                    preparer = ""
                fto = json.dumps(forward.get("to", []), ensure_ascii=False) if kind == "skip" else ""
                fcc = json.dumps(forward.get("cc", []), ensure_ascii=False) if kind == "skip" else ""
                lines.append(
                    "INSERT INTO report_rule "
                    "(rule_domain, region, rule_key, rule_variant, customer_code, action, "
                    "preparer, forward_to, forward_cc, seq, status, remark) VALUES "
                    f"('close', {q(region)}, {q(rule_key)}, '', {q(customer)}, "
                    f"{q(kind)}, {q(preparer)}, {q(fto)}, {q(fcc)}, {seq}, 1, {q(remark)});"
                )
                counts["report_rule"] += 1
    lines += [
        "-- 校验模板及新增 close 域行数。确认所有前置条件后，单独审核 COMMIT 版本。",
        "-- 应为 39；若不足，先核查已有同名但停用或正文为空的行。",
        f"SELECT COUNT(DISTINCT name) AS active_v2_template_rows FROM report_template "
        f"WHERE status=1 AND content IS NOT NULL AND TRIM(content)<>'' "
        f"AND name IN ({', '.join(q(n) for n in sorted(templates))});",
        "SELECT 'report_rule_template' AS table_name, COUNT(*) AS close_rows FROM report_rule_template WHERE rule_domain='close'",
        "UNION ALL SELECT 'report_rule_map', COUNT(*) FROM report_rule_map WHERE rule_domain='close'",
        "UNION ALL SELECT 'report_rule', COUNT(*) FROM report_rule WHERE rule_domain='close';",
        "ROLLBACK;",
    ]
    return "\n".join(lines) + "\n", dict(counts)


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    sql, counts = build(data)
    OUT.write_text(sql, encoding="utf-8")
    print(OUT)
    print(json.dumps(counts, ensure_ascii=False))


if __name__ == "__main__":
    main()
