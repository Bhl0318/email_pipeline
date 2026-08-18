#!/usr/bin/env python3
"""OA 分配 —— 本次 OA「人员安排建议」(≥3 组方案)，AI 生成。

候选人库来自 oa_personnel.collect_candidates（在职/离职 + 来源：本案撰写/本案历史OA/同族OA）。
把候选人 + 分配规则喂给 DeepSeek，**限定只能从候选人里选**（避免编人名），产出结构化 ≥3 组方案：
  [{id, label, responder, qc, note}]  —— 前端可点选自动填「答复负责人/QC」。

分配规则（OA_distribute 需求 2.4，第一阶段不含工作饱和度）：
  ①需 QC 一人 + 答复负责人一人；②优先本案撰写人或上次 OA 的人；
  ③有同族且本案首次 OA → 优先参与过同族 OA 的人；④原人离职 → 优先参与过同族 OA 的人；
  ⑤无同族且原人离职 → 优先同技术领域（饱和度一阶段不做）。

DeepSeek 不可达/欠费时返回 []（前端回退到「自定义方案」手工选人）。绝不抛异常。
"""
import json
import re
import sys

_RULES_TEXT = (
    "1. 需要安排 QC 一人、答复负责人一人；\n"
    "2. 优先安排本案的撰写人员或上一次 OA 的人员；\n"
    "3. 若存在此前的同族案件且本案为首次 OA，则优先安排参与过同族案件 OA 的人员；\n"
    "4. 若本案的此前人员存在离职，则优先安排参与过同族案件 OA 的人员；\n"
    "5. 若本案无同族且此前人员离职，则优先同技术领域的人员（工作饱和度第一阶段不考虑）。"
)


def _deepseek_schemes(candidates, tech_field=""):
    """候选人 + 规则 → DeepSeek 出 JSON 方案数组。失败返回 None。"""
    from openai import OpenAI
    from filter_oa_email import _DEEPSEEK_API_KEY, _DEEPSEEK_BASE_URL, _DEEPSEEK_MODEL

    lines = []
    for c in candidates:
        attr = "/".join([x for x in (c.get("duty"), c.get("level")) if x])
        lines.append(f"- {c['name']}（{attr or '职务职级未知'}，{c.get('status') or '在职状态未知'}；"
                     f"来源：{'、'.join(c.get('sources', [])) or '—'}）")
    cand_block = "\n".join(lines)
    prompt = (
        "你是资深专利 OA 任务分配分析官。请**仅从下面候选人库中**为本次 OA 挑选人员，给出人员安排建议。\n"
        "分配规则（按优先级）：\n" + _RULES_TEXT + "\n"
        f"本案技术领域：{tech_field or '（未提供）'}\n\n"
        "候选人库（只能从这里选，禁止编造库外姓名）：\n" + cand_block + "\n\n"
        "要求：\n"
        "- 每组方案含 答复负责人 1 人、QC 1 人（同一人不得兼两角色）；优先在职人员，离职者不作为首选。\n"
        "- 至少给 3 组方案，按推荐度从高到低；note 用一句话说明推荐理由（命中的规则/来源/在职情况）。\n"
        "- **只输出 JSON 数组**，元素形如 "
        '{"responder": "姓名", "qc": "姓名", "note": "理由"}，不要输出任何其它文字。'
    )
    try:
        client = OpenAI(api_key=_DEEPSEEK_API_KEY, base_url=_DEEPSEEK_BASE_URL)
        resp = client.chat.completions.create(
            model=_DEEPSEEK_MODEL, max_tokens=1200,
            messages=[{"role": "user", "content": prompt}])
        content = (resp.choices[0].message.content or "").strip()
        m = re.search(r"\[.*\]", content, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception as e:
        print(f"[oa_schemes] DeepSeek 方案生成失败: {e}", file=sys.stderr)
    return None


def build_assignment_schemes(project, tech_field="", execute=None):
    """生成本次 OA 人员安排建议（≥3 组）。无候选人或 DeepSeek 失败返回 []。绝不抛异常。
    返回 [{id, label, responder, qc, note}]（不含「自定义方案」，由上层补）。"""
    try:
        from oa_personnel import collect_candidates
        candidates = collect_candidates(project, execute=execute)
    except Exception as e:
        print(f"[oa_schemes] 候选池不可用: {e}", file=sys.stderr)
        return []
    if not candidates:
        print(f"[oa_schemes] {project} 无候选人（本案/同族无在库承办人），跳过方案生成", file=sys.stderr)
        return []

    raw = _deepseek_schemes(candidates, tech_field=tech_field)
    if not raw:
        return []

    valid_names = {c["name"] for c in candidates}
    labels = ["方案一", "方案二", "方案三", "方案四", "方案五", "方案六"]
    schemes = []
    for i, s in enumerate(raw):
        if not isinstance(s, dict):
            continue
        responder = (s.get("responder") or "").strip()
        qc = (s.get("qc") or "").strip()
        # 只保留候选库内的姓名，杜绝编造（库外名清空）
        responder = responder if responder in valid_names else ""
        qc = qc if qc in valid_names else ""
        if not responder and not qc:
            continue
        schemes.append({
            "id": f"ai-{i+1}",
            "label": labels[i] if i < len(labels) else f"方案{i+1}",
            "responder": responder,
            "qc": qc,
            "note": (s.get("note") or "").strip(),
        })
    return schemes


if __name__ == "__main__":
    _proj = sys.argv[1] if len(sys.argv) > 1 else "20618-0424US00"
    print(json.dumps(build_assignment_schemes(_proj), ensure_ascii=False, indent=2))
