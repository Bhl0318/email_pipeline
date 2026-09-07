"""钉钉接收消息（基础通用层 · 网络与服务调用）。

范式抽自 patent_center_ui.py 的 _otp：用钉钉机器人 Stream Mode（WebSocket）直接收用户回复，
无需公网回调。把"从回复里提取什么"泛化成 matcher，收到第一条命中的即返回。

依赖：dingtalk-stream（惰性导入，未装则返回 None）。
"""
import sys
import threading


def wait_for_reply(matcher, timeout=300, client_id=None, client_secret=None):
    """启动钉钉 Stream，等用户回复机器人，返回第一条被 matcher 命中的结果；超时/失败返回 None。

    输入：
      matcher   callable(text)->结果|None：对每条收到的消息文本判定，返回非 None 即采纳
      timeout   最长等待秒数（默认 300）
      client_id / client_secret  钉钉应用凭据；不给则走环境变量/配置（见 send.resolve_creds）
    输出：matcher 命中的结果；超时/未装 SDK/启动失败 → None
    """
    from .send import resolve_creds
    cid, csec, _ = resolve_creds(client_id, client_secret)
    if not cid or not csec or "****" in (csec or ""):
        print("[dingtalk] 未配置完整的 client_id/secret（secret 不能是掩码）", file=sys.stderr)
        return None
    try:
        import dingtalk_stream
    except Exception:
        print("[dingtalk] 未安装 dingtalk-stream（pip install dingtalk-stream）", file=sys.stderr)
        return None

    result = {"value": None}
    got = threading.Event()

    def run_stream():
        try:
            from dingtalk_stream import AckMessage

            class Handler(dingtalk_stream.ChatbotHandler):
                async def process(self, callback):
                    try:
                        m = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
                        txt = (m.text.content if getattr(m, "text", None) else "") or ""
                    except Exception as ex:
                        print(f"[dingtalk] 消息解析失败：{ex}", file=sys.stderr)
                        return AckMessage.STATUS_OK, "OK"
                    hit = matcher(txt)
                    if hit is not None:
                        result["value"] = hit
                        got.set()
                    return AckMessage.STATUS_OK, "OK"

            cred = dingtalk_stream.Credential(cid, csec)
            client = dingtalk_stream.DingTalkStreamClient(cred)
            client.register_callback_handler(dingtalk_stream.ChatbotMessage.TOPIC, Handler())
            client.start_forever()
        except Exception as ex:
            print(f"[dingtalk] Stream 启动失败：{ex}", file=sys.stderr)
            got.set()

    threading.Thread(target=run_stream, daemon=True).start()
    if got.wait(timeout) and result["value"] is not None:
        return result["value"]
    return None
