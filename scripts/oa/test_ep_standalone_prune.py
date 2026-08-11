#!/usr/bin/env python3
"""复现并锁定：R.70(2)/70a(2)(standalone_project=False) 经 OUTPUT_FIELDS 裁剪后
布尔 False 必须保留，否则 dispatch_oa 的 EP 过滤失效 → R.70(2) 误入 OA 立项。
用 LIVE 副本 report/classify_report.py；mock DeepSeek，不连网络。
  cd scripts/oa && python3 test_ep_standalone_prune.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "..", "report"))
import classify_report as R  # noqa: E402

R._ai_parse_ep_deadline = lambda *a, **k: {"deadline": "2027-02-11", "issue_date": "2026-08-11"}

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def _ed(project="20608-0401EP00"):
    return {
        "subject": f"【Communication R.70(2) & 70a(2) EPC】  EP Application (EP24939056.8) "
                   f"- Your Ref.: {project}; Our Ref: MQVT318PEP25 ",
        "from": "Mail Panovision IP <mail@panovision-ip.com>",
        "body": "due date 2027-02-11", "html_body": "", "message_id": "<x>",
    }


def test_standalone_false_survives_pruning():
    res, _skipped, _unknown = R.process_emails([_ed()])
    ok(len(res) == 1, "R.70(2) 进 results(供汇报信 sink)")
    sp = res[0].get("standalone_project")
    ok(sp is False, f"standalone_project 保留为布尔 False(不是空串) (got {sp!r})")


def test_dispatch_oa_filter_drops_it():
    res, _s, _u = R.process_emails([_ed()])
    it = res[0]
    # 复刻 dispatch_oa 入口过滤：EP 且 standalone_project is False → 不参与立项
    dropped = (it.get("region") == "EP" and it.get("standalone_project") is False)
    ok(dropped is True, "dispatch_oa 会把 R.70(2) 过滤出 OA 立项(不写新增OA/不写TIP)")
    # 其它区/字段缺失不应被误过滤
    for fake in [{"region": "CN"}, {"region": "US"}, {"region": "EP", "standalone_project": True}]:
        ok(not (fake.get("region") == "EP" and fake.get("standalone_project") is False),
           f"{fake} 不被误过滤")


if __name__ == "__main__":
    for fn in [test_standalone_false_survives_pruning, test_dispatch_oa_filter_drops_it]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
