#!/usr/bin/env python3
"""
数据库查询工具 — 执行 SQL 语句并返回结果。

用法:
  python3 db_query.py "SELECT * FROM some_table LIMIT 5"
  python3 db_query.py "INSERT INTO some_table (col) VALUES ('val')"
"""
import sys
import json
import pymysql

DB_CONFIG = {
    "host": "10.10.70.88",
    "user": "tip88",
    "password": "tipadmin",
    "database": "atw",
    "port": 3306,
    "charset": "utf8",
}


def execute(sql):
    db = pymysql.connect(**DB_CONFIG)
    cur = db.cursor()
    cur.execute(sql)
    db.commit()
    if sql.strip().lower().startswith(("select", "show", "desc")):
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
    else:
        results = "success"
    cur.close()
    db.close()
    return results


def execute_params(sql, params=None):
    """参数化执行 SQL，避免字符串拼接的注入/转义问题。
    SELECT 返回 list[dict]；其他返回 affected rows 数。"""
    db = pymysql.connect(**DB_CONFIG)
    cur = db.cursor()
    cur.execute(sql, params or ())
    db.commit()
    if sql.strip().lower().startswith(("select", "show", "desc")):
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
    else:
        results = cur.rowcount
    cur.close()
    db.close()
    return results


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("用法: python3 db_query.py \"SQL语句\"")
    #     sys.exit(1)
    #
    # sql = sys.argv[1]
    sql = "select * from projects where project='20618-1345US00'"
    result = execute(sql)
    if isinstance(result, str):
        print(result)
    else:
        print(json.dumps(result, ensure_ascii=False, default=str, indent=2))
