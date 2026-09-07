"""唯德 IPEasy SQL Server 查询客户端（基础通用层 · 网络与服务调用）。

抽自 report/enrich_report.py 里重复的 pymssql.connect 样板（query_case_info/demands/recipients
各写一遍），归一成一个 mssql_query。逻辑不变；返回从"按位置取值"改为按列名 list[dict]（更通用）。
依赖：pymssql。
"""
import sys

from .config import load_db_config

_SELECTISH = ("select", "show", "desc")


def mssql_query(sql, params=None, config=None):
    """对 IPEasy(SQL Server) 执行 SQL。SELECT 返回 list[dict]，其它 commit 后返回影响行数。

    输入：
      sql     SQL 字符串（用 %s 占位 + params 参数化）
      params  可选，参数元组/列表
      config  可选，连接 dict；不给则读 db_config.mssql_ipeasy
    输出：list[dict]（查询）或 int 影响行数；**未配置（host 空/占位）时返回 []**（不阻塞，与原行为一致）。
          连接/查询出错会抛异常，交给上层（如 db_merge）兜底。
    """
    cfg = config or load_db_config().get("mssql_ipeasy", {})
    host = cfg.get("host", "")
    if not host or host.startswith("请填写") or host.startswith("请填"):
        print("[mssql] IPEasy 未配置(host 空)，跳过", file=sys.stderr)
        return []
    import pymssql
    conn = pymssql.connect(cfg["host"], cfg["user"], cfg["password"], cfg["database"],
                           charset=cfg.get("charset", "utf8"))
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        if sql.strip().lower().startswith(_SELECTISH):
            cols = [d[0] for d in cur.description] if cur.description else []
            result = [dict(zip(cols, row)) for row in cur.fetchall()]
        else:
            conn.commit()
            result = cur.rowcount
        cur.close()
        return result
    finally:
        conn.close()
