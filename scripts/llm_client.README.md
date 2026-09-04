# llm_client —— 统一大模型调用模块（接口说明）

把散在各文件的 DeepSeek / qwen 调用收敛成一处，消除硬编码 key 与重复的 client 建法。
fail-soft：任何异常 → 打 stderr → 返回 None，不会因模型不可达中断主流程。
目前为纯新增资产，未迁移原调用方（原 8 个文件仍保留各自内联实现）。

可运行示例：`python3 scripts/examples/llm_client_basic.py`（需有效 key 才真发请求；无 key 时 fail-soft 返回 None）。

## 如何调

```python
import os, sys
sys.path.insert(0, "<...>/scripts")      # 让 llm_client 可被 import
import llm_client
```

## 配置（key 来源，优先级：环境变量 > 配置文件 > 无兜底）

- 环境变量：`DEEPSEEK_API_KEY` / `QWEN_API_KEY`（可选 `DEEPSEEK_BASE_URL`/`DEEPSEEK_MODEL` 等覆盖）。
- 配置文件：`scripts/email_config.json` 的 `llm` 段（模块优先读这份）：
  ```jsonc
  "llm": {
    "deepseek": { "api_key": "sk-...", "base_url": "https://api.deepseek.com", "model": "deepseek-chat" },
    "qwen":     { "api_key": "sk-...", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-vl-max" }
  }
  ```
- 无硬编码兜底 key；缺 key 时调用会 fail-soft 返回 None 并在 stderr 提示。

## 接口

### `chat(messages, *, profile="deepseek", model=None, max_tokens=1024, temperature=None, timeout=60, extract="text", response_format=None)`

文本调用。

| 参数 | 输入 | 说明 |
|---|---|---|
| messages | list[{"role","content"}] 或 str | 传 str 时当作单条 user 消息 |
| profile | "deepseek"｜"qwen" | 选路，决定 key/base/默认 model |
| model | str｜None | 覆盖默认 model |
| max_tokens / temperature / timeout | int / float｜None / int | temperature 为 None 时不传 |
| extract | "text"｜"json" | json 时自动抠 JSON 并解析 |
| response_format | dict｜None | 如 `{"type":"json_object"}`；None 不传 |

- **输出**：`extract="text"` → str（模型原文，已 strip）；`extract="json"` → dict/list（解析成功）或 None；任何异常 → None。
- **示例**：
  ```python
  llm_client.chat("用一句话解释专利答复期限。", max_tokens=100)
  # -> "……"（str）
  llm_client.chat('只输出 JSON：{"months": 3}', extract="json")
  # -> {"months": 3}
  ```

### `vision(images, prompt, *, profile="qwen", model=None, max_tokens=1024, timeout=60, mime="image/png", extract="text")`

图片调用（多模态 OCR/判断）。

| 参数 | 输入 | 说明 |
|---|---|---|
| images | list | 每项可为：base64 字符串 / data URI / bytes / 本地文件路径，内部统一编码 |
| prompt | str | 文本指令 |
| profile | 默认 "qwen" | — |
| mime | str | 裸 base64/bytes 编码时的 MIME，默认 image/png |
| extract | "text"｜"json" | 同 chat |

- **输出**：str 或（extract="json"）dict/list/None；无有效图片时直接 None（不发请求）；异常 → None。
- **示例**：
  ```python
  llm_client.vision([b64_png_str], '答复期限几个月？只输出 JSON: {"months": <int>}', extract="json")
  # -> {"months": 3}
  ```

## 迁移状态

现有内联调用点（DeepSeek/qwen 各处 `OpenAI(...)+create(...)`）分布在
`oa/{parse_us_pdf,parse_cn_pdf,parse_us_refs,filter_oa_email,oa_schemes,oa_report_ai,word_to_wiki}.py`、
`report/classify_report.py`、`submission/qa_seed.py`，共 16 处——**尚未迁移**，待后续逐个替换为 `chat/vision`。
