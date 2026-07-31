#!/usr/bin/env python3
"""备注(oa_remark)取值测试：类型映射 + 同族首案判定。纯逻辑，不连网络。
  cd scripts/oa && python3 test_oa_remark.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from filter_oa_email import type_oa_remark
from oainfo_cli import family_first_case_remark

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


# ---------- 类型映射 ----------
def test_type_fenan():
    ok(type_oa_remark("NOA") == "分案评估", "US NOA → 分案评估")
    ok(type_oa_remark("分案评估") == "分案评估", "CN 办登(notification_type=分案评估) → 分案评估")


def test_type_bohui():
    ok(type_oa_remark("驳回决定") == "驳回复审评估", "驳回决定 → 驳回复审评估")


def test_type_buzheng_us():
    ok(type_oa_remark("NT.CR.APP.PA") == "补正", "US corrected papers → 补正")
    ok(type_oa_remark("NTC.MISS.PRT") == "补正", "US missing parts → 补正")


def test_type_buzheng_cn():
    ok(type_oa_remark("补正答复") == "补正", "CN 补正通知书 → 补正")
    ok(type_oa_remark("复审补正答复") == "补正", "CN 复审请求补正通知书 → 补正")


def test_type_other_oa_empty():
    for nt in ("CTNF", "CTFR", "CTRS", "审查意见答复", "OA1-Non-Final Rejection答复", ""):
        ok(type_oa_remark(nt) == "", f"其他OA/{nt or '空'} → 空(交 dispatch 判同族首案)")


# ---------- 同族首案判定 ----------
def _ex(rows):
    """构造注入 execute：忽略 SQL，返回预置 dict 行。"""
    return lambda sql: rows


def test_first_case_sibling_has_oa():
    # 同族里有个 CN 案已有 OA 立项 → 当前 US 案为非同族首案
    rows = [{"project": "20618-1061CN00", "project_name": "OA1-第一次审查意见答复"},
            {"project": "20618-1061US00", "project_name": "US撰写"}]
    ok(family_first_case_remark("20618-1061US00", "OA1-Non-Final Rejection答复", execute=_ex(rows))
       == "非同族首案", "同族有OA立项 → 非同族首案")


def test_first_case_no_oa():
    rows = [{"project": "20618-1061CN00", "project_name": "CN撰写"},
            {"project": "20618-1061US00", "project_name": "US撰写"}]
    ok(family_first_case_remark("20618-1061US00", "OA1-Non-Final Rejection答复", execute=_ex(rows))
       == "同族首案", "同族无OA立项 → 同族首案")


def test_first_case_excludes_self():
    # 只有当前案自身的 OA 行（若已抢先写入）→ 排除后应判同族首案
    rows = [{"project": "20618-1061US00", "project_name": "OA1-Non-Final Rejection答复"}]
    ok(family_first_case_remark("20618-1061US00", "OA1-Non-Final Rejection答复", execute=_ex(rows))
       == "同族首案", "排除当前案自身行 → 同族首案")


def test_first_case_self_plus_sibling_oa():
    # 自身行被排除，但兄弟案有OA → 仍为非同族首案
    rows = [{"project": "20618-1061US00", "project_name": "OA1-Non-Final Rejection答复"},
            {"project": "20618-1061CN00", "project_name": "OA2-第二次审查意见答复"}]
    ok(family_first_case_remark("20618-1061US00", "OA1-Non-Final Rejection答复", execute=_ex(rows))
       == "非同族首案", "排除自身后兄弟案有OA → 非同族首案")


def test_first_case_empty_family():
    ok(family_first_case_remark("20618-1061US00", "x", execute=_ex([])) == "同族首案",
       "同族无任何行 → 同族首案")


def test_first_case_no_project():
    ok(family_first_case_remark("", "x", execute=_ex([{"project": "a", "project_name": "OAx"}])) == "",
       "空案号 → 空")


def test_first_case_db_error():
    def boom(sql):
        raise RuntimeError("db down")
    ok(family_first_case_remark("20618-1061US00", "x", execute=boom) == "",
       "查库异常 → 空(留空人工补)")


if __name__ == "__main__":
    for fn in [test_type_fenan, test_type_bohui, test_type_buzheng_us, test_type_buzheng_cn,
               test_type_other_oa_empty,
               test_first_case_sibling_has_oa, test_first_case_no_oa, test_first_case_excludes_self,
               test_first_case_self_plus_sibling_oa, test_first_case_empty_family,
               test_first_case_no_project, test_first_case_db_error]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
