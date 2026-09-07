"""数据库连接配置读取（基础通用层）。

统一从 db_config.json 读连接信息（键：mysql_atw / mssql_ipeasy），可用环境变量
DB_CONFIG_PATH 覆盖路径。修正原状况：MySQL 连接曾硬编码在 db_query.py，现统一走配置。
"""
import json
import os

# 本模块在 scripts/reusable/foundation/db/ 下，db_config.json 在 scripts/report/（上溯三级到 scripts）
_DEFAULT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "report", "db_config.json"))


def load_db_config(path=None):
    """读 db_config.json，返回 dict（含 mysql_atw / mssql_ipeasy 两段）。

    输入：path（可选，默认环境变量 DB_CONFIG_PATH 或 scripts/report/db_config.json）
    输出：dict
    """
    path = path or os.environ.get("DB_CONFIG_PATH") or _DEFAULT_PATH
    with open(path, encoding="utf-8") as f:
        return json.load(f)
