#!/usr/bin/env python3
"""转OA 收件人/客户公共邮箱 测试。纯逻辑,不连网络。
  cd scripts/oa && python3 test_forward_oa.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from forward_oa import customer_public_email, forward_recipients, PUBLIC_EMAIL_FALLBACK

_passed = 0


def ok(cond, msg):
    global _passed
    assert cond, f"FAIL: {msg}"
    _passed += 1
    print(f"  ok - {msg}")


def test_public_email_mapping():
    ok(customer_public_email("20615-0001CN00") == "didi_pa@metis-ip.com", "滴滴")
    ok(customer_public_email("20608-0320US00") == "shokz@metis-ip.com", "韶音")
    ok(customer_public_email("20618-1200CN00") == "ui_pa@metis-ip.com", "联影")
    ok(customer_public_email("20633-0128CN00") == "patent8@metis-ip.com", "大华")


def test_public_email_fallback():
    ok(customer_public_email("20849-0001CN00") == PUBLIC_EMAIL_FALLBACK, "未列出客户→兜底")
    ok(customer_public_email("") == PUBLIC_EMAIL_FALLBACK, "空案号→兜底")


def test_recipients():
    to = forward_recipients("20618-1200CN00")
    ok(to == ["jiao.yang@metis-ip.com", "jialu.bo@metis-ip.com", "ui_pa@metis-ip.com"],
       f"联影收件人 = 杨姣+薄佳璐+联影公共邮箱 (got {to})")
    to2 = forward_recipients("20849-0001CN00")
    ok(to2[-1] == PUBLIC_EMAIL_FALLBACK, "兜底客户收件人末位=兜底邮箱")


if __name__ == "__main__":
    for fn in [test_public_email_mapping, test_public_email_fallback, test_recipients]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
