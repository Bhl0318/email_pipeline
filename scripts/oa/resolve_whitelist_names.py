#!/usr/bin/env python3
"""把 oa_assign_whitelist 里的白名单名字(简称/名) 解析成 users.username_zn(全名)。

白名单用口语简称(胜权/小琴/美欣…)，users 用全名(陆胜权/倪小琴/伍美欣…)，需按案匹配。
匹配策略：① username_zn == name_raw（本就是全名）；② username_zn 以 name_raw 结尾（简称=名，
如 胜权→陆胜权）；③ username_zn 含 name_raw。唯一命中→回填 username_zn；多义/无命中→列出待人工。

用法（在能连 atw 的机器上）：
  python3 resolve_whitelist_names.py            # 只报告，不改库（dry-run）
  python3 resolve_whitelist_names.py --apply    # 唯一命中的回填 username_zn
"""
import sys

TABLE = "oa_assign_whitelist"


def _q(v):
    return str(v if v is not None else "").replace("'", "\\'")


def _match(name, users):
    """返回候选 username_zn 列表（去重，保序）。"""
    n = (name or "").strip()
    if not n:
        return []
    exact = [u for u in users if u == n]
    if exact:
        return [n]
    ends = [u for u in users if u.endswith(n) and u != n]
    if ends:
        return list(dict.fromkeys(ends))
    contains = [u for u in users if n in u and u != n]
    return list(dict.fromkeys(contains))


def main():
    apply = "--apply" in sys.argv
    from db_query import execute

    users = [r.get("username_zn") for r in
             (execute("SELECT DISTINCT username_zn FROM users WHERE username_zn IS NOT NULL AND username_zn<>''") or [])
             if r.get("username_zn")]
    print(f"users 表姓名 {len(users)} 个", file=sys.stderr)

    names = sorted({r.get("name_raw") for r in
                    (execute(f"SELECT DISTINCT name_raw FROM {TABLE}") or []) if r.get("name_raw")})
    print(f"白名单去重姓名 {len(names)} 个\n", file=sys.stderr)

    uniq, ambi, none = {}, {}, []
    for n in names:
        cands = _match(n, users)
        if len(cands) == 1:
            uniq[n] = cands[0]
        elif len(cands) > 1:
            ambi[n] = cands
        else:
            none.append(n)

    print(f"== 唯一命中 {len(uniq)} ==")
    for n, u in uniq.items():
        print(f"  {n}  →  {u}")
    print(f"\n== 多义(需人工选) {len(ambi)} ==")
    for n, cs in ambi.items():
        print(f"  {n}  →  {', '.join(cs)}")
    print(f"\n== 无匹配(users 表里没有, 需人工补/核对) {len(none)} ==")
    print("  " + "、".join(none) if none else "  (无)")

    if apply and uniq:
        for n, u in uniq.items():
            execute(f"UPDATE {TABLE} SET username_zn='{_q(u)}' WHERE name_raw='{_q(n)}'")
        print(f"\n[apply] 已回填 username_zn: {len(uniq)} 个唯一命中的名字", file=sys.stderr)
    elif not apply:
        print("\n(dry-run，未改库；加 --apply 回填唯一命中的 username_zn)", file=sys.stderr)


if __name__ == "__main__":
    main()
