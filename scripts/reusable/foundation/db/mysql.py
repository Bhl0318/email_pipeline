"""atw（TIP）MySQL 查询客户端（基础通用层 · 网络与服务调用）。

抽自 report/db_query.py 的 execute/execute_params，逻辑不变；改动：连接信息不再硬编码，
统一从 db_config.json 的 mysql_atw 段读（或调用方传入 config）。依赖：pymysql。
"""
import sys

from .config import load_db_config

_SELECTISH = ("select", "show", "desc")


def mysql_query(sql, params=None, config=None):
    """对 atw(MySQL) 执行 SQL。SELECT/SHOW/DESC 返回 list[dict]，其它 commit 后返回影响行数。

    输入：
      sql     SQL 字符串（**建议用 %s 占位 + params 参数化，避免注入**）
      params  可选，参数元组/列表
      config  可选，连接 dict（host/user/password/database/port/charset）；不给则读 db_config.mysql_atw
    输出：list[dict]（查询）或 int 影响行数（增删改）。
    """
    import pymysql
    cfg = config or load_db_config().get("mysql_atw", {})
    db = pymysql.connect(
        host=cfg["host"], user=cfg["user"], password=cfg["password"],
        database=cfg["database"], port=int(cfg.get("port", 3306)),
        charset=cfg.get("charset", "utf8"))
    try:
        cur = db.cursor()
        cur.execute(sql, params or ())
        db.commit()
        if sql.strip().lower().startswith(_SELECTISH):
            cols = [d[0] for d in cur.description] if cur.description else []
            result = [dict(zip(cols, row)) for row in cur.fetchall()]
        else:
            result = cur.rowcount
        cur.close()
        return result
    finally:
        db.close()
