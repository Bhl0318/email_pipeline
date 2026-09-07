"""dingtalk 收发消息用法示例。

OTP matcher 等纯逻辑离线实跑；真实收发需钉钉凭据+SDK+联网，只示范写法。

运行：python3 scripts/reusable/examples/dingtalk_demo.py
"""
import os
import re
import sys

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "foundation"))
from dingtalk import send_message, wait_for_reply  # noqa: E402


def otp_matcher(text):
    """从回复里提数字验证码：≥4 位数字即采纳，否则 None（给 wait_for_reply 用）。"""
    digits = re.sub(r"\D", "", text or "")
    return digits if len(digits) >= 4 else None


if __name__ == "__main__":
    print("== OTP matcher（离线）==")
    for t in ["验证码 123456", "你好", "8342"]:
        print(f"  {t!r:16} -> {otp_matcher(t)}")
    # '验证码 123456'->'123456'；'你好'->None；'8342'->'8342'

    print("\n== 真实收发（需钉钉凭据+SDK+联网，仅示范写法）==")
    print('''
    from dingtalk import send_message, wait_for_reply

    # 发消息（凭据走参数/环境变量/email_config.json 的 dingtalk 段）
    send_message("毕海灵", "当前进展：环节3 已完成")

    # 收消息：发提示后等对方回复机器人，收到含验证码的即返回（超时→None）
    send_message("毕海灵", "请回复 USPTO 验证码")
    code = wait_for_reply(otp_matcher, timeout=300)
    ''')
