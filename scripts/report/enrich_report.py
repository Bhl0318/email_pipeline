#!/usr/bin/env python3
"""
汇报信 enrich：拿代理所案号（project）补全案件主数据，合并进 fields_json。

数据源（两个库分别查，应用层合并，不跨库 JOIN）：
- 客户名称：MySQL atw 的 customer 表（customer_code = project 前 5 位）
- 申请号/申请名/申请日/客户案号：SQL Server IPEasy 的 p_case_info（case_volume = project）

查不到 / 连不上时跳过该字段（保持调用方原来的"请提供"），不阻塞主流程。

测试：
  python3 enrich_report.py 20651-0129CM00
"""
import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_CONFIG_PATH = os.path.join(SCRIPT_DIR, "db_config.json")


def _load_db_config():
    with open(DB_CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def query_customer_name(project):
    """MySQL atw: customer_code = project 前 5 位 → customer_name"""
    code = (project or "")[:5]
    if not code:
        return ""
    try:
        from db_query import execute_params
        rows = execute_params(
            "SELECT customer_name FROM customer WHERE customer_code = %s", (code,))
        return rows[0]["customer_name"] if rows else ""
    except Exception as e:
        print(f"[enrich] 查客户名失败 {project}: {e}", file=sys.stderr)
        return ""


def query_case_info(project):
    """SQL Server IPEasy: case_volume = project → 申请号/申请名/申请日/客户案号"""
    if not project:
        return {}
    cfg = _load_db_config().get("mssql_ipeasy", {})
    host = cfg.get("host", "")
    if not host or host.startswith("请填写"):
        return {}  # 未配置 IPEasy，跳过
    try:
        import pymssql
        conn = pymssql.connect(
            cfg["host"], cfg["user"], cfg["password"], cfg["database"],
            charset=cfg.get("charset", "utf8"),
        )
        cur = conn.cursor()  # 普通 cursor，按位置取值
        cur.execute(
            "SELECT case_volume_customer, app_no, case_name, app_date "
            "FROM p_case_info WHERE case_volume = %s", (project,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return {}
        return {
            "case_volume_customer": row[0],  # 委托方案号
            "app_no": row[1],                # 官方申请号（数字）= 申请号
            "case_name": row[2],
            "app_date": row[3],
        }
    except Exception as e:
        print(f"[enrich] 查 p_case_info 失败 {project}: {e}", file=sys.stderr)
        return {}


def enrich_cn_fields(project):
    """返回要合并进 fields_json 的字段（查到才返回该键，覆盖"请提供"）"""
    out = {}

    name = query_customer_name(project)
    if name:
        out["客户名称"] = name

    info = query_case_info(project)
    if info:
        if info.get("case_volume_customer"):
            out["客户案号"] = info["case_volume_customer"]
        if info.get("app_no"):
            out["申请号"] = info["app_no"]       # 官方申请号
        if info.get("case_name"):
            out["申请名称"] = info["case_name"]
        if info.get("app_date"):
            out["申请日"] = str(info["app_date"])[:10]  # datetime → YYYY-MM-DD

    return out


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(enrich_cn_fields(sys.argv[1]), ensure_ascii=False, indent=2))
    else:
        print("用法: python3 enrich_report.py <代理所案号>", file=sys.stderr)
