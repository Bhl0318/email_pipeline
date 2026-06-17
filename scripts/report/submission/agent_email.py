#!/usr/bin/env python3
"""给美国代理人的邮件正文（代码模板生成，严禁 AI）。

环节4 生成 POA/Transmittal/ADS 后，随附此邮件请美代理签署。
固定模板（业务确认 2026-06-16）：POA、Transmittal 请签署，其他文件已走 DocuSign。
落款：成萍。
"""


def build_agent_email(case_volume: str, recipient: str = "X总/X律师") -> dict:
    """构造给美代理人的邮件。:return: {subject, body, recipient}

    recipient: 称呼（如"Smith 律师"/"张总"），缺省占位"X总/X律师"由审核人改。
    """
    subject = f"{case_volume} 递交文件签署"
    body = (
        f"{recipient}，您好，\n\n"
        "烦请签署题述 POA、Transmittal 文件，其他文件已通过 DocuSign 发送，谢谢。\n\n"
        "祝好！\n"
        "成萍"
    )
    return {"subject": subject, "body": body, "recipient": recipient}


if __name__ == "__main__":
    import json
    print(json.dumps(build_agent_email("64504-H006US00"), ensure_ascii=False, indent=2))
