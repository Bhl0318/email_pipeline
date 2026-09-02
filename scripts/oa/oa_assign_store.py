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


PERF_ROLE_TABLE = "tip_budgetperformance_role"


def _user_id(name, ex):
    """按中文名查 users.userid；查不到/异常返回 ""。"""
    name = (name or "").strip()
    if not name:
        return ""
    rows = ex(f"SELECT userid FROM users WHERE username_zn='{_q(name)}'")
    if isinstance(rows, str) or not rows:
        return ""
    return str(rows[0].get("userid") or "")


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
