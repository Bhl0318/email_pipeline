"""US 递交质量埋点（seeded error / 校验项）——纯逻辑，不含 DB/流程副作用。

机制：对抽样的真实案，在一个可审字段里植入"故意错值 B"（原值 A 记下来）；
出口发送前判定该字段当前值——仍等于 B ＝ 漏检（拦截，逼改，B 绝不出门），
不等于 B ＝ 已捕获（放行）。安全线由调用方在出口处"仍==B 就拦截"保证。

本模块只负责：抽样决定 / 选字段 / 造错值 / 判定，不落库、不改流程。
"""
import random

SEED_RATE = 0.15   # 抽样比例（10–20% 取中）

# 可播种字段池：路径（点号 + 数字下标定位 fields_json）+ 人可读标签。
# 只选"可审、改了不影响生成、还原无副作用"的字段。
POOL = [
    {"path": "priorities.0.priority_no",     "label": "优先权号"},
    {"path": "priorities.0.priority_date",   "label": "优先权日"},
    {"path": "applicants.0.city_en",         "label": "申请人城市"},
    {"path": "applicants.0.postcode",        "label": "申请人邮编"},
    {"path": "inventors.0.last_name_en",     "label": "发明人姓"},
]


def get_by_path(obj, path):
    """按 'a.0.b' 取值；任一段缺失返回 None。"""
    cur = obj
    for part in path.split("."):
        if part.isdigit():
            if not isinstance(cur, list) or int(part) >= len(cur):
                return None
            cur = cur[int(part)]
        else:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        if cur is None:
            return None
    return cur


def set_by_path(obj, path, val):
    """按 'a.0.b' 写值；中间段须已存在（播种前用 get_by_path 确认过）。"""
    parts = path.split(".")
    cur = obj
    for part in parts[:-1]:
        cur = cur[int(part)] if part.isdigit() else cur[part]
    last = parts[-1]
    if last.isdigit():
        cur[int(last)] = val
    else:
        cur[last] = val


def _mutate(s, rng=random):
    """把字符串改成"必不相同"的错值：换掉一个字母/数字（同类替换，保持大小写）。
    无字母数字则末尾加 X 兜底。用于优先权号/日期/城市/邮编/姓名。"""
    s = str(s)
    idxs = [i for i, c in enumerate(s) if c.isalnum()]
    if not idxs:
        return s + "X"
    i = rng.choice(idxs)
    c = s[i]
    if c.isdigit():
        repl = rng.choice([d for d in "0123456789" if d != c])
    else:
        cand = [x for x in "abcdefghijklmnopqrstuvwxyz" if x != c.lower()]
        r = rng.choice(cand)
        repl = r.upper() if c.isupper() else r
    return s[:i] + repl + s[i + 1:]


def maybe_make_seed(fields, rate=SEED_RATE, rng=random):
    """按 rate 抽样：命中则从池里挑一个"存在且非空"的字段，把它改成错值 B，
    返回种子 {path,label,value_a,value_b}（同时已就地把 fields 里该字段改成 B）；
    未命中 / 无可播字段 / 造值失败 → None（不改 fields）。"""
    if rng.random() >= rate:
        return None
    cands = []
    for item in POOL:
        v = get_by_path(fields, item["path"])
        if isinstance(v, str) and v.strip():
            cands.append((item, v))
    if not cands:
        return None
    item, a = rng.choice(cands)
    b = _mutate(a, rng=rng)
    if b == a:
        return None
    set_by_path(fields, item["path"], b)
    return {"path": item["path"], "label": item["label"], "value_a": a, "value_b": b}


def check_outcome(fields, seed):
    """出口判定：当前值仍等于 B → 'missed'（漏检）；否则 'caught'（已捕获/已改）。"""
    cur = get_by_path(fields, seed.get("path"))
    return "missed" if (cur is not None and str(cur) == str(seed.get("value_b"))) else "caught"
