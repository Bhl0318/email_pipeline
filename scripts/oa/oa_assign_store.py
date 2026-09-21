#!/usr/bin/env python3
"""OA 分配 —— 待分配状态表访问（atw，每案一行，只存 id + status）。

设计：oa_assign_task 只记 案件id + 是否已分配；案件展示字段(案号/客户/日期/名称)
按 id JOIN projects 现取（projects 为单一数据源，不冗余）。分配结果回写 projects：
  project_qc ← QC；project_leader ← 答复负责人；project_participant ← 答复负责人(参与人=负责人)。
Wiki 人员分配格另由 oainfo_cli.write_oa_assignment 写。

表 oa_assign_task（DDL 见 oa_assign_task.sql）：
  id      varchar PK   立项唯一 id(=projects.row_id / Wiki 行 data-oa-id)
  status  tinyint      0待分配 / 1已分配

execute 可注入(测试用)，默认 db_query.execute（atw）。
"""
TABLE = "oa_assign_task"
REPORT_TABLE = "oa_assign_report"
SHARE_BATCH_TABLE = "oa_assign_share_batch"   # 批量分享：一批次一行（batch_id → oaid 列表 + 分享时间）


def _q(v):
    return str(v if v is not None else "").replace("'", "\\'")


def _get_execute(execute):
    if execute is not None:
        return execute
    from db_query import execute as _e
    return _e


def add_pending(items, execute=None):
    """立项后把每件 id 写入待分配表(status=0，按 id 去重)，并记 link_sent_at=当前时刻
    (=该案要求分配/发分配链接的时间，供分配页展示)。返回新增条数。"""
    ex = _get_execute(execute)
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    added = 0
    for it in items or []:
        oid = it.get("oa_id", "")
        if not oid:
            continue
        if ex(f"SELECT id FROM {TABLE} WHERE id='{_q(oid)}'"):
            continue
        ex(f"INSERT INTO {TABLE} (id, status, link_sent_at) VALUES ('{_q(oid)}', 0, '{now}')")
        added += 1
    return added


def list_pending(execute=None):
    """JOIN projects 返回待分配/已分配案件的展示字段。submitted=status(0/1)。"""
    ex = _get_execute(execute)
    rows = ex(
        f"SELECT t.id AS id, t.status AS submitted, t.link_sent_at AS link_sent_at, "
        f"p.project AS case_volume, p.project_name AS project_name, p.customer AS customer, "
        f"p.oa_doc_date AS oa_doc_date, p.entrust_date AS entrust_date, "
        f"p.project_deadline AS project_deadline "
        f"FROM {TABLE} t JOIN projects p ON t.id = p.id "
        f"ORDER BY p.oa_doc_date DESC")
    return rows or []


def mark_submitted(oa_id, responder="", qc="", execute=None):
    """置已分配 + 分配结果回写 projects(qc←QC, leader/participant←负责人)。返回是否命中。"""
    ex = _get_execute(execute)
    if not oa_id:
        return False
    ex(f"UPDATE {TABLE} SET status=1 WHERE id='{_q(oa_id)}'")
    ex(f"UPDATE projects SET project_qc='{_q(qc)}', project_leader='{_q(responder)}', "
       f"project_participant='{_q(responder)}' WHERE id='{_q(oa_id)}'")
    return bool(ex(f"SELECT id FROM {TABLE} WHERE id='{_q(oa_id)}'"))


def user_exists(name, execute=None):
    """校验中文名是否在 users.username_zn（提交分配前用；空名视为通过）。异常时不拦(返回 True)。"""
    name = (name or "").strip()
    if not name:
        return True
    ex = _get_execute(execute)
    try:
        rows = ex(f"SELECT userid FROM users WHERE username_zn='{_q(name)}'")
        if isinstance(rows, str):
            return True   # 查询异常不拦
        return bool(rows)
    except Exception:
        return True


def mark_skipped(oa_id, execute=None):
    """标记该案「不需处理」：oa_assign_task.status=2（区别于 0待分配/1已分配）→ 从待分配列表移除。
    不写 projects/Wiki/绩效表。返回是否命中。"""
    ex = _get_execute(execute)
    if not oa_id:
        return False
    ex(f"UPDATE {TABLE} SET status=2 WHERE id='{_q(oa_id)}'")
    return bool(ex(f"SELECT id FROM {TABLE} WHERE id='{_q(oa_id)}'"))


PERF_ROLE_TABLE = "tip_budgetperformance_role"


def _user_id(name, ex):
    """按中文名查 users.userid；查不到/异常返回 ""。名字为「QC,AQC」拼接时用逗号前的 QC 查。"""
    name = (name or "").strip()
    if not name:
        return ""
    rows = ex(f"SELECT userid FROM users WHERE username_zn='{_q(name)}'")
    if not isinstance(rows, str) and rows:
        return str(rows[0].get("userid") or "")
    if "," in name:   # 「QC,AQC」→ 用逗号前的 QC 取 uid
        first = name.split(",")[0].strip()
        rows = ex(f"SELECT userid FROM users WHERE username_zn='{_q(first)}'")
        if not isinstance(rows, str) and rows:
            return str(rows[0].get("userid") or "")
    return ""


def write_perf_roles(oa_id, responder="", qc="", execute=None):
    """提交分配时把答复负责人/QC 写进 tip_budgetperformance_role（pid=oa_id）：
      答复负责人 → wkrole='答复负责人', role='PM'
      答复 QC    → wkrole='答复QC',    role='QC'
      name=人名, perf=0, uid=users.userid(按 username_zn 查)
    幂等/支持重分配：先删该 pid 的答复角色行再插。返回写入条数。best-effort，不抛。"""
    ex = _get_execute(execute)
    if not oa_id:
        return 0
    try:
        ex(f"DELETE FROM {PERF_ROLE_TABLE} WHERE pid='{_q(oa_id)}' "
           f"AND wkrole IN ('答复负责人','答复QC')")
        n = 0
        for name, wkrole, role in ((responder, "答复负责人", "PM"), (qc, "答复QC", "QC")):
            name = (name or "").strip()
            if not name:
                continue
            uid = _user_id(name, ex)
            ex(f"INSERT INTO {PERF_ROLE_TABLE} (pid, name, wkrole, role, perf, uid) "
               f"VALUES ('{_q(oa_id)}', '{_q(name)}', '{wkrole}', '{role}', 0, '{_q(uid)}')")
            n += 1
        return n
    except Exception as e:
        import sys
        print(f"[perf_role] 写入失败 pid={oa_id}: {e}", file=sys.stderr)
        return 0


def save_report(oa_id, report_md="", schemes=None, execute=None):
    """立项时按 id 存 AI 案件报告(markdown)+方案 JSON。存在则覆盖(UPSERT)。返回是否写入。
    schemes 为 list/dict 时序列化为 JSON 文本；None/空则存空串。"""
    ex = _get_execute(execute)
    if not oa_id:
        return False
    if schemes is None:
        schemes_json = ""
    elif isinstance(schemes, str):
        schemes_json = schemes
    else:
        import json
        schemes_json = json.dumps(schemes, ensure_ascii=False)
    if ex(f"SELECT id FROM {REPORT_TABLE} WHERE id='{_q(oa_id)}'"):
        ex(f"UPDATE {REPORT_TABLE} SET report_md='{_q(report_md)}', "
           f"schemes_json='{_q(schemes_json)}' WHERE id='{_q(oa_id)}'")
    else:
        ex(f"INSERT INTO {REPORT_TABLE} (id, report_md, schemes_json) "
           f"VALUES ('{_q(oa_id)}', '{_q(report_md)}', '{_q(schemes_json)}')")
    return True


def save_submission(oa_id, submit, execute=None):
    """把提交的分配结果+附言存入 oa_assign_report.submit_json（UPSERT，行不存在则建）。
    submit: dict，如 {scheme_id, responder, qc, postscript, reason, submitted_at}。返回是否写入。"""
    ex = _get_execute(execute)
    if not oa_id:
        return False
    import json
    submit_json = json.dumps(submit or {}, ensure_ascii=False)
    if ex(f"SELECT id FROM {REPORT_TABLE} WHERE id='{_q(oa_id)}'"):
        ex(f"UPDATE {REPORT_TABLE} SET submit_json='{_q(submit_json)}' WHERE id='{_q(oa_id)}'")
    else:
        ex(f"INSERT INTO {REPORT_TABLE} (id, submit_json) VALUES ('{_q(oa_id)}', '{_q(submit_json)}')")
    return True


def _ensure_share_batch_table(ex):
    """建批量分享表（幂等）。best-effort：建不了不报错，交由后续写入自然失败。"""
    try:
        ex(f"CREATE TABLE IF NOT EXISTS {SHARE_BATCH_TABLE} ("
           f"batch_id VARCHAR(32) PRIMARY KEY, oaids_json TEXT, shared_at VARCHAR(32))")
    except Exception:
        pass


def save_share_batch(batch_id, oaids, shared_at="", execute=None):
    """存一个分享批次：batch_id → oaid 列表 + 分享时间。返回是否写入。"""
    ex = _get_execute(execute)
    if not batch_id or not oaids:
        return False
    import json
    _ensure_share_batch_table(ex)
    oaids_json = json.dumps(list(oaids), ensure_ascii=False)
    ex(f"INSERT INTO {SHARE_BATCH_TABLE} (batch_id, oaids_json, shared_at) "
       f"VALUES ('{_q(batch_id)}', '{_q(oaids_json)}', '{_q(shared_at)}')")
    return True


def get_share_batch(batch_id, execute=None):
    """按 batch_id 取分享批次。返回 {'oaids': [...], 'shared_at': '...'}；无记录返回 None。"""
    ex = _get_execute(execute)
    if not batch_id:
        return None
    rows = ex(f"SELECT oaids_json, shared_at FROM {SHARE_BATCH_TABLE} WHERE batch_id='{_q(batch_id)}'")
    if not rows:
        return None
    import json
    r = rows[0]
    oaids = []
    if r.get("oaids_json"):
        try:
            oaids = json.loads(r["oaids_json"])
        except Exception:
            oaids = []
    return {"oaids": oaids, "shared_at": r.get("shared_at") or ""}


def get_report(oa_id, execute=None):
    """按 id 取 AI 案件报告。返回 {'report_md':..., 'schemes': [...], 'submit': {...}}；无记录返回 None。"""
    ex = _get_execute(execute)
    if not oa_id:
        return None
    rows = ex(f"SELECT report_md, schemes_json, submit_json FROM {REPORT_TABLE} WHERE id='{_q(oa_id)}'")
    if not rows:
        return None
    r = rows[0]
    md = r.get("report_md") or ""
    import json
    schemes = []
    if r.get("schemes_json"):
        try:
            schemes = json.loads(r["schemes_json"])
        except Exception:
            schemes = []
    submit = {}
    if r.get("submit_json"):
        try:
            submit = json.loads(r["submit_json"])
        except Exception:
            submit = {}
    return {"report_md": md, "schemes": schemes, "submit": submit}
