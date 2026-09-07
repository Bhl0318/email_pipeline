# llm_client —— 大模型调用与路由（接口说明）

**做什么用**：一个入口统一调用大模型——发文本给 DeepSeek 或发图片给千问（qwen），密钥集中在配置里、可选自动解析 JSON、任何异常都返回 None 不中断主流程（fail-soft）。从各文件内联的调用收敛而来。

可运行示例：`python3 scripts/reusable/examples/llm_client_basic.py`。

## 如何 import + 配置

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/integration")
import llm_client
```

key 优先级：环境变量（`DEEPSEEK_API_KEY`/`QWEN_API_KEY`）> `scripts/email_config.json` 的 `llm` 段 > 无（不再硬编码）。base_url/model 有公开默认值。缺 key 时 fail-soft 返回 None。

## 逐函数：作用 / 输入 / 返回

### `chat(messages, *, profile="deepseek", model=None, max_tokens=1024, temperature=None, timeout=60, extract="text", response_format=None)`

**作用**：发一段文本给大模型，取回答；可要求返回并自动解析 JSON。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `messages` | **必填** | list[{"role","content"}]，或直接传 str（当作单条 user 消息） |
| `profile` | 可选 | `"deepseek"`（默认）｜`"qwen"`，决定 key/base/默认 model |
| `model` | 可选 | 覆盖默认 model |
| `max_tokens` / `temperature` / `timeout` | 可选 | 默认 1024 / 不传 / 60 秒 |
| `extract` | 可选 | `"text"`（默认，返回原文）｜`"json"`（自动解析） |
| `response_format` | 可选 | 如 `{"type":"json_object"}`；默认不传 |

**返回**：`extract="text"`→str；`extract="json"`→dict/list（解析成功）或 None；任何异常→None。

### `vision(images, prompt, *, profile="qwen", model=None, max_tokens=1024, timeout=60, mime="image/png", extract="text")`

**作用**：发图片给多模态模型做 OCR 或判断（如从扫描件官文读答复期限）。

| 输入参数 | 必填/可选 | 说明 |
|---|---|---|
| `images` | **必填** | list，每项：base64 字符串 / data URI / bytes / 本地文件路径（内部统一编码） |
| `prompt` | **必填** | str，文本指令 |
| `profile` | 可选 | 默认 `"qwen"` |
| `model` / `max_tokens` / `timeout` | 可选 | 同 chat |
| `mime` | 可选 | 默认 `"image/png"`（裸 base64/bytes 编码用） |
| `extract` | 可选 | `"text"`（默认）｜`"json"` |

**返回**：str 或（extract="json"）dict/list/None；**无有效图片时直接 None**（不发请求）；异常→None。

## 使用示例

```python
import llm_client

# 文本：取原文
llm_client.chat("用一句话解释专利答复期限。", max_tokens=100)
# -> "专利答复期限是……"（str）

# 文本：要 JSON 并自动解析
llm_client.chat('从这段话提取答复月数，只输出 JSON：{"months": <int>}。原文：……', extract="json")
# -> {"months": 3}

# 图片：扫描件逐页 OCR/判断
llm_client.vision([b64_png_page1, b64_png_page2],
                  '这些官文页里答复期限几个月？只输出 JSON: {"months": <int>}',
                  extract="json")
# -> {"months": 3}；无有效图片时返回 None（不发请求）
```
