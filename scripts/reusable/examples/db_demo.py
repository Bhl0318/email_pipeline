"""db（客户端）+ db_merge（跨库合并）用法示例。

跨库合并这层离线实跑（用假 fetcher）；真实查库需连 atw/IPEasy，只示范写法。

运行：python3 scripts/reusable/examples/db_demo.py
"""
import os
import sys

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "foundation"))
sys.path.insert(0, os.path.join(_LIB, "business"))
from db_merge import merge_by_key  # noqa: E402


# 两个"数据源 fetcher"：真实里分别用 db.mysql_query / db.mssql_query，字段命名是业务
def from_atw(project):            # 假装查 atw(MySQL)
    return {"客户名称": "众慧" if project.startswith("206") else ""}


def from_ipeasy(project):         # 假装查 唯德 IPEasy(MSSQL)
    return {"客户案号": "TZ2023", "申请号": "17456882", "申请日": ""}  # 申请日空→被跳过


def from_broken(project):         # 假装连不上 → 跳过，不阻塞
    raise ConnectionError("IPEasy 连接超时")


if __name__ == "__main__":
    print("== 跨库合并（离线）==")
    merged = merge_by_key("20618-0424US00", [from_atw, from_ipeasy, from_broken])
    print("  合并结果:", merged)
    # -> {'客户名称': '众慧', '客户案号': 'TZ2023', '申请号': '17456882'}  (申请日空被跳过, broken源跳过)

    print("\n== 真实查库 + 合并（需连库，仅示范写法）==")
    print('''
    from db import mysql_query, mssql_query

    def from_atw(project):
        code = project[:5]
        rows = mysql_query("SELECT customer_name FROM customer WHERE customer_code=%s", (code,))
        return {"客户名称": rows[0]["customer_name"] if rows else ""}

    def from_ipeasy(project):
        rows = mssql_query("SELECT case_volume_customer, app_no, app_date "
                           "FROM p_case_info WHERE case_volume=%s", (project,))
        r = rows[0] if rows else {}
        return {"客户案号": r.get("case_volume_customer"), "申请号": r.get("app_no"),
                "申请日": str(r.get("app_date"))[:10] if r.get("app_date") else ""}

    fields = merge_by_key(project, [from_atw, from_ipeasy])   # 查两库、合并、逐源兜底
    ''')
