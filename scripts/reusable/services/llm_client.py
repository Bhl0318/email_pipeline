"""统一大模型调用模块（可复用资产）。

把散在各文件里的 DeepSeek / qwen 调用收敛成一处：两个薄封装 chat() / vision()
+ 配置读取 _cfg()，消除硬编码 key 与重复的 client 建法。

设计约定：
- fail-soft：任何异常 → 打 stderr → 返回 None，与被替换的旧代码语义一致，
  不会因模型不可达而中断主流程。
- profile 两个预设：'deepseek'（文本）、'qwen'（图片 OCR/判断）；model= 可覆盖。
- key 来源优先级：环境变量 > email_config.json 的 llm 段 > 无（不再有硬编码兜底）。
  base_url / model 是公开信息，保留非机密默认值。

本模块目前为独立资产，尚未接入在跑的调用方；迁移是后续独立步骤。
用法示例见 examples/llm_client_basic.py。
"""

import base64
import json
import os
import sys

# profile → (env key 变量名, 默认 base_url, 默认 model)
_PROFILES = {
    "deepseek": ("DEEPSEEK_API_KEY", "https://api.deepseek.com", "deepseek-chat"),
    "qwen": ("QWEN_API_KEY", "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-vl-max"),
}

# email_config.json 的候选位置（隔离加载下 oa/ 与 report/ 各自独占 sys.path，
# 故按顺序探测，用第一个存在的）。
# 本模块在 scripts/reusable/services/ 下，email_config.json 在 scripts/（上溯两级）
_SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_CONFIG_CANDIDATES = [
    os.path.join(_SCRIPTS_DIR, "email_config.json"),
    os.path.join(_SCRIPTS_DIR, "report", "email_config.json"),
]


def _load_llm_config():
    """读 email_config.json 的 llm 段；读不到返回 {}。"""
    for path in _CONFIG_CANDIDATES:
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f).get("llm") or {}
        except Exception:
            continue
    return {}


def _cfg(profile):
    """按 profile 解析 (api_key, base_url, model)。

    优先级：环境变量 > 配置文件 llm.<profile> > 默认。api_key 无兜底。
    """
    if profile not in _PROFILES:
        raise ValueError(f"未知 profile: {profile}（可选 {list(_PROFILES)}）")
    env_key_name, def_base, def_model = _PROFILES[profile]
    section = _load_llm_config().get(profile) or {}
    api_key = os.environ.get(env_key_name) or section.get("api_key")
    base_url = os.environ.get(f"{profile.upper()}_BASE_URL") or section.get("base_url") or def_base
    model = os.environ.get(f"{profile.upper()}_MODEL") or section.get("model") or def_model
    return api_key, base_url, model


def _extract_json(text):
    """从模型输出里抠出 JSON 对象/数组并解析；失败返回 None。

    兼容 ```json 围栏与前后夹带说明文字的情况。
    """
    if not text:
        return None
    import re
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", s).strip()
    try:
        return json.loads(s)
    except Exception:
        m = re.search(r"[\{\[].*[\}\]]", s, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                return None
    return None


def _client(profile):
    from openai import OpenAI  # 延迟导入，保持模块 import 轻量
    api_key, base_url, _ = _cfg(profile)
    if not api_key:
        raise RuntimeError(
            f"缺少 {profile} 的 api_key：请设环境变量或在 email_config.json 的 llm.{profile} 中配置。")
    return OpenAI(api_key=api_key, base_url=base_url)


def chat(messages, *, profile="deepseek", model=None, max_tokens=1024,
         temperature=None, timeout=60, extract="text", response_format=None):
    """文本调用。

    messages: 消息列表 [{"role","content"}]；也可直接传 str（当作单条 user 消息）。
    extract:  'text' 返回原文字符串；'json' 返回解析后的 dict/list（失败 None）。
    异常 → stderr → None。
    """
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    _, _, def_model = _cfg(profile)
    kwargs = {"model": model or def_model, "max_tokens": max_tokens,
              "timeout": timeout, "messages": messages}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if response_format is not None:
        kwargs["response_format"] = response_format
    try:
        resp = _client(profile).chat.completions.create(**kwargs)
        content = (resp.choices[0].message.content or "").strip()
    except Exception as e:  # noqa: BLE001
        print(f"[llm_client.chat] {profile} 调用失败: {e}", file=sys.stderr)
        return None
    return _extract_json(content) if extract == "json" else content


def vision(images, prompt, *, profile="qwen", model=None, max_tokens=1024,
           timeout=60, mime="image/png", extract="text"):
    """图片调用（多模态）。

    images: 列表，每项可为
      - 已编码的 base64 字符串（现有调用方即此形态）
      - data URI（"data:image/...;base64,..."），原样使用
      - bytes（原始图片字节，内部编码）
      - 本地文件路径（内部读取并编码）
    prompt: 文本指令。
    异常 → stderr → None。
    """
    content = [{"type": "text", "text": prompt}]
    for img in images or []:
        url = _to_data_uri(img, mime)
        if url:
            content.append({"type": "image_url", "image_url": {"url": url}})
    if len(content) == 1:  # 没有有效图片
        return None
    _, _, def_model = _cfg(profile)
    try:
        resp = _client(profile).chat.completions.create(
            model=model or def_model, max_tokens=max_tokens, timeout=timeout,
            messages=[{"role": "user", "content": content}])
        text = (resp.choices[0].message.content or "").strip()
    except Exception as e:  # noqa: BLE001
        print(f"[llm_client.vision] {profile} 调用失败: {e}", file=sys.stderr)
        return None
    return _extract_json(text) if extract == "json" else text


def _to_data_uri(img, mime):
    """把多形态图片输入统一成 data URI；无法识别返回 None。"""
    if not img:
        return None
    if isinstance(img, bytes):
        b64 = base64.b64encode(img).decode()
        return f"data:{mime};base64,{b64}"
    if isinstance(img, str):
        if img.startswith("data:"):
            return img
        if os.path.isfile(img):
            with open(img, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return f"data:{mime};base64,{b64}"
        return f"data:{mime};base64,{img}"  # 视作已编码 base64
    return None
