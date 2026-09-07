"""rule_engine 用法示例（离线）：分级查表 + 兜底。

复刻 OA 分派规则的用法：按 (国别, 官文类型, 客户码) 查动作，
客户码精确 → 5开头 → 其他 依次兜底，类型下若有 "*" 则全部同规则。

运行：python3 scripts/reusable/examples/rule_engine_demo.py
"""
import os
import sys

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "business"))
from rule_engine import resolve  # noqa: E402

# 规则表（实际用 load_rules 从 oa_report_rules.json 读；这里内联示意）
RULES = {
    "CN": {
        "审查意见通知书@1": {
            "20849": {"action": "assign", "preparer": "任惠"},   # 精确客户码
            "5开头":  {"action": "skip"},                        # 5 开头客户
            "其他":   {"action": "assign", "preparer": "王晶"},   # 兜底
        },
        "补正通知书": {"*": {"action": "ignore"}},                # 所有客户同规则
    },
}


def resolve_oa(region, rule_type, project):
    """业务层：客户码=案号前5位；5开头才试"5开头"，最后试"其他"。"""
    code = (project or "")[:5]
    fallbacks = (["5开头"] if code.startswith("5") else []) + ["其他"]
    return resolve(RULES, [region, rule_type, code], fallbacks=fallbacks)


if __name__ == "__main__":
    print("精确命中 :", resolve_oa("CN", "审查意见通知书@1", "20849-0032CN01"))
    # -> {'action': 'assign', 'preparer': '任惠'}
    print("5开头兜底:", resolve_oa("CN", "审查意见通知书@1", "50021-0001CN00"))
    # -> {'action': 'skip'}
    print("其他兜底 :", resolve_oa("CN", "审查意见通知书@1", "30011-0002CN00"))
    # -> {'action': 'assign', 'preparer': '王晶'}
    print("通配符   :", resolve_oa("CN", "补正通知书", "任意客户码"))
    # -> {'action': 'ignore'}
    print("类型缺失 :", resolve_oa("CN", "不存在的类型", "20849-x"))
    # -> None
