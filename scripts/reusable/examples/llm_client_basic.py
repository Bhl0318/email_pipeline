"""llm_client 用法示例。

真正发起调用需要有效 api_key（环境变量或 scripts/email_config.json 的 llm 段）。
不带 key 运行时，chat/vision 会 fail-soft 返回 None 并打 stderr。
"""
import os
import sys

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "integration"))
import llm_client  # noqa: E402


def demo_text():
    # 文本调用：返回原文
    reply = llm_client.chat("用一句话解释什么是专利答复期限。", max_tokens=100)
    print("text:", reply)

    # 文本调用：要求 JSON 输出并自动解析
    data = llm_client.chat(
        '只输出 JSON：{"months": 3}', max_tokens=50, extract="json")
    print("json:", data)


def demo_vision(image_path):
    # 图片调用：image 可为路径 / bytes / base64 字符串 / data URI
    text = llm_client.vision(
        [image_path], "这页官文里答复期限是几个月？只输出 JSON: {\"months\": <int>}",
        max_tokens=50, extract="json")
    print("vision:", text)


if __name__ == "__main__":
    demo_text()
    if len(sys.argv) > 1:
        demo_vision(sys.argv[1])
