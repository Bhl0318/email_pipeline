#!/usr/bin/env python3
"""结项邮件「抄送名单」规则 —— 从 close_report_rules.json 派生。

背景：OA 官文规则读原始官文邮件、skip 时转发原始邮件；而结项不是邮件触发，
而是 web 表单提交（案号 + 结项类型一 cls_task_1 + 结项类型二 cls_task_2），提交后系统
自动发结项邮件。所以结项规则里 skip 的 forward（to/cc）语义改为：**发结项邮件时把这些人加进抄送**。

规则（本次约定）：
- 只有 action=skip 的规则产生抄送：cc = forward.to + forward.cc 合并去重（全进 cc）。
- assign / ignore 不产生抄送（空）。

法域判定（与 close_report_rules._meta 一致）：案号含 EP→EP / 含 US→US / 含 WO→PCT / 含 CN→CN / 其余→空。
客户码解析优先级：精确客户码(前5位) → 「5开头」(客户号以5开头时) → 「其他」兜底。

用法：
  import close_cc
  rules = close_cc.load_rules()
  close_cc.resolve_cc(rules, "20618-0001CN00", "著录项目", "变更申请人")   # 单次查 → {region,combination,closeType,action,cc:[...]}
  close_cc.build_cc_map(rules)                                          # 整份派生表 {region:{combination:{客户码:[cc]}}}
"""
import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(_DIR, "close_report_rules.json")


def region_of(project):
    """案号 → 法域：含 EP→EP / 含 US→US / 含 WO→PCT / 含 CN→CN / 其余→''。"""
    p = (project or "").upper()
    for tok, reg in (("EP", "EP"), ("US", "US"), ("WO", "PCT"), ("CN", "CN")):
        if tok in p:
            return reg
    return ""


def _skip_cc(act):
    """一条规则 → 结项邮件抄送名单：仅 skip 取 forward.to+cc 合并去重；否则空。"""
    if not act or act.get("action") != "skip":
        return []
    fwd = act.get("forward") or {}
    cc, seen = [], set()
    for e in list(fwd.get("to") or []) + list(fwd.get("cc") or []):
        e = (e or "").strip()
        if e and e.lower() not in seen:
            seen.add(e.lower())
            cc.append(e)
    return cc


def load_rules(path=RULES_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_cc_map(rules):
    """整份派生表：{region: {combination: {客户码/5开头/其他: [cc...]}}}，仅收 skip 且 cc 非空的条目。
    供表单页直读；未出现的 region/combination/客户码 → 无抄送。"""
    out = {}
    for region, node in (rules or {}).items():
        if region.startswith("_") or not isinstance(node, dict):
            continue
        combos = node.get("combinations") or {}
        rmap = node.get("rules") or {}
        for combo, close_type in combos.items():
            crules = ((rmap.get(close_type) or {}).get("rules")) or {}
            cc_by_code = {}
            for code, act in crules.items():
                cc = _skip_cc(act)
                if cc:
                    cc_by_code[code] = cc
            if cc_by_code:
                out.setdefault(region, {})[combo] = cc_by_code
    return out


def resolve_cc(rules, project, task1, task2):
    """单次查：案号 + 结项类型一/二 → 结项邮件抄送名单。
    返回 {region, combination, closeType, action, cc:[...]}；查不到 → cc 为空。"""
    region = region_of(project)
    combo = f"{(task1 or '').strip()}_{(task2 or '').strip()}"
    node = (rules or {}).get(region) or {}
    close_type = (node.get("combinations") or {}).get(combo, "")
    crules = ((node.get("rules") or {}).get(close_type) or {}).get("rules") or {}
    code = (project or "")[:5]
    act = crules.get(code)
    if act is None and code.startswith("5") and "5开头" in crules:
        act = crules["5开头"]
    if act is None:
        act = crules.get("其他")
    return {"region": region, "combination": combo, "closeType": close_type,
            "action": (act or {}).get("action", ""), "cc": _skip_cc(act)}
