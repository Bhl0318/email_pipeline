"""US 递交质量埋点（seeded error / 校验项）——纯逻辑，不含 DB/流程副作用。

机制：对抽样的真实案，在一个可审字段里植入"故意错值 B"（原值 A 记下来）；
出口发送前判定该字段当前值——仍等于 B ＝ 漏检（拦截，逼改，B 绝不出门），
不等于 B ＝ 已捕获（放行）。安全线由调用方在出口处"仍==B 就拦截"保证。

本模块只负责：抽样决定 / 选字段 / 造错值 / 判定，不落库、不改流程。
"""
import os
import json
import random

SEED_RATE = 0.20     # (机械版遗留，AI 版不用)
SEED_MAX = 3         # 每案最多埋点数；实际 0~min(SEED_MAX, 可埋字段数) 随机

# 可播种字段池：路径（点号 + 数字下标定位 fields_json）+ 人可读标签。
# 只选"可审、改了不影响生成、还原无副作用、且为拉丁/数字（错一位/一字母仍是可信错值）"的字段；
# 不含中文字段（拉丁替换会变乱码、太明显）、不含代码/下拉/驱动生成的字段（国别、实体、落地方式、
# 续案类型等，改了会崩或不可信）。
POOL = [
    {"path": "priorities.0.priority_no",           "label": "优先权号"},
    {"path": "priorities.0.priority_date",         "label": "优先权日"},
    {"path": "priorities.0.access_code",           "label": "优先权 DAS 码"},
    {"path": "applicants.0.applicant_name_en",     "label": "申请人英文名"},
    {"path": "applicants.0.address1",              "label": "申请人地址1（英文）"},
    {"path": "applicants.0.city_en",               "label": "申请人城市（英文）"},
    {"path": "applicants.0.province_city_en_us",   "label": "申请人州/省（英文）"},
    {"path": "applicants.0.postcode",              "label": "申请人邮编"},
    {"path": "inventors.0.last_name_en",           "label": "发明人姓（英文）"},
    {"path": "inventors.0.first_name_en",          "label": "发明人名（英文）"},
    {"path": "case_info.case_name_en",             "label": "申请名称（英文）"},
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


# ─────────────── AI（DeepSeek）造错版 ───────────────
_REPORT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ai_cfg():
    """DeepSeek 配置：email_config.submission.qa_ai 优先，退环境变量/默认。"""
    key = os.environ.get("DEEPSEEK_API_KEY") or "REDACTED_API_KEY"
    base, model = "https://api.deepseek.com", "deepseek-chat"
    try:
        with open(os.path.join(_REPORT_DIR, "email_config.json"), encoding="utf-8") as f:
            ai = (json.load(f).get("submission") or {}).get("qa_ai") or {}
        key = ai.get("api_key") or key
        base = ai.get("base_url") or base
        model = ai.get("model") or model
    except Exception:
        pass
    return key, base, model


def _candidates(fields):
    """白名单里"存在且非空文本"的可埋字段。"""
    out = []
    for item in POOL:
        v = get_by_path(fields, item["path"])
        if isinstance(v, str) and v.strip():
            out.append({"path": item["path"], "label": item["label"], "value": v})
    return out


def ai_make_seeds(fields, n_max=SEED_MAX, rng=random):
    """AI(DeepSeek) 造错版：本地随机定"埋几个/埋哪些"(0~min(n_max,可埋数))，
    让 AI 为选中字段各造一处"貌似合理、不太明显"的错值；就地把 fields 改成错值 B，
    返回 [{path,label,value_a,value_b}]。best-effort：无候选/AI失败/无合格产出 → []（不改 fields）。"""
    cands = _candidates(fields)
    if not cands:
        return []
    n = rng.randint(0, min(n_max, len(cands)))
    if n == 0:
        return []
    picks = rng.sample(cands, n)
    payload = [{"path": p["path"], "label": p["label"], "value": p["value"]} for p in picks]
    prompt = (
        "你在做专利递交著录数据的质量抽检：给下面每个字段各造一个「貌似合理、不太明显」的错误值，"
        "用于检验人工是否认真核对。要求：\n"
        "1) 错误要细微可信(如姓名拼写差一两个字母、号码/邮编差一位数字、城市换成邻近城市、名称个别单词改动)，不要明显缺失或乱码；\n"
        "2) 保持与原值同类型同格式(数字仍是数字、日期仍是合法日期)；\n"
        "3) 每个错值必须与原值不同；\n"
        "4) 只输出 JSON 对象，键=path，值=错误值字符串，不要多余解释。\n\n"
        f"字段：\n{json.dumps(payload, ensure_ascii=False)}"
    )
    try:
        from openai import OpenAI
        key, base, model = _ai_cfg()
        client = OpenAI(api_key=key, base_url=base)
        resp = client.chat.completions.create(
            model=model, temperature=1.0, timeout=40,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"})
        data = json.loads(resp.choices[0].message.content or "{}")
    except Exception as e:  # noqa: BLE001
        import sys
        print(f"[qa_seed] AI 造错失败(不播): {e}", file=sys.stderr)
        return []
    seeds = []
    for p in picks:
        wrong = data.get(p["path"])
        if isinstance(wrong, str) and wrong.strip() and wrong.strip() != p["value"]:
            set_by_path(fields, p["path"], wrong.strip())
            seeds.append({"path": p["path"], "label": p["label"],
                          "value_a": p["value"], "value_b": wrong.strip()})
    return seeds
