"""db —— 数据库查询客户端（基础通用层 · 网络与服务调用）。

- mysql.mysql_query   查 atw(MySQL/TIP)
- mssql.mssql_query   查 唯德 IPEasy(SQL Server)
两者统一从 db_config.json 读连接（mysql_atw / mssql_ipeasy），参数化查询、返回 list[dict]。
跨库合并（查两库按 key 合并）见 business/db_merge。
"""
from .config import load_db_config
from .mysql import mysql_query
from .mssql import mssql_query

__all__ = ["load_db_config", "mysql_query", "mssql_query"]
