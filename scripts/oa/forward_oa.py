#!/usr/bin/env python3
"""转达 OA 人员（转OA）— 把立项后的官文按客户/类型路由转给 OA 处理团队。
规则见 OP02-转达OA人员.md;客户公共邮箱见 P1-客户公共邮箱对照表.md。

本模块按步骤逐步补全,当前已实现:
  - 客户公共邮箱匹配（customer_public_email）
  - 收件人组装（forward_recipients）= 固定人员 + 客户公共邮箱
"""

# 客户案号前缀（案号第一段）→ 客户公共邮箱；未列出的客户用兜底邮箱
CUSTOMER_PUBLIC_EMAIL = {
    "20615": "didi_pa@metis-ip.com",    # 滴滴
    "20608": "shokz@metis-ip.com",      # 韶音
    "20618": "ui_pa@metis-ip.com",      # 联影
    "20633": "patent8@metis-ip.com",    # 大华
}
PUBLIC_EMAIL_FALLBACK = "patents_pa@metis-ip.com"   # 其他/未列出客户兜底

# 转OA 固定收件人（OP02 §3.2.1）：杨姣、薄佳璐
FORWARD_FIXED_TO = [
    "jiao.yang@metis-ip.com",    # 杨姣
    "jialu.bo@metis-ip.com",     # 薄佳璐
]


def customer_public_email(project):
    """按案号前缀（第一段,如 20618）返回客户公共邮箱;未匹配用兜底邮箱。"""
    code = (project or "").split("-")[0].strip()
    return CUSTOMER_PUBLIC_EMAIL.get(code, PUBLIC_EMAIL_FALLBACK)


def forward_recipients(project):
    """转OA 收件人 = 固定人员(杨姣/薄佳璐) + 该客户公共邮箱。去重保序。"""
    to = list(FORWARD_FIXED_TO)
    pub = customer_public_email(project)
    if pub not in to:
        to.append(pub)
    return to


import re as _re


def _split_names(bspeople):
    """把 customer.bspeople 拆成人名列表（支持中英文逗号/顿号/分号分隔，去空白空项）。"""
    return [n.strip() for n in _re.split(r'[,，、;；]', bspeople or '') if n.strip()]


def get_customer_contacts(project, execute=None):
    """客户接口人邮箱列表（转OA 抄送用）:
    atw customer.bspeople(customer_code = 案号前5位) → 拆多个中文名 → 各查 users.usermail。
    查不到 / 异常 → 返回 []（不阻塞抄送）。execute 可注入（测试用），默认用 db_query.execute。"""
    code = (project or "")[:5]
    if not code:
        return []
    if execute is None:
        from db_query import execute as execute
    try:
        safe = code.replace("'", "\\'")
        rows = execute(f"SELECT bspeople FROM customer WHERE customer_code = '{safe}'")
        bspeople = rows[0].get("bspeople") if rows else ""
        mails = []
        for name in _split_names(bspeople):
            sn = name.replace("'", "\\'")
            r2 = execute(f"SELECT usermail FROM users WHERE username_zn = '{sn}'")
            mail = (r2[0].get("usermail") if r2 else "") or ""
            if mail and mail not in mails:
                mails.append(mail)
        return mails
    except Exception as e:
        import sys
        print(f"[转OA] 查客户接口人失败 {code}: {e}", file=sys.stderr)
        return []
