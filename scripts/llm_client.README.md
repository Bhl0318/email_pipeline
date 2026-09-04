# llm_client —— 统一大模型调用模块（接口说明）

把散在各文件的 DeepSeek / qwen 调用收敛成一处。fail-soft：异常 → stderr → 返回 None。
目前为纯新增，未迁移原调用方。可运行示例：`python3 scripts/examples/llm_client_basic.py`。
测试：`python3 scripts/test_llm_client.py`（5 条；配置/JSON抠取/图片编码/fail-soft 离线，不发真实请求，已通过）。

## 如何 import + 配置

```python
import os, sys
sys.path.insert(0, "<...>/scripts")
import llm_client
```

key 优先级：环境变量（`DEEPSEEK_API_KEY`/`QWEN_API_KEY`）> `scripts/email_config.json` 的 `llm` 段 > 无（不再硬编码）。base_url/model 有公开默认值。缺 key 时 fail-soft 返回 None。

## 逐函数：调用方法 / 输入 / 返回

### `chat` —— 文本调用

调用方法：
```python
# 取原文
reply = llm_client.chat("用一句话解释专利答复期限。", max_tokens=100)
# 要 JSON 并自动解析
data  = llm_client.chat('只输出 JSON：{"months": 3}', extract="json")
```

| 输入参数 | 说明 |
|---|---|
| `messages` | list[{"role","content"}]，或直接传 str（当作单条 user 消息） |
| `profile` | `"deepseek"`（默认）｜`"qwen"`，决定 key/base/默认 model |
| `model` | str｜None，覆盖默认 model |
| `max_tokens` / `temperature` / `timeout` | int / float｜None（None 不传）/ int=60 |
| `extract` | `"text"`（默认）｜`"json"` |
| `response_format` | dict｜None，如 `{"type":"json_object"}`；None 不传 |

**返回**：`extract="text"` → str（模型原文，已 strip）；`extract="json"` → dict/list（解析成功）或 None；任何异常 → None。

### `vision` —— 图片调用（多模态 OCR/判断）

调用方法：
```python
result = llm_client.vision(
    [b64_png_str],                                   # 或 bytes / 文件路径 / data URI
    '答复期限几个月？只输出 JSON: {"months": <int>}',
    extract="json")
```

| 输入参数 | 说明 |
|---|---|
| `images` | list，每项：base64 字符串 / data URI / bytes / 本地文件路径（内部统一编码） |
| `prompt` | str，文本指令 |
| `profile` | 默认 `"qwen"` |
| `model` / `max_tokens` / `timeout` | 同 chat |
| `mime` | str="image/png"（裸 base64/bytes 编码用） |
| `extract` | `"text"`（默认）｜`"json"` |

**返回**：str 或（extract="json"）dict/list/None；**无有效图片时直接 None**（不发请求）；异常 → None。

## 迁移状态

现有内联调用点（DeepSeek/qwen 各处 `OpenAI(...)+create(...)`）共 16 处，分布在
`oa/{parse_us_pdf,parse_cn_pdf,parse_us_refs,filter_oa_email,oa_schemes,oa_report_ai,word_to_wiki}.py`、
`report/classify_report.py`、`submission/qa_seed.py`——**尚未迁移**，待逐个替换为 `chat/vision`。
