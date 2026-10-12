#!/usr/bin/env python3
"""结项邮件「抄送名单」规则 —— 从规则表或 close_report_rules.json 派生。

背景：OA 官文规则读原始官文邮件、skip 时转发原始邮件；而结项不是邮件触发，
而是 web 表单提交（案号 + 结项类型一 cls_task_1 + 结项类型二 cls_task_2），提交后系统
自动发结项邮件。所以结项规则里 skip 的 forward（to/cc）语义改为：**发结项邮件时把这些人加进抄送**。

规则（本次约定）：
- 只有 action=skip 的规则产生抄送：cc = forward.to + forward.cc 合并去重（全进 cc）。
- assign / ignore 不产生抄送（空）。

法域判定：从完整案号的地区位置取两位代码；V2 使用 CN/CM/CS/US/DS/PR/WO/DM。
客户码解析优先级：精确客户码(前5位) → 「5开头」(客户号以5开头时) → 「其他」兜底。

用法：
  import close_cc
  rules = close_cc.load_rules()
  close_cc.resolve_cc(rules, "20618-0001CN00", "著录项目", "变更申请人")   # 单次查 → {region,combination,closeType,action,cc:[...]}
  close_cc.build_cc_map(rules)                                          # 整份派生表 {region:{combination:{客户码:[cc]}}}
"""
import json
import os
import re

_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(_DIR, "close_report_rules.json")
_PROJECT_RE = re.compile(r"^[A-Z0-9]{5}-[A-Z0-9]{4}([A-Z]{2})[A-Z0-9]{2}$", re.I)
_REGIONS = {"CN", "CM", "CS", "US", "DS", "PR", "WO", "DM", "EP"}


def region_of(project):
    """按案号固定位置提取地区码；兼容数字/字母客户码和 -Hxxx 案号。"""
    match = _PROJECT_RE.fullmatch((project or "").strip())
    code = match.group(1).upper() if match else ""
    return code if code in _REGIONS else ""


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


def load_rules(path=None):
    """默认优先读结项规则表；表空或查询失败时回退 JSON。

    显式传入 path 时直接读取该文件，便于离线核对规则。
    """
    if path is None:
        try:
            import rules_store
            rules = rules_store.build_close_rules()
            if rules and any(region in rules for region in ("CN", "US", "EP", "PCT")):
                return rules
        except Exception:
            pass
        path = RULES_FILE
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


def resolve_cc(rules, project, task1, task2, region=None):
    """单次查：案号 + 结项类型一/二 → 结项邮件抄送名单。
    从案号读取 V2 地区码；先按 类型1_类型2，未命中再按 仅类型1。
    返回 {region, combination, closeType, action, cc:[...]}；查不到 → cc 为空。"""
    explicit_region = (region or "").strip().upper()
    region = region_of(project) or explicit_region
    if region == "WO" and region not in (rules or {}) and "PCT" in (rules or {}):
        region = "PCT"  # 兼容旧 JSON 中 PCT 作为 WO 分组名
    task1 = (task1 or "").strip()
    combo = f"{task1}_{(task2 or '').strip()}"
    node = (rules or {}).get(region) or {}
    combinations = node.get("combinations") or {}
    close_type = combinations.get(combo) or combinations.get(task1, "")
    crules = ((node.get("rules") or {}).get(close_type) or {}).get("rules") or {}
    code = (project or "")[:5]
    act = crules.get(code)
    if act is None and code.startswith("5") and "5开头" in crules:
        act = crules["5开头"]
    if act is None:
        act = crules.get("其他")
    return {"region": region, "combination": combo, "closeType": close_type,
            "action": (act or {}).get("action", ""), "cc": _skip_cc(act)}
