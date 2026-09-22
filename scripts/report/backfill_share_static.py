#!/usr/bin/env python3
"""历史 OA 分配「只读分享」链接：批量补生成静态页文件（output/oa-share/{key}.html）。

背景：分享页已改为「提交时写死静态 HTML」。此脚本把**改造前**已分享过的链接一次性补生成，
让老链接也走静态文件（否则老链接继续走 assign.html 动态回退，也能用，只是每次查库）。

覆盖两类：
  · 批量分享：oa_assign_share_batch 每行 → output/oa-share/{batch_id}.html
  · 单案分享：oa_assign_report 里有 submit_json 的案 → output/oa-share/{oaid}.html
    （单案分享链接是 ?oaid=..，无法区分"单独分享过"还是"批量的一员"，
     故对所有已提交/已分享的案都补一份单案文件，多生成无害——只有人真去开那条链接才用到。）

复用 oa_assign 的 _write_share_file / _case_for_share，保证与线上生成逻辑完全一致。

需在**能连 atw 库**的机器上跑（dev 连不到内网库）。只读 SELECT + 写本地 HTML，无写库、无发信。

用法：
  python3 backfill_share_static.py              # 补全所有历史批量 + 单案
  python3 backfill_share_static.py --batch-only # 只补批量
  python3 backfill_share_static.py --single-only# 只补单案
  python3 backfill_share_static.py --force      # 已存在的文件也覆盖重建（默认跳过已存在）
  python3 backfill_share_static.py KEY1 KEY2    # 只补指定 batch_id / oaid
"""
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

import oa_assign  # 复用 _write_share_file / _case_for_share / _share_dir


def _list_batches():
    """oa_assign_share_batch → [(batch_id, oaids[list], shared_at)]。"""
    from db_query import execute as dbx
    import json
    rows = dbx("SELECT batch_id, oaids_json, shared_at FROM oa_assign_share_batch") or []
    out = []
    for r in rows:
        bid = r.get("batch_id")
        if not bid:
            continue
        oaids = []
        if r.get("oaids_json"):
            try:
                oaids = json.loads(r["oaids_json"])
            except Exception:
                oaids = []
        out.append((bid, oaids, r.get("shared_at") or ""))
    return out


def _list_single_oaids():
    """oa_assign_report 里有 submit_json（已提交/已分享）的 oaid 列表。"""
    from db_query import execute as dbx
    rows = dbx("SELECT id FROM oa_assign_report "
               "WHERE submit_json IS NOT NULL AND submit_json <> ''") or []
    return [r.get("id") for r in rows if r.get("id")]


def _exists(key):
    return os.path.isfile(os.path.join(oa_assign._share_dir(), f"{key}.html"))


def main(argv):
    args = set(a for a in argv if a.startswith("--"))
    keys = [a for a in argv if not a.startswith("--")]
    force = "--force" in args
    do_batch = "--single-only" not in args
    do_single = "--batch-only" not in args
    key_filter = set(keys) if keys else None

    n_batch = n_single = n_skip = n_fail = 0

    if do_batch:
        for bid, oaids, shared_at in _list_batches():
            if key_filter and bid not in key_filter:
                continue
            if not force and _exists(bid):
                n_skip += 1
                continue
            ok = oa_assign._write_share_file(bid, oaids, shared_at=shared_at, batch=True)
            if ok:
                n_batch += 1
                print(f"[批量] {bid}  ({len(oaids)} 件, {shared_at})")
            else:
                n_fail += 1
                print(f"[批量] {bid}  失败", file=sys.stderr)

    if do_single:
        for oid in _list_single_oaids():
            if key_filter and oid not in key_filter:
                continue
            if not force and _exists(oid):
                n_skip += 1
                continue
            ok = oa_assign._write_share_file(oid, [oid], batch=False)
            if ok:
                n_single += 1
                print(f"[单案] {oid}")
            else:
                n_fail += 1
                print(f"[单案] {oid}  失败", file=sys.stderr)

    print(f"\n完成：批量 {n_batch}、单案 {n_single}、跳过(已存在) {n_skip}、失败 {n_fail}")
    print(f"输出目录：{oa_assign._share_dir()}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
