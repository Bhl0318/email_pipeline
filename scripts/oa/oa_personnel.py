#!/usr/bin/env python3
"""OA 案件报告 第五类「内部人员档案」—— 纯查库拼 markdown（不走 AI，避免编造）。

数据源（atw MySQL）：
  projects：撰写案(project_type∈CN撰写/EN撰写)取撰写负责人/原QC；
            答复案(project_type LIKE %答复及其他%)每行=一轮OA，取答复负责人/QC + 轮次(project_name「第N次」)。
  users   ：按 username_zn 取 职务=usertype、职级=position、在职=status('在职'/'离职')。
  同族    ：案号前 10 位(组内号)LIKE，列同族案号 + 撰写人/QC + 同族历史OA。

execute 可注入(测试用)，默认 db_query.execute（atw）。build_personnel_md 绝不抛异常。
"""
import re
import sys


def _get_execute(execute):
    if execute is not None:
        return execute
    from db_query import execute as _e
    return _e


def _q(v):
    return str(v if v is not None else "").replace("'", "\\'")


def _round_no(project_name):
    """从立项名「第N次」取轮次数字；取不到返回空串。"""
    m = re.search(r"第\s*([一二三四五六七八九十\d]+)\s*次", project_name or "")
    if not m:
        return ""
    s = m.group(1)
    cn = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    if s.isdigit():
        return s
    return str(cn.get(s, s))


def _person_label(name, ex, cache):
    """姓名 → 「姓名（职务/职级，在职|离职）」。查不到只给姓名。多名(顿号/逗号)逐个标。"""
    name = (name or "").strip()
    if not name:
        return "—"
    parts = re.split(r"[、,，/]+", name)
    labels = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p in cache:
            labels.append(cache[p])
            continue
        label = p
        try:
            rows = ex(f"SELECT usertype, position, status, usermail FROM users WHERE username_zn='{_q(p)}' LIMIT 1")
            if rows:
                r = rows[0]
                duty = (r.get("usertype") or "").strip()
                level = (r.get("position") or "").strip()
                status = (r.get("status") or "").strip()
                if not (r.get("usermail") or "").strip():   # 无 usermail 视同离职
                    status = "离职"
                attr = "/".join([x for x in (duty, level) if x])
                inservice = status or "在职状态未知"
                label = f"{p}（{attr}，{inservice}）" if attr else f"{p}（{inservice}）"
        except Exception:
            pass
        cache[p] = label
        labels.append(label)
    return "；".join(labels) if labels else "—"


def _is_oa_name(project_name):
    """立项名是否为 OA 记录：project_name 含 "OA"（大小写不敏感）。"""
    return "OA" in (project_name or "").upper()


def _first_nonempty(rows, key):
    for r in rows:
        v = (r.get(key) or "").strip()
        if v:
            return v
    return ""


def _oa_rounds(rows, ex, cache):
    """同案号行里挑「project_name 含 OA」且有承办的行 → 历史OA markdown 列表项，按轮次排序。"""
    items = []
    for r in rows:
        if not _is_oa_name(r.get("project_name", "")):
            continue
        leader_raw = (r.get("project_leader") or "").strip()
        qc_raw = (r.get("project_qc") or "").strip()
        if not leader_raw and not qc_raw:      # 本轮新立项(承办未分配)不计入历史
            continue
        rn = _round_no(r.get("project_name", ""))
        date = str(r.get("oa_doc_date", "") or "")[:10]
        leader = _person_label(leader_raw, ex, cache)
        qc = _person_label(qc_raw, ex, cache)
        head = f"第{rn}次" if rn else (r.get("project", "") or "OA")
        when = f"（{date}）" if date else ""
        items.append((rn or "999", f"  - {head}{when}：答复负责人 {leader}；答复 QC {qc}"))
    items.sort(key=lambda x: (len(str(x[0])), str(x[0])))
    return [t for _, t in items]


def _user_attrs(name, ex, cache):
    """姓名 → {name, duty(职务), level(职级), status(在职/离职)}；查不到属性留空。"""
    name = (name or "").strip()
    if not name:
        return None
    if name in cache:
        return cache[name]
    a = {"name": name, "duty": "", "level": "", "status": ""}
    try:
        rows = ex(f"SELECT usertype, position, status, usermail FROM users WHERE username_zn='{_q(name)}' LIMIT 1")
        if rows:
            a["duty"] = (rows[0].get("usertype") or "").strip()
            a["level"] = (rows[0].get("position") or "").strip()
            a["status"] = (rows[0].get("status") or "").strip()
            if not (rows[0].get("usermail") or "").strip():   # 无 usermail 视同离职
                a["status"] = "离职"
    except Exception:
        pass
    cache[name] = a
    return a


def collect_candidates(project, execute=None):
    """收集候选人库供人员安排建议用：本案撰写/历史OA承办人 + 同族OA参与者，带职务/职级/在职/来源。
    返回 [{name, duty, level, status, sources:[本案撰写|本案历史OA|同族OA...]}]，去重。"""
    try:
        ex = _get_execute(execute)
    except Exception:
        return []
    project = project or ""
    zu = project[:10]
    cache = {}
    cands = {}

    def _add(names, source):
        for p in re.split(r"[、,，/]+", names or ""):
            p = p.strip()
            if not p:
                continue
            a = _user_attrs(p, ex, cache)
            if not a:
                continue
            c = cands.setdefault(p, {**a, "sources": set()})
            c["sources"].add(source)

    try:
        own = ex(f"SELECT project_name, project_leader, project_qc FROM projects "
                 f"WHERE project='{_q(project)}'") or []
        for r in own:
            src = "本案历史OA" if _is_oa_name(r.get("project_name", "")) else "本案撰写"
            _add(r.get("project_leader", ""), src)
            _add(r.get("project_qc", ""), src)
        fam = ex(f"SELECT project_name, project_leader, project_qc FROM projects "
                 f"WHERE project LIKE '{_q(zu)}%' AND project <> '{_q(project)}'") or []
        for r in fam:
            if _is_oa_name(r.get("project_name", "")):
                _add(r.get("project_leader", ""), "同族OA")
                _add(r.get("project_qc", ""), "同族OA")
    except Exception as e:
        print(f"[oa_personnel] 候选池收集出错: {e}", file=sys.stderr)

    out = []
    for c in cands.values():
        c["sources"] = sorted(c["sources"])
        out.append(c)
    return out


def build_personnel_md(project, execute=None):
    """拼「## 内部人员档案」markdown。DB 不可达/无数据时返回带说明的段落，绝不抛。"""
    try:
        ex = _get_execute(execute)
    except Exception as e:
        return f"## 内部人员档案\n\n> 人员档案未生成（数据库不可达：{e}）。"
    project = project or ""
    zu = project[:10]
    cache = {}
    L = ["## 内部人员档案", ""]
    try:
        # (1) 本案信息 —— 新立项本身无承办，撰写负责人/原QC 取同案号(projects.project=案号)已有的 leader/qc
        L.append("### (1) 本案信息")
        own = ex(f"SELECT project, project_name, project_leader, project_qc, oa_doc_date "
                 f"FROM projects WHERE project='{_q(project)}'") or []
        leader = _first_nonempty(own, "project_leader")
        qc = _first_nonempty(own, "project_qc")
        L.append(f"- 撰写负责人：{_person_label(leader, ex, cache) if leader else '资料缺失'}")
        L.append(f"- 原 QC：{_person_label(qc, ex, cache) if qc else '资料缺失'}")
        # 本案历史OA记录：同案号下 project_name 含 "OA" 的行
        rounds = _oa_rounds(own, ex, cache)
        L.append("- 历史 OA 记录：" + ("" if rounds else "无"))
        L.extend(rounds)

        # (2) 同族案件信息（案号前10位=组内号，排除本案；同规则）
        L.append("")
        L.append("### (2) 同族案件信息")
        fam = ex(f"SELECT project, project_name, project_leader, project_qc, oa_doc_date "
                 f"FROM projects WHERE project LIKE '{_q(zu)}%' AND project <> '{_q(project)}'") or []
        fam_nos = sorted({r.get("project", "") for r in fam if r.get("project")})
        if not fam_nos:
            L.append("- 无同族案件")
        else:
            L.append("- 同族案号：" + "、".join(fam_nos))
            L.append(f"- 同族撰写负责人：{_person_label(_first_nonempty(fam, 'project_leader'), ex, cache) or '资料缺失'}")
            L.append(f"- 同族原 QC：{_person_label(_first_nonempty(fam, 'project_qc'), ex, cache) or '资料缺失'}")
            # 同族历史OA（各案号分组，project_name 含 OA）
            by_case = {}
            for r in fam:
                by_case.setdefault(r.get("project", ""), []).append(r)
            fam_oa_lines = []
            for case_no in sorted(by_case):
                lines = _oa_rounds(by_case[case_no], ex, cache)
                if lines:
                    fam_oa_lines.append(f"  - {case_no}：")
                    fam_oa_lines.extend("  " + ln for ln in lines)
            if fam_oa_lines:
                L.append("- 同族历史 OA 记录：")
                L.extend(fam_oa_lines)
    except Exception as e:
        print(f"[oa_personnel] 拼档案出错: {e}", file=sys.stderr)
        L.append(f"\n> ⚠️ 人员档案部分生成出错：{e}")
    return "\n".join(L)


if __name__ == "__main__":
    _proj = sys.argv[1] if len(sys.argv) > 1 else "20618-0424US00"
    print(build_personnel_md(_proj))
