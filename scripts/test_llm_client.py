"""llm_client 测试用例（离线，不发真实模型请求）。

只验证配置读取、JSON 抠取、图片编码、fail-soft 短路等纯逻辑。

运行：python3 scripts/test_llm_client.py   或   pytest scripts/test_llm_client.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm_client  # noqa: E402


def test_cfg_reads_profiles():
    for profile in ("deepseek", "qwen"):
        _, base, model = llm_client._cfg(profile)
        assert base and model            # 有默认 base/model
    os.environ["DEEPSEEK_API_KEY"] = "env-override"
    try:
        assert llm_client._cfg("deepseek")[0] == "env-override"   # env 覆盖 key
    finally:
        del os.environ["DEEPSEEK_API_KEY"]


def test_cfg_unknown_profile():
    try:
        llm_client._cfg("nope")
    except ValueError:
        return
    raise AssertionError("未知 profile 应抛 ValueError")


def test_extract_json():
    assert llm_client._extract_json('{"months": 3}') == {"months": 3}
    assert llm_client._extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert llm_client._extract_json('前言 {"x": [1,2]} 后语') == {"x": [1, 2]}
    assert llm_client._extract_json("[1, 2, 3]") == [1, 2, 3]
    assert llm_client._extract_json("不是json") is None
    assert llm_client._extract_json("") is None


def test_to_data_uri():
    assert llm_client._to_data_uri(b"abc", "image/png").startswith("data:image/png;base64,")
    du = "data:image/jpeg;base64,QQ=="
    assert llm_client._to_data_uri(du, "image/png") == du          # 已是 data URI 原样
    assert llm_client._to_data_uri("QQ==", "image/png") == "data:image/png;base64,QQ=="
    assert llm_client._to_data_uri(None, "image/png") is None


def test_vision_no_images_returns_none():
    assert llm_client.vision([], "prompt") is None                  # 无图不发请求


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("ok", fn.__name__)
    print(f"all passed ({len(fns)})")
