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

# 人员安排建议默认指令（外部编辑系统未配置时回退，= 原硬编码）。技术领域/候选人库由代码在其后追加。
DEFAULT_SCHEMES_INSTRUCTION = (
    "你是资深专利 OA 任务分配分析官。请**仅从随后给出的候选人库中**为本次 OA 挑选人员，给出人员安排建议。\n"
    "分配规则（按优先级）：\n"
    "1. 需要安排 QC 一人、答复负责人一人；\n"
    "2. 优先安排本案的撰写人员或上一次 OA 的人员；\n"
    "3. 若存在此前的同族案件且本案为首次 OA，则优先安排参与过同族案件 OA 的人员；\n"
    "4. 若本案的此前人员存在离职，则优先安排参与过同族案件 OA 的人员；\n"
    "5. 若本案无同族且此前人员离职，则优先同技术领域的人员（工作饱和度第一阶段不考虑）。\n"
    "要求：\n"
    "- 每组方案含 答复负责人 1 人、QC 1 人（同一人不得兼两角色）；优先在职人员，离职者不作为首选。\n"
    "- 至少给 3 组方案，按推荐度从高到低；note 用一句话说明推荐理由（命中的规则/来源/在职情况）。\n"
    "- **只能从候选人库里选人，禁止编造库外姓名**。\n"
    "- **只输出 JSON 数组**，元素形如 "
    '{"responder": "姓名", "qc": "姓名", "note": "理由"}，不要输出任何其它文字。'
)


def _schemes_instruction():
    """人员安排建议指令：优先读 atw 表 zxassist_result_instruction(mtype='oa_schemes') 的 instruction；
    读不到/为空/DB 异常回退 DEFAULT_SCHEMES_INSTRUCTION（重新生成时即用最新编辑的指令）。"""
    try:
        from db_query import execute
        rows = execute("SELECT instruction FROM zxassist_result_instruction WHERE mtype = 'oa_schemes'")
        if rows and (rows[0].get("instruction") or "").strip():
            return rows[0]["instruction"]
    except Exception as e:
        print(f"[oa_schemes] 读外部指令失败，用默认: {e}", file=sys.stderr)
    return DEFAULT_SCHEMES_INSTRUCTION


def _grade(project, region):
    """案号+地区 → 白名单档位。5/6 开头→普及；否则 US/EP→海外、CN→标准。取不到返回空。"""
    p = (project or "").strip()
    if p[:1] in ("5", "6"):
        return "普及"
    reg = (region or "").upper()
    if not reg:
        pu = p.upper()
        reg = "US" if "US" in pu else "EP" if "EP" in pu else "CN" if "CN" in pu else ""
    if reg in ("US", "EP"):
        return "海外"
    if reg == "CN":
        return "标准"
    return ""


def _cand_block(candidates):
    lines = []
    for c in candidates:
        attr = "/".join([x for x in (c.get("duty"), c.get("level")) if x])
        lines.append(f"- {c['name']}（{attr or '职务职级未知'}，{c.get('status') or '在职状态未知'}；"
                     f"来源：{'、'.join(c.get('sources', [])) or '—'}）")
    return "\n".join(lines)


def _deepseek(prompt):
    from openai import OpenAI
    from filter_oa_email import _DEEPSEEK_API_KEY, _DEEPSEEK_BASE_URL, _DEEPSEEK_MODEL
    try:
        client = OpenAI(api_key=_DEEPSEEK_API_KEY, base_url=_DEEPSEEK_BASE_URL,
                        timeout=180.0, max_retries=0)
        resp = client.chat.completions.create(
            model=_DEEPSEEK_MODEL, max_tokens=1400,
            messages=[{"role": "user", "content": prompt}])
        if not resp.choices or not resp.choices[0].message:
            raise ValueError("DeepSeek 返回 HTTP 200，但没有可用的分配方案")
        content = (resp.choices[0].message.content or "").strip()
        m = re.search(r"\[.*\]", content, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception as e:
        print(f"[oa_schemes] DeepSeek 方案生成失败: {e}", file=sys.stderr)
    return None


def _deepseek_schemes(candidates, tech_field=""):
    """无白名单时的兜底：仅候选池 + 规则。"""
    prompt = (_schemes_instruction().rstrip() + "\n\n"
              f"【本案技术领域】\n{tech_field or '（未提供）'}\n\n"
              "【候选人库（只能从这里选，禁止编造库外姓名）】\n" + _cand_block(candidates))
    return _deepseek(prompt)


def _deepseek_schemes_wl(candidates, whitelist, grade, report_md):
    """有白名单：先判领域→从该领域白名单选人；连续性候选(本案/同族承办)优先、梯队1优先。"""
    cont = {c["name"] for c in candidates}
    by_field = {}
    for w in whitelist:
        by_field.setdefault(w.get("field") or "(未分领域)", []).append(w)
    wl_lines = []
    for fld, ws in by_field.items():
        wl_lines.append(f"◆ 领域【{fld}】")
        for w in sorted(ws, key=lambda x: x.get("tier_level", 99)):
            mark = "，本案/同族承办" if w["name"] in cont else ""
            note = f"，{w['note']}" if w.get("note") else ""
            wl_lines.append(f"  - {w['name']}（{w.get('tier','')}{mark}{note}）")
    wl_block = "\n".join(wl_lines)
    # 连续性候选（本案撰写/上次OA/同族承办人）：不受领域限制，答复负责人优先从这里取
    cont_lines = []
    for c in candidates:
        attr = "/".join(x for x in (c.get("duty"), c.get("level")) if x) or "职务职级未知"
        src = "/".join(c.get("sources", [])) or "承办"
        cont_lines.append(f"  - {c['name']}（{attr}，{c.get('status') or '在职状态未知'}；{src}）")
    cont_block = "\n".join(cont_lines) if cont_lines else "  (无)"
    # 人员负荷（读 Confluence 负荷页；连不上则空，不阻断）
    try:
        from oa_workload import workload_block
        wl_load = workload_block()
    except Exception:
        wl_load = ""
    load_part = ("\n\n" + wl_load + "\n\n【负荷要求】同等条件下优先负荷低(饱和度%小)的人；"
                 "避开请假/培训人员；在 note 里注明所选人的负荷情况。") if wl_load else ""
    prompt = (
        _schemes_instruction().rstrip() + "\n\n"
        "【本案档位】" + (grade or "未知") + "（白名单已按此档位给出）\n\n"
        "【判定要求】先据下方报告判断本案技术领域属 通用/结构/生化 中的哪一个。\n"
        "答复负责人选人顺序（**连续性优先，不受领域限制**）：\n"
        "  1) **优先取【连续性候选】里在职的人**（即上次OA/本案·同族承办人；即使其不在本案判定领域的白名单，也应优先，以保证承办连续性）；\n"
        "  2) 连续性候选无在职合适人 → 从**本案判定领域**的白名单选，梯队1→2→3；\n"
        "QC 选人：优先取【连续性候选】里适合任 QC 的在职人员，否则取该领域白名单 QC 档；同一人不得兼两角色。\n"
        "报告的「历史 OA 记录」标明了上次的答复负责人/QC，请据此还原承办组合（负责人对负责人、QC 对 QC）。\n"
        "**推荐人必须出自【连续性候选】或【白名单】，禁止编造库外姓名。**\n"
        "每组方案的 JSON 里额外带一个字段 \"field\"，值为你判定的技术领域（通用/结构/生化）。\n\n"
        "【案件报告（判领域 + 看历史OA承办人用，节选）】\n" + (report_md or "")[:4000] + "\n\n"
        "【连续性候选（上次OA/本案·同族承办人，不受领域限制，答复负责人优先从这里取；在职优先，离职不作首选）】\n"
        + cont_block + "\n\n"
        "【本档位白名单（按领域/梯队；连续性候选取不到时，从本案判定领域的白名单选）】\n" + wl_block
        + load_part
    )
    return _deepseek(prompt)


def _existing_usernames(names, execute=None):
    """从 names 里筛出确实在 users.username_zn 的（AI 组合的人名必须经 users 验证）。
    一次 IN 查询；DB 异常/无结果解析失败时**不拦**（原样返回），避免误清空。"""
    names = {(n or "").strip() for n in names if (n or "").strip()}
    if not names:
        return set()
    try:
        ex = execute
        if ex is None:
            from db_query import execute as ex
        vals = ",".join("'" + n.replace("'", "\\'") + "'" for n in names)
        rows = ex(f"SELECT username_zn FROM users WHERE username_zn IN ({vals})")
        if isinstance(rows, str) or rows is None:
            return names   # 查询异常 → 不拦
        got = {(r.get("username_zn") or "").strip() for r in rows if r.get("username_zn")}
        return got or names   # 一个都没查到多半是查询问题 → 不拦
    except Exception as e:
        print(f"[oa_schemes] 人名 users 验证失败(不拦): {e}", file=sys.stderr)
        return names


def build_assignment_schemes(project, region="", report_md="", execute=None):
    """生成本次 OA 人员安排建议（≥3 组）。绝不抛异常，失败返回 []。
    白名单可用时按 档位(案号/地区)×领域(DeepSeek判) 选人；否则退回候选池逻辑。
    返回 [{id, label, responder, qc, note}]（不含「自定义方案」，由上层补）。"""
    try:
        from oa_personnel import collect_candidates
        candidates = collect_candidates(project, execute=execute)
    except Exception as e:
        print(f"[oa_schemes] 候选池不可用: {e}", file=sys.stderr)
        candidates = []

    # 白名单（OA实质 × 本案档位）
    grade = _grade(project, region)
    whitelist = []
    if grade:
        try:
            from oa_whitelist_store import list_for
            whitelist = list_for("OA实质", grade, execute=execute)
        except Exception as e:
            print(f"[oa_schemes] 读白名单失败: {e}", file=sys.stderr)

    # AI 组合的人名必须都在 users.username_zn：先把 白名单/候选池 过滤到 users 里存在的人，
    # 这样喂给 DeepSeek 的、校验用的、兜底补的，全是验证过的人名。
    _names = {w.get("name") for w in whitelist} | {c.get("name") for c in candidates}
    _valid_users = _existing_usernames(_names, execute)
    whitelist = [w for w in whitelist if w.get("name") in _valid_users]
    candidates = [c for c in candidates if c.get("name") in _valid_users]

    if whitelist:
        print(f"[oa_schemes] {project} 候选人和白名单已读取；开始生成方案", file=sys.stderr)
        raw = _deepseek_schemes_wl(candidates, whitelist, grade, report_md)
        # 合法名单 = 白名单 ∪ 连续性候选(本案/同族承办人)：后者是 projects 查出的真人，
        # 虽未必在白名单该格内，但连续性规则允许选，故不清空（只清真正编造的库外名）。
        valid_names = {w["name"] for w in whitelist} | {c["name"] for c in candidates}
        print(f"[oa_schemes] {project} 档位={grade} 白名单{len(whitelist)}人 → 按白名单选人", file=sys.stderr)
    else:
        if not candidates:
            print(f"[oa_schemes] {project} 无白名单且无候选人，跳过", file=sys.stderr)
            return []
        print(f"[oa_schemes] {project} 候选人已读取；开始生成方案", file=sys.stderr)
        raw = _deepseek_schemes(candidates)   # 兜底：候选池
        valid_names = {c["name"] for c in candidates}
        print(f"[oa_schemes] {project} 无白名单(档位={grade or '未知'})，退回候选池", file=sys.stderr)

    if not raw:
        return []
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
        field = (s.get("field") or "").strip()   # DeepSeek 判定的技术领域，供兜底补人
        # 兜底：角色空 → 先从连续性候选(在职)补，再从同技术领域白名单补（同领域补不到再跨领域）
        if whitelist and (not responder or not qc):
            responder, qc = _fallback_fill(whitelist, field, responder, qc, candidates)
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


def _fallback_fill(whitelist, field, responder, qc, candidates=None):
    """角色空时补人：**先从连续性候选(在职)补**（不受领域限制，落实规则②/④），
    再从白名单补（负责人梯队1→2→3、QC 取 QC 档；优先同 field，补不到跨 field）；避开同人。"""
    cont = [c["name"] for c in (candidates or []) if c.get("name") and c.get("status") != "离职"]

    def pool(is_qc, fld):
        rows = [w for w in whitelist
                if (w.get("tier") == "QC") == is_qc and (not fld or w.get("field") == fld)]
        return [w["name"] for w in sorted(rows, key=lambda x: x.get("tier_level", 99))]
    if not responder:
        for n in cont + pool(False, field) + (pool(False, "") if field else []):
            if n and n != qc:
                responder = n
                break
    if not qc:
        for n in cont + pool(True, field) + (pool(True, "") if field else []):
            if n and n != responder:
                qc = n
                break
    return responder, qc


def render_schemes_md(schemes):
    """把人员安排方案渲染成报告「六、本次OA人员安排建议」markdown。跳过「自定义方案」；空则返回空串。"""
    real = [s for s in (schemes or []) if s and s.get("id") != "custom"]
    if not real:
        return ""
    lines = ["## 本次OA人员安排建议", ""]
    for s in real:
        lines.append(f"**{s.get('label', '方案')}**")
        lines.append(f"- 答复负责人：{s.get('responder') or '—'}")
        lines.append(f"- 答复 QC：{s.get('qc') or '—'}")
        if s.get("note"):
            lines.append(f"- 理由：{s['note']}")
        lines.append("")
    return "\n".join(lines).rstrip()


if __name__ == "__main__":
    _proj = sys.argv[1] if len(sys.argv) > 1 else "20618-0424US00"
    print(json.dumps(build_assignment_schemes(_proj), ensure_ascii=False, indent=2))
