#!/usr/bin/env python3
"""OA 分配白名单 —— atw 表 oa_assign_whitelist 增删改查。

一行 = 某人在某(业务类型×档位×领域×梯队)下可安排。tier_level 由 tier 自动推。
维护页(web/whitelist.html)经 report/oa_whitelist.py 调这里，实时写 atw。
execute 可注入(测试用)，默认 db_query.execute。
"""
TABLE = "oa_assign_whitelist"
TIER_LV = {"QC": 0, "梯队1": 1, "梯队2": 2, "梯队3": 3}


def _lv(tier):
    return TIER_LV.get((tier or "").strip(), 99)


def _q(v):
    return str(v if v is not None else "").replace("'", "\\'")


def _get_execute(execute):
    if execute is not None:
        return execute
    from db_query import execute as _e
    return _e


COLS = ["biz_type", "tier", "grade", "field", "name_raw", "note", "flag"]


def list_all(execute=None):
    """全量返回，按 业务类型/梯队/档位/领域/姓名 排序。"""
    ex = _get_execute(execute)
    rows = ex(f"SELECT id, biz_type, tier, tier_level, grade, field, name_raw, note, flag "
              f"FROM {TABLE} ORDER BY biz_type, tier_level, grade, field, name_raw")
    return rows or []


def add(row, execute=None):
    """新增一行。row 为 dict(COLS 子集)；name_raw/biz_type/tier 必填。返回是否成功。"""
    ex = _get_execute(execute)
    if not (row.get("name_raw") and row.get("biz_type") and row.get("tier")):
        return False
    tier = row.get("tier", "")
    vals = {c: row.get(c, "") for c in COLS}
    def _v(c):
        return f"'{_q(vals[c])}'" if vals[c] != "" else "NULL"
    # username_zn：姓名从 users 表选出时同名回填（口径与 name_raw 一致）；未提供则 NULL
    uzn = (row.get("username_zn") or "").strip()
    uzn_sql = f"'{_q(uzn)}'" if uzn else "NULL"
    ex(f"INSERT INTO {TABLE} (biz_type, tier, tier_level, grade, field, name_raw, username_zn, note, flag, synced_at) "
       f"VALUES ('{_q(vals['biz_type'])}', '{_q(vals['tier'])}', {_lv(tier)}, "
       f"{_v('grade')}, {_v('field')}, '{_q(vals['name_raw'])}', {uzn_sql}, {_v('note')}, {_v('flag')}, NOW())")
    return True


def delete(row_id, execute=None):
    """按 id 删除。返回是否成功。"""
    ex = _get_execute(execute)
    try:
        rid = int(row_id)
    except (TypeError, ValueError):
        return False
    ex(f"DELETE FROM {TABLE} WHERE id={rid}")
    return True


def update(row_id, fields, execute=None):
    """按 id 更新给定列(COLS 子集)；改 tier 时同步 tier_level。返回是否成功。"""
    ex = _get_execute(execute)
    try:
        rid = int(row_id)
    except (TypeError, ValueError):
        return False
    sets = []
    for c in COLS:
        if c in fields:
            v = fields[c]
            sets.append(f"{c}=" + (f"'{_q(v)}'" if v not in (None, "") else "NULL"))
    if "tier" in fields:
        sets.append(f"tier_level={_lv(fields['tier'])}")
    if not sets:
        return False
    sets.append("synced_at=NOW()")
    ex(f"UPDATE {TABLE} SET {', '.join(sets)} WHERE id={rid}")
    return True
