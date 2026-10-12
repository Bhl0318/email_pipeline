#!/usr/bin/env python3
"""离线生成结项 V2 规则替换 SQL 草案；不会连接数据库。

本脚本只替换三个规则表的 close 域，不触及 OA、report_tasks 或共享模板正文。
生成文件默认以 ROLLBACK 结束。国别码从案号地区位提取；上线前需确认 TIP 的类型1回退匹配，
并完成 V2 Word 正文转换与审核，随后再决定是否提交事务。
"""

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs" / "结项V2规范化草表.json"
OUT = ROOT / "outputs" / "结项V2规则替换草案.sql"


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


def build(data):
    lines = [
        "-- 结项 V2 替换草案（仅 close 域）；本文件默认 ROLLBACK，不会实际替换。",
        "-- 无需修改现有表结构：rule_key 最长 128 字符，超长 Excel 匹配键用可读摘要。",
        "-- 结项模板键取 Excel「模板」原文；「无需做」不分配汇报信，只随结项邮件抄送。",
        "-- 「待填模板（仅表头版）」正文来自 待填模板-仅表头版-示例.docx。",
        "-- 启用前须将同名正文导入 report_template.name。",
        "-- 地区码取自案号；完整 Excel 原键在规范化草表中；仍需确认 TIP 类型1回退匹配和模板正文。",
        "-- 规则表清理范围：report_rule / report_rule_map / report_rule_template 的 close 域。",
        "-- 不删除 report_template、report_tasks 或 OA 域数据。",
        "START TRANSACTION;",
        "DELETE FROM report_rule WHERE rule_domain='close';",
        "DELETE FROM report_rule_map WHERE rule_domain='close';",
        "DELETE FROM report_rule_template WHERE rule_domain='close';",
    ]
    counts = Counter()
    used = set()
    for record in data["records"]:
        # 常规行使用 Excel 原匹配键；仅超长行使用可读摘要，完整匹配逐项见 map。
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
        "-- 校验新增 close 域行数。确认所有前置条件后，单独审核 COMMIT 版本。",
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
