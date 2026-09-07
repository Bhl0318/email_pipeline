"""nas_locator 用法示例（离线）：造一个假 NAS 目录树，按案号定位说明书。

运行：python3 scripts/reusable/examples/nas_locator_demo.py
"""
import os
import sys
import tempfile

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "business"))
from nas_locator import find_application_file, resolve_app_dir  # noqa: E402


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as nas:
        # 造假 NAS：{nas}/其他客户/30011-测试所/30011-0001/30011-0001CN00/递交文件/说明书-xxx.docx
        submit = os.path.join(nas, "其他客户", "30011-测试所", "30011-0001",
                              "30011-0001CN00", "01-递交文件")
        os.makedirs(submit)
        spec = os.path.join(submit, "说明书-30011-0001CN00.docx")
        open(spec, "w").close()

        cfg = {"nas_base": nas, "zhuohui_dir": os.path.join(nas, "众慧"),
               "toplevel_customers": set(), "keywords": {"CN": ["说明书"]}}
        # 客户码→简称：真实里用 db.mysql_query 查 customer 表；这里注入假的
        lookup = lambda code: "测试所" if code == "30011" else ""

        print("定位目录:", resolve_app_dir("30011-0001CN00", "CN", cfg, lookup))
        print("说明书  :", find_application_file("30011-0001CN00", "CN", cfg, lookup))
        # -> .../01-递交文件/说明书-30011-0001CN00.docx

    print("\n真实用法（NAS 挂载 + 查库，仅示范写法）：")
    print('''
    from nas_locator import find_application_file
    from db import mysql_query

    def shortname(code):   # 客户码→客户简称（查 atw）
        rows = mysql_query("SELECT customer_shortname FROM customer WHERE customer_code=%s", (code,))
        return rows[0]["customer_shortname"] if rows else ""

    spec = find_application_file("20849-0032US01", "US", shortname_lookup=shortname)  # 默认 Z 盘规则
    ''')
