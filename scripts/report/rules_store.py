#!/usr/bin/env python3
"""从四张规则表重建「与 oa_report_rules.json / close_report_rules.json 完全同形」的 dict，
供分发代码读表而无需改下游解析逻辑。表结构见 DS/汇报信流程/汇报信规则数据表设计.md。

设计要点：
- build_oa_rules() 产出 {"_templates":{region:{ntype:[md,attach]}}, "CN":{...}, "US":{...}, "EP":{...}}，
  与 oa_report_rules.json 去掉 _meta 后完全等价；ntype 键按 rule_key + '@' + rule_variant 复原（变体空则无 @）。
- 动作复原：assign→{action,preparer}；skip→{action,forward:{to,cc}}；ignore→{action}。
- query 可注入（测试用 SQLite）；默认走 db_query.execute_params（atw）。
"""
import json


def _default_query(sql, params=()):
    from db_query import execute_params
    return execute_params(sql, params)


def _parse_list(s):
    s = (s or "").strip()
    if not s:
        return []
    try:
        v = json.loads(s)
        return v if isinstance(v, list) else [v]
    except Exception:
        return [x.strip() for x in s.split(",") if x.strip()]


def _action_of(row):
    a = row.get("action")
    if a == "assign":
        d = {"action": "assign", "preparer": row.get("preparer") or ""}
        # assign+转发：forward_to/cc 两列在 assign 语义下即 also_forward（非空才带）
        to, cc = _parse_list(row.get("forward_to")), _parse_list(row.get("forward_cc"))
        if to or cc:
            d["also_forward"] = {"to": to, "cc": cc}
        return d
    if a == "skip":
        return {"action": "skip", "forward": {
            "to": _parse_list(row.get("forward_to")), "cc": _parse_list(row.get("forward_cc"))}}
    return {"action": "ignore"}


def build_oa_rules(query=None):
    """重建 OA 官文规则 dict（同 oa_report_rules.json 形状，无 _meta）。表为空则返回 {} 供调用方回退。"""
    q = query or _default_query
    tpl = q("SELECT region, rule_key, template, attach_pdf FROM report_rule_template "
            "WHERE rule_domain='oa' AND status=1") or []
    rules = q("SELECT region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc "
              "FROM report_rule WHERE rule_domain='oa' AND status=1 "
              "ORDER BY region, rule_key, rule_variant, seq, id") or []
    if not rules and not tpl:
        return {}
    out = {"_templates": {}}
    for r in tpl:
        reg = r["region"]
        if reg.startswith("_"):
            continue
        out["_templates"].setdefault(reg, {})[r["rule_key"]] = [r.get("template") or "", bool(r.get("attach_pdf"))]
    for r in rules:
        reg = r["region"]
        var = (r.get("rule_variant") or "").strip()
        nk = r["rule_key"] + ("@" + var if var else "")
        out.setdefault(reg, {}).setdefault(nk, {})[r["customer_code"]] = _action_of(r)
    return out


def build_close_rules(query=None):
    """重建结项规则 dict（同 close_report_rules.json 形状，无 _meta）。表为空则返回 {}。
    结构：{region:{combinations:{combo:结项类型}, rules:{结项类型:{template,attach,rules:{客户:动作}}}}}。"""
    q = query or _default_query
    tpl = q("SELECT region, rule_key, template, attach_pdf FROM report_rule_template "
            "WHERE rule_domain='close' AND status=1") or []
    maps = q("SELECT region, match_key, rule_key FROM report_rule_map "
             "WHERE rule_domain='close' AND status=1 ORDER BY region, match_key") or []
    rules = q("SELECT region, rule_key, customer_code, action, preparer, forward_to, forward_cc "
              "FROM report_rule WHERE rule_domain='close' AND status=1 "
              "ORDER BY region, rule_key, seq, id") or []
    if not rules and not maps and not tpl:
        return {}
    out = {}

    def _node(reg):
        return out.setdefault(reg, {"combinations": {}, "rules": {}})

    tpl_by = {(r["region"], r["rule_key"]): r for r in tpl}
    for m in maps:
        _node(m["region"])["combinations"][m["match_key"]] = m["rule_key"]
    for r in rules:
        reg, ct = r["region"], r["rule_key"]
        node = _node(reg)["rules"].setdefault(ct, None)
        if node is None:
            t = tpl_by.get((reg, ct), {})
            node = {"template": (t.get("template") or None) or None,
                    "attach": bool(t.get("attach_pdf")), "rules": {}}
            _node(reg)["rules"][ct] = node
        node["rules"][r["customer_code"]] = _action_of(r)
    # 补：有模板/映射但无分派行的结项类型也建出（保持结构完整）
    for (reg, ct), t in tpl_by.items():
        rn = _node(reg)["rules"]
        if ct not in rn:
            rn[ct] = {"template": (t.get("template") or None) or None,
                      "attach": bool(t.get("attach_pdf")), "rules": {}}
    return out


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "oa"
    d = build_oa_rules() if which == "oa" else build_close_rules()
    print(json.dumps(d, ensure_ascii=False, indent=2))
