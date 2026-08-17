#!/usr/bin/env python3
"""OA 分配 —— 待分配/分配结果数据表访问（atw，每案一行）。

立项(dispatch_oa)转OA后，把每件立项案件(含 oa_id)写入一行；分配页读它当
/api/cases/pending 数据源；提交后按 oa_id 回填 responder/qc 并置已分配。
同一张表既是"待分配列表来源"，也承载"分配结果"。

表：oa_assign_task（★表名/字段待确认 C2，DDL 见 oa_assign_task.sql）
  id           varchar  PK   立项唯一 id(=projects.row_id / Wiki 行 data-oa-id)
  case_volume  varchar       案号
  project_name varchar       立项类型/名称
  customer     varchar       客户简称
  region       varchar
  oa_doc_date/entrust_date/project_deadline varchar
  designee     varchar       指定人(C4待确认)
  responder    varchar       答复负责人(分配结果)
  qc           varchar       答复QC(分配结果)
  submitted    tinyint       0待分配/1已分配
  created_at/assigned_at datetime

execute 可注入(测试用)，默认用 db_query.execute（atw）。SELECT 返回 dict 行；
INSERT/UPDATE 直接执行。字符串按单引号转义（沿用本仓库现有 SQL 风格）。
"""
TABLE = "oa_assign_task"


def _q(v):
    """单引号转义，None/空 → 空串。"""
    return str(v if v is not None else "").replace("'", "\\'")


def _get_execute(execute):
    if execute is not None:
        return execute
    from db_query import execute as _e
    return _e


def summary_from_item(item):
    """立项 item → 待分配行字段。"""
    return {
        "id": item.get("oa_id", ""),
        "case_volume": item.get("project", ""),
        "project_name": item.get("project_name", ""),
        "customer": item.get("customer", ""),
        "region": item.get("region", ""),
        "oa_doc_date": item.get("oa_doc_date", ""),
        "entrust_date": item.get("entrust_date", ""),
        "project_deadline": item.get("project_deadline", ""),
        "designee": item.get("designee", ""),
    }


def add_pending(items, execute=None):
    """把若干立项 item 写入待分配表（按 id 去重，已存在跳过）。返回新增条数。"""
    ex = _get_execute(execute)
    added = 0
    for it in items or []:
        r = summary_from_item(it)
        oid = r["id"]
        if not oid:
            continue
        exists = ex(f"SELECT id FROM {TABLE} WHERE id='{_q(oid)}'")
        if exists:
            continue
        cols = ("id", "case_volume", "project_name", "customer", "region",
                "oa_doc_date", "entrust_date", "project_deadline", "designee",
                "submitted", "created_at")
        vals = (f"'{_q(r['id'])}'", f"'{_q(r['case_volume'])}'", f"'{_q(r['project_name'])}'",
                f"'{_q(r['customer'])}'", f"'{_q(r['region'])}'", f"'{_q(r['oa_doc_date'])}'",
                f"'{_q(r['entrust_date'])}'", f"'{_q(r['project_deadline'])}'",
                f"'{_q(r['designee'])}'", "0", "NOW()")
        ex(f"INSERT INTO {TABLE} ({', '.join(cols)}) VALUES ({', '.join(vals)})")
        added += 1
    return added


def list_pending(execute=None):
    """返回全部记录(含已分配，前端按 submitted 筛选)，按收文日期倒序。"""
    ex = _get_execute(execute)
    rows = ex(f"SELECT id, case_volume, project_name, customer, region, oa_doc_date, "
              f"entrust_date, project_deadline, designee, responder, qc, submitted "
              f"FROM {TABLE} ORDER BY oa_doc_date DESC, created_at DESC")
    return rows or []


def mark_submitted(oa_id, responder="", qc="", execute=None):
    """按 oa_id 回填分配结果并置已分配。返回是否命中(影响行数>0 或存在)。"""
    ex = _get_execute(execute)
    if not oa_id:
        return False
    ex(f"UPDATE {TABLE} SET responder='{_q(responder)}', qc='{_q(qc)}', "
       f"submitted=1, assigned_at=NOW() WHERE id='{_q(oa_id)}'")
    check = ex(f"SELECT id FROM {TABLE} WHERE id='{_q(oa_id)}'")
    return bool(check)
