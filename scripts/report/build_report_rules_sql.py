#!/usr/bin/env python3
"""把现有汇报信规则(oa_report_rules.json + close_report_rules.json)与模板 md 转成 INSERT SQL，
供流程人员一次性导入四张规则表（设计见 DS/汇报信流程/汇报信规则数据表设计.md）。

四表：
  report_template        —— 模板 md 正文（按 basename，79 个）
  report_rule_template   —— 模板层（rule_domain,region,rule_key → 模板名+attach）
  report_rule_map        —— 分类映射（结项 组合→结项类型）
  report_rule            —— 分派层（rule_key+客户→动作；OA 通知类型按 '@' 拆基名+次数变体）

改完规则/模板后重跑同步：
  python3 build_report_rules_sql.py    → 生成同目录 import_report_rules.sql
"""
import json
import os
import glob

DIR = os.path.dirname(os.path.abspath(__file__))
MD_DIR = os.path.join(DIR, "..", "templates", "md")
OUT = os.path.join(DIR, "import_report_rules.sql")


def q(s):
    """SQL 单引号字符串（'' 转义；模板正文已确认无反斜杠）。"""
    return "'" + str("" if s is None else s).replace("'", "''") + "'"


def jarr(lst):
    return json.dumps(list(lst or []), ensure_ascii=False)


def main():
    oa = json.load(open(os.path.join(DIR, "oa_report_rules.json"), encoding="utf-8"))
    close = json.load(open(os.path.join(DIR, "close_report_rules.json"), encoding="utf-8"))
    L = []
    L.append("-- 汇报信规则初始数据导入（由 build_report_rules_sql.py 生成）")
    L.append("-- 四表：report_template / report_rule_template / report_rule_map / report_rule")
    L.append("-- 初次全量导入前如需清空，取消下面注释：")
    for t in ("report_template", "report_rule_template", "report_rule_map", "report_rule"):
        L.append(f"-- TRUNCATE TABLE {t};")
    L.append("")

    # ① report_template：md 正文
    L.append("-- ① report_template：模板 md 正文（按 basename）")
    n_tpl = 0
    for p in sorted(glob.glob(os.path.join(MD_DIR, "**", "*.md"), recursive=True)):
        name = os.path.basename(p)
        content = open(p, encoding="utf-8").read()
        L.append("INSERT INTO report_template (name, content, format, status, remark) VALUES ("
                 + f"{q(name)}, {q(content)}, 'md', 1, '');")
        n_tpl += 1
    L.append("")

    # ② report_rule_template：OA _templates + close 各结项类型 template
    L.append("-- ② report_rule_template：模板层（规则键→模板名+是否附PDF）")
    n_rt = 0
    for reg, types in oa.get("_templates", {}).items():
        if reg.startswith("_"):
            continue
        for base, v in types.items():
            md = v[0] if isinstance(v, list) and v else ""
            attach = 1 if (isinstance(v, list) and len(v) > 1 and v[1]) else 0
            L.append("INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ("
                     + f"'oa', {q(reg)}, {q(base)}, {q(md)}, {attach}, 1, '');")
            n_rt += 1
    for reg, node in close.items():
        if reg.startswith("_") or not isinstance(node, dict):
            continue
        for ctype, cfg in (node.get("rules") or {}).items():
            md = cfg.get("template")
            if not md:
                continue
            attach = 1 if cfg.get("attach") else 0
            L.append("INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ("
                     + f"'close', {q(reg)}, {q(ctype)}, {q(md)}, {attach}, 1, '');")
            n_rt += 1
    L.append("")

    # ③ report_rule_map：close combination→结项类型
    L.append("-- ③ report_rule_map：分类映射（结项 组合→结项类型）")
    n_map = 0
    for reg, node in close.items():
        if reg.startswith("_") or not isinstance(node, dict):
            continue
        for combo, ctype in (node.get("combinations") or {}).items():
            L.append("INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ("
                     + f"'close', {q(reg)}, {q(combo)}, {q(ctype)}, 1, '');")
            n_map += 1
    L.append("")

    # ④ report_rule：OA 分派 + close 分派
    L.append("-- ④ report_rule：分派层（规则键+客户→动作）")
    n_rule = [0]

    def emit(domain, reg, rule_key, variant, cust, act, seq):
        action = act.get("action", "")
        preparer = act.get("preparer", "") if action == "assign" else ""
        fto = fcc = ""
        if action == "skip":
            fwd = act.get("forward") or {}
            fto, fcc = jarr(fwd.get("to")), jarr(fwd.get("cc"))
        L.append("INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ("
                 + f"{q(domain)}, {q(reg)}, {q(rule_key)}, {q(variant)}, {q(cust)}, {q(action)}, {q(preparer)}, {q(fto)}, {q(fcc)}, {seq}, 1, '');")
        n_rule[0] += 1

    for reg in ("CN", "US", "EP"):
        for ntype_key, custmap in (oa.get(reg) or {}).items():
            base, _, variant = ntype_key.partition("@")
            for i, (cust, act) in enumerate(custmap.items()):
                emit("oa", reg, base, variant, cust, act, i)
    for reg, node in close.items():
        if reg.startswith("_") or not isinstance(node, dict):
            continue
        for ctype, cfg in (node.get("rules") or {}).items():
            for i, (cust, act) in enumerate((cfg.get("rules") or {}).items()):
                emit("close", reg, ctype, "", cust, act, i)
    L.append("")

    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"生成 {OUT}")
    print(f"report_template={n_tpl}  report_rule_template={n_rt}  report_rule_map={n_map}  report_rule={n_rule[0]}")


if __name__ == "__main__":
    main()
