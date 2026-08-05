#!/usr/bin/env python3
"""邮件动作记录页：行构建 + 按日折叠插入。纯字符串逻辑，不连网络。
  cd scripts/oa && python3 test_email_actions.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from oainfo_cli import (_build_email_action_row, _insert_rows_by_day, _new_day_block,
                        _day_title, build_email_action_records)

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def test_row_moved_yes_no():
    r = _build_email_action_row({"project": "20618-1061US00", "subject": "CTNF",
                                 "received_time": "2026-08-05 09:00", "action": "转OA立项",
                                 "reason": "OA立项官文类型:CTNF", "moved": True})
    ok("<td>20618-1061US00</td>" in r and "<td>是</td>" in r, "moved=True → 是")
    ok("<td>OA立项官文类型:CTNF</td>" in r, "判断依据列有值")
    r2 = _build_email_action_row({"project": "", "action": "无动作", "moved": False})
    ok("<td>否</td>" in r2 and r2.count("<td>") == 6, "moved=False → 否，6 列")


def test_row_escapes_subject():
    r = _build_email_action_row({"project": "X", "subject": "A<b> & <c>", "action": "转发原始", "moved": True})
    ok("&lt;b&gt;" in r and "&amp;" in r and "<b>" not in r, "主题 <>& 被转义")


def test_multi_action_cell():
    r = _build_email_action_row({"project": "X", "action": "转OA立项；转汇报信", "moved": True})
    ok("转OA立项；转汇报信" in r, "多动作合并一格")


def test_insert_into_existing_day():
    day = "2026年8月5日"
    body = _new_day_block(day, _build_email_action_row(
        {"project": "OLD", "action": "转汇报信", "moved": True}))
    new = _build_email_action_row({"project": "NEW", "action": "转OA立项", "moved": True})
    out, created = _insert_rows_by_day(body, new, day)
    ok(created is False, "已有当天块 → 不新建")
    # 新行插到表头之后、旧行之前（置顶）
    ok(out.index("NEW") < out.index("OLD"), "新行置于旧行之前")
    ok(out.index("<th>案号</th>") < out.index("NEW"), "新行在表头行之后")


def test_create_new_day_block_on_top():
    day_old = "2026年8月4日"
    body = _new_day_block(day_old, _build_email_action_row({"project": "OLD", "action": "无动作", "moved": False}))
    new = _build_email_action_row({"project": "NEW", "action": "转OA立项", "moved": True})
    out, created = _insert_rows_by_day(body, new, "2026年8月5日")
    ok(created is True, "无当天块 → 新建")
    ok(out.index("2026年8月5日") < out.index("2026年8月4日"), "新日块置顶(在旧日块之前)")
    ok("NEW" in out and "OLD" in out, "新旧内容都在")


def test_empty_body_creates_block():
    out, created = _insert_rows_by_day("", _build_email_action_row(
        {"project": "X", "action": "无动作", "moved": False}), "2026年8月5日")
    ok(created is True and "2026年8月5日" in out and "<th>案号</th>" in out, "空页 → 建块含表头")


def test_day_title_no_pad():
    import datetime
    ok(_day_title(datetime.datetime(2026, 8, 5)) == "2026年8月5日", "日标题不补零")


# ---------- 聚合 build_email_action_records ----------
def _em(mid, subject, date="2026-08-05 09:00"):
    return ("acc", {"message_id": mid, "subject": subject, "date": date})


def test_agg_merge_two_actions():
    # 同一案既转OA立项又分配汇报信 → 合并一行，动作/依据都合并
    results = [{"message_id": "<m1>", "project": "20618-1061CN00", "email_subject": "OA1"}]
    emails = [_em("<m1>", "第一次审查意见-20618-1061CN00")]
    oa = [{"message_id": "<m1>", "project": "20618-1061CN00", "action": "转OA立项", "reason": "OA立项官文类型:审查意见通知书"}]
    rep = [{"message_id": "<m1>", "project": "20618-1061CN00", "action": "分配汇报信", "reason": "命中汇报信模板:CN/审查意见通知书"}]
    recs = build_email_action_records(results, emails, oa, rep)
    ok(len(recs) == 1, "一案一行")
    ok(recs[0]["action"] == "转OA立项；分配汇报信", "多动作合并")
    ok("OA立项官文类型" in recs[0]["reason"] and "命中汇报信模板" in recs[0]["reason"], "依据合并")
    ok(recs[0]["moved"] is True, "命中→moved=True")


def test_agg_matched_no_action():
    results = [{"message_id": "<m2>", "project": "X-CN00", "email_subject": "S"}]
    emails = [_em("<m2>", "S")]
    recs = build_email_action_records(results, emails, [], [])
    ok(recs[0]["action"] == "无动作" and recs[0]["reason"] == "" and recs[0]["moved"] is True,
       "命中但无动作 → 无动作/空依据/moved=True")


def test_agg_unmatched_email():
    results = []
    emails = [_em("<m3>", "某封未命中邮件")]
    recs = build_email_action_records(results, emails, [], [])
    ok(len(recs) == 1 and recs[0]["project"] == "" and recs[0]["action"] == "无动作"
       and recs[0]["reason"] == "未命中OA/汇报信分类" and recs[0]["moved"] is False,
       "未命中邮件 → 案号空/无动作/依据未命中/moved=False")


def test_agg_multi_case_one_email():
    # 一封US邮件两案，各自动作
    results = [{"message_id": "<m4>", "project": "A-US00", "email_subject": "US"},
               {"message_id": "<m4>", "project": "B-US00", "email_subject": "US"}]
    emails = [_em("<m4>", "US docketing")]
    oa = [{"message_id": "<m4>", "project": "A-US00", "action": "转OA立项", "reason": "r1"}]
    recs = build_email_action_records(results, emails, oa, [])
    ok(len(recs) == 2, "两案两行")
    a = next(r for r in recs if r["project"] == "A-US00")
    b = next(r for r in recs if r["project"] == "B-US00")
    ok(a["action"] == "转OA立项" and b["action"] == "无动作", "同封不同案动作各自归位")
    ok(a["subject"] == "US docketing", "主题取自原邮件")


if __name__ == "__main__":
    for fn in [test_row_moved_yes_no, test_row_escapes_subject, test_multi_action_cell,
               test_insert_into_existing_day, test_create_new_day_block_on_top,
               test_empty_body_creates_block, test_day_title_no_pad,
               test_agg_merge_two_actions, test_agg_matched_no_action,
               test_agg_unmatched_email, test_agg_multi_case_one_email]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
