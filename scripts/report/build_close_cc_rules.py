#!/usr/bin/env python3
"""从 close_report_rules.json 生成结项邮件「抄送名单」派生表 close_email_cc_rules.json。

结构：{region: {combination: {客户码/5开头/其他: [cc邮箱...]}}}，仅收 action=skip 且 cc 非空的条目。
供结项 web 表单页直读（也可走 report_server 的 /api/close-cc-rules 拉同一份）。

每次改完 close_report_rules.json 后跑一次以同步：
  python3 build_close_cc_rules.py
"""
import json
import os
import close_cc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "close_email_cc_rules.json")


def main():
    rules = close_cc.load_rules()
    m = close_cc.build_cc_map(rules)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write("\n")
    stat = {r: len(v) for r, v in m.items()}
    total = sum(len(v) for v in m.values())
    print(f"已生成 {OUT}")
    print(f"各法域含抄送的组合数：{stat}  合计 {total}")


if __name__ == "__main__":
    main()
