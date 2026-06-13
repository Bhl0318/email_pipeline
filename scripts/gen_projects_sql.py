#!/usr/bin/env python3
"""离线生成 OA 立项 projects 表的 INSERT 语句（只读，不写库/不发信/不写Wiki）。

用途：dispatch_oa 已启用前漏写的那批立项数据，用本脚本重新分类后把 INSERT 语句
导出到 .sql 文件，人工 review 后自行执行入库。生成逻辑与 dispatch_oa 的 INSERT
完全一致（同字段、同顺序、同转义、project_name 带 _by_email_pipline 后缀、
customer 取客户简称）。

用法：
  python3 gen_projects_sql.py                      # 读 TEST_AUTO，含 US 期限下载
  python3 gen_projects_sql.py --folder TEST        # 指定文件夹
  python3 gen_projects_sql.py --no-us-deadline     # 跳过 US 官文下载（US 期限留空，快）
  python3 gen_projects_sql.py --out my.sql         # 指定输出文件

输出：默认 projects_inserts.sql（与本脚本同目录）。
注意：会连真实邮箱读取（只读 IMAP），开启 US 期限时会调 USPTO API 下载官文，
      并对 atw customer 表做只读 SELECT 取客户简称。
      不写数据库（不执行任何 INSERT/UPDATE）、不发任何邮件、不写 Wiki、不移动邮件。
"""
import os
import sys
import json
import uuid
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from loader import Pipeline  # noqa: E402

SHARED_EMAIL_CONFIG = os.path.join(SCRIPT_DIR, "email_config.json")
PIPELINE_CONFIG = os.path.join(SCRIPT_DIR, "pipeline_config.json")

# 与 dispatch_oa 完全一致的字段顺序
FIELDS = ["id", "project", "project_name", "project_type", "customer", "oa_doc_date", "entrust_date",
          "oaNum", "applytype", "project_deadline", "dueDate",
          "now_status", "project_phase", "submitby", "oa_remark", "wikiurl"]

_customer_cache = {}


def lookup_customer_shortname(project):
    """atw customer 表只读查：customer_code（案号前5位）→ customer_shortname。
    复刻 dispatch_oa 的 query_customer_shortname；查不到/连不上返回空串。"""
    code = (project or "")[:5]
    if not code:
        return ""
    if code in _customer_cache:
        return _customer_cache[code]
    name = ""
    try:
        from db_query import execute
        safe = code.replace("'", "\\'")
        rows = execute(f"SELECT customer_shortname FROM customer WHERE customer_code = '{safe}'")
        if rows and rows[0].get("customer_shortname"):
            name = rows[0]["customer_shortname"]
    except Exception as e:
        print(f"[customer] 查客户简称失败 {code}: {e}", file=sys.stderr)
    _customer_cache[code] = name
    return name


def build_insert(item):
    """复刻 dispatch_oa 的单条 INSERT 构造逻辑。"""
    # project_type：CN → 中国答复及其他；其他 → 海外答复及其他
    item["project_type"] = "中国答复及其他" if item.get("region") == "CN" else "海外答复及其他"
    # customer：客户简称，按案号前5位查 atw customer 表（只读）
    item["customer"] = lookup_customer_shortname(item.get("project", ""))
    values = []
    for f in FIELDS:
        if f == "id":
            values.append(str(uuid.uuid4()))
            continue
        v = item.get(f, "")
        if v is None:
            v = ""
        if f == "oa_doc_date" and not v:
            values.append("__NULL__")
            continue
        values.append(str(v).replace("'", "\\'"))
    cols = ", ".join(FIELDS)
    vals = ", ".join("NULL" if v == "__NULL__" else f"'{v}'" for v in values)
    return f"INSERT INTO projects ({cols}) VALUES ({vals});"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", default="TEST_AUTO", help="读取的 IMAP 文件夹（默认 TEST_AUTO，因邮件已归档到此）")
    ap.add_argument("--out", default=os.path.join(SCRIPT_DIR, "projects_inserts.sql"))
    ap.add_argument("--no-us-deadline", action="store_true", help="跳过 US 官文下载，US 期限留空")
    args = ap.parse_args()

    pcfg = json.load(open(PIPELINE_CONFIG, encoding="utf-8"))
    accounts = [{**a, "folder": args.folder} for a in pcfg.get("accounts", [{"account": "docketing"}])]

    oa = Pipeline(os.path.join(SCRIPT_DIR, "oa"))
    with oa as OA:
        OA.set_config_path(SHARED_EMAIL_CONFIG)
        all_emails, all_results = OA.read_and_classify_oa(accounts=accounts)

        # project_name 后缀（与 dispatch_oa 一致）
        SUFFIX = "_by_email_pipline"
        for it in all_results:
            pn = it.get("project_name", "") or ""
            if pn and not pn.endswith(SUFFIX):
                it["project_name"] = pn + SUFFIX

        # US 答复期限（与 dispatch_oa 一致；可用 --no-us-deadline 跳过）
        if not args.no_us_deadline:
            us_items = [r for r in all_results if r.get("region") == "US" and r.get("application_no")]
            if us_items:
                from us_deadline import get_us_deadline
                from filter_oa_email import calc_dueDate
                print(f"{len(us_items)} 条 US 记录下载官文取期限...", file=sys.stderr)
                for item in us_items:
                    try:
                        dl = get_us_deadline(item["application_no"], item.get("notification_type", ""),
                                             item.get("oa_doc_date", ""), item.get("project", ""))
                        if dl and dl.get("deadline"):
                            item["project_deadline"] = dl["deadline"]
                            item["dueDate"] = calc_dueDate(item)
                            print(f"[US] {item['project']} 期限: {dl['deadline']}", file=sys.stderr)
                    except Exception as e:
                        print(f"[US] {item['project']} 异常: {e}", file=sys.stderr)

        # 生成 SQL
        lines = [build_insert(it) for it in all_results if it.get("project") and it.get("project_name")]

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("-- OA 立项 projects 离线 INSERT，由 gen_projects_sql.py 生成\n")
        f.write(f"-- 共 {len(lines)} 条\n\n")
        f.write("\n".join(lines) + "\n")

    print(f"\n✓ 已生成 {len(lines)} 条 INSERT → {args.out}", file=sys.stderr)
    print("  请人工 review 后在 SQL 客户端执行（本脚本未连库）。", file=sys.stderr)


if __name__ == "__main__":
    main()
