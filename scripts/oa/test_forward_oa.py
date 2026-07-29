#!/usr/bin/env python3
"""转OA 收件人/客户公共邮箱 测试。纯逻辑,不连网络。
  cd scripts/oa && python3 test_forward_oa.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from forward_oa import (
    customer_public_email, forward_recipients, PUBLIC_EMAIL_FALLBACK,
    _split_names, get_customer_contacts, forward_cc, FORWARD_FIXED_CC,
    build_forward_body,
)

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


def _fake_execute(bspeople, name_mail):
    """构造假 execute：customer 表返回 bspeople；users 表按名字返回 usermail。"""
    import re

    def execute(sql):
        if "FROM customer" in sql:
            return [{"bspeople": bspeople}] if bspeople is not None else []
        if "FROM users" in sql:
            m = re.search(r"username_zn = '([^']+)'", sql)
            name = m.group(1) if m else ""
            mail = name_mail.get(name)
            return [{"usermail": mail}] if mail else []
        return []
    return execute


def test_split_names():
    ok(_split_names("钱祎,孙竹青") == ["钱祎", "孙竹青"], "半角逗号拆分")
    ok(_split_names("钱祎，孙竹青、李四") == ["钱祎", "孙竹青", "李四"], "全角逗号/顿号拆分")
    ok(_split_names(" 张三 ") == ["张三"], "去空白")
    ok(_split_names("") == [], "空串→空列表")


def test_contacts_multi():
    ex = _fake_execute("钱祎,孙竹青", {"钱祎": "qian.yi@metis-ip.com", "孙竹青": "sun.zq@metis-ip.com"})
    ok(get_customer_contacts("20618-1200CN00", execute=ex) ==
       ["qian.yi@metis-ip.com", "sun.zq@metis-ip.com"], "多接口人→多邮箱")


def test_contacts_missing_user_skipped():
    # 孙竹青 在 users 查不到邮箱 → 跳过
    ex = _fake_execute("钱祎,孙竹青", {"钱祎": "qian.yi@metis-ip.com"})
    ok(get_customer_contacts("20618-1200CN00", execute=ex) == ["qian.yi@metis-ip.com"],
       "查不到邮箱的接口人跳过")


def test_contacts_no_customer():
    ex = _fake_execute("", {})
    ok(get_customer_contacts("20849-0001CN00", execute=ex) == [], "无 bspeople→空")
    ok(get_customer_contacts("", execute=ex) == [], "空案号→空")


def test_cc_fixed_plus_contacts():
    ex = _fake_execute("钱祎,孙竹青", {"钱祎": "qian.yi@metis-ip.com", "孙竹青": "sun.zq@metis-ip.com"})
    cc = forward_cc("20618-1200CN00", execute=ex)
    ok(cc[:7] == FORWARD_FIXED_CC, "抄送前7位=固定7人")
    ok(cc[7:] == ["qian.yi@metis-ip.com", "sun.zq@metis-ip.com"], "固定人员之后接客户接口人")
    ok(len(FORWARD_FIXED_CC) == 7, "固定抄送为7人")


def test_cc_dedup():
    # 接口人邮箱恰好是固定人员之一 → 不重复
    ex = _fake_execute("苏雅", {"苏雅": "ya.su@metis-ip.com"})
    cc = forward_cc("20618-1200CN00", execute=ex)
    ok(cc == FORWARD_FIXED_CC, "接口人与固定人员重复时去重")


def test_forward_body():
    item = {"project": "20633-0128CN00", "notification_type": "第一次审查意见通知书",
            "oa_doc_date": "2026-07-22", "project_deadline": "2026-11-22"}
    body = build_forward_body(item)
    ok("题述申请收到了第一次审查意见通知书" in body, "官文类型填入")
    ok("案号：20633-0128CN00" in body, "案号")
    ok("发文日：2026-07-22" in body, "发文日")
    ok("截止日期：2026-11-22" in body, "截止日期")
    ok("发送人：系统" in body, "落款=系统")


def test_forward_body_no_deadline():
    body = build_forward_body({"project": "X", "notification_type": "补正通知书"})
    ok("待确认" in body, "无期限→待确认")


if __name__ == "__main__":
    for fn in [test_public_email_mapping, test_public_email_fallback, test_recipients,
               test_split_names, test_contacts_multi, test_contacts_missing_user_skipped,
               test_contacts_no_customer, test_cc_fixed_plus_contacts, test_cc_dedup,
               test_forward_body, test_forward_body_no_deadline]:
        print(f"[{fn.__name__}]")
        fn()
    print(f"\n全部通过：{_passed} 项断言")
