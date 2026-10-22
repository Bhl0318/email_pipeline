# Mistral OCR：PDF 解析接口与返回格式

本文按仓库中现有实现整理，适合开发独立的 PDF → Markdown 解析功能。现有实现有两层：项目自建的 OCR HTTP 服务，以及服务内部调用的 Mistral 官方 API。

## 一、调用现有 OCR 服务（推荐复用）

服务代码：`projects/mistral-ocr-service/service.py`；项目内客户端：`DS/email_pipeline/scripts/oa/mistral_ocr.py`。

### 请求

| 项目 | 值 |
| --- | --- |
| 方法和路径 | `POST {OCR_SERVICE_URL}/ocr` |
| 鉴权 | 请求头 `X-API-Key: {SERVICE_API_KEY}` |
| 请求体 | `multipart/form-data`，字段 `file` 为 PDF 文件 |
| 可选参数 | `?format=md`：返回纯 Markdown；默认返回 JSON |
| 服务端配置 | `SERVICE_API_KEY` 用于校验客户端；`MISTRAL_API_KEY` 用于调用 Mistral |

服务按同步方式工作，OCR 完成后才响应。当前部署文档的示例地址为 `https://149.248.15.179:8445`，实际地址以部署配置为准。该地址使用自签证书；正式接入时宜配置受信任证书。

```bash
curl -X POST "${OCR_SERVICE_URL}/ocr" \
  -H "X-API-Key: ${OCR_SERVICE_KEY}" \
  -F "file=@/path/to/sample.pdf"
```

### JSON 返回

```json
{
  "filename": "sample.md",
  "pages": 2,
  "elapsed": 8.4,
  "markdown": "第一页识别内容\n\n---\n\n第二页识别内容"
}
```

| 字段 | 含义 |
| --- | --- |
| `filename` | 由上传文件名改后缀得到的 `.md` 文件名 |
| `pages` | PDF 页数；未安装页数识别依赖或识别失败时可能为 `null` |
| `elapsed` | 服务端 OCR 耗时，单位秒 |
| `markdown` | 全文 Markdown；各页按原页序排列，以 `\n\n---\n\n` 分隔 |

若只需要正文，可调用 `POST {OCR_SERVICE_URL}/ocr?format=md`，响应的 `Content-Type` 为 `text/markdown; charset=utf-8`，响应体直接是 Markdown 文本。

```python
import os
from pathlib import Path
import requests

pdf_path = Path("sample.pdf")
with pdf_path.open("rb") as pdf:
    response = requests.post(
        os.environ["OCR_SERVICE_URL"].rstrip("/") + "/ocr",
        headers={"X-API-Key": os.environ["OCR_SERVICE_KEY"]},
        files={"file": (pdf_path.name, pdf, "application/pdf")},
        timeout=420,
    )
response.raise_for_status()
result = response.json()
markdown = result["markdown"]
pdf_path.with_suffix(".md").write_text(markdown, encoding="utf-8")
```

### 错误及调用注意事项

- 请求不是 `.pdf` 文件：HTTP 400。
- `X-API-Key` 缺失或不匹配：HTTP 401。
- 服务端未配置密钥或内部处理失败：HTTP 500；上游 Mistral HTTP 错误会包装为 HTTP 502。
- 每次请求会重新执行 OCR；如果需要避免重复调用，请在自己的功能中按文件内容或文件版本做缓存。服务端会在处理后删除临时 PDF 和上传至 Mistral 的临时文件。
- PDF 内容会发送到 Mistral OCR API。调用方应按自己的文件权限规则控制上传。

## 二、直接调用 Mistral 官方 API

仓库实现：`projects/set_skill/skill-catalog/skills/mistral-ocr/scripts/mistral_ocr.py`。认证头为 `Authorization: Bearer {MISTRAL_API_KEY}`，模型为 `mistral-ocr-latest`。

1. `POST https://api.mistral.ai/v1/files`：`multipart/form-data` 上传 PDF，附加 `purpose=ocr`；从返回 JSON 的 `id` 取得 `file_id`。
2. `GET https://api.mistral.ai/v1/files/{file_id}/url?expiry=24`：从返回 JSON 的 `url` 取得签名 URL。
3. `POST https://api.mistral.ai/v1/ocr`：发送 JSON：

   ```json
   {
     "model": "mistral-ocr-latest",
     "document": {
       "type": "document_url",
       "document_url": "<上一步得到的签名 URL>"
     }
   }
   ```

4. OCR 响应中的 `pages` 是按页的数组；当前实现取每页的 `index` 排序，再提取各页 `markdown`，用 `\n\n---\n\n` 拼接为全文。
5. 最后调用 `DELETE https://api.mistral.ai/v1/files/{file_id}` 清理临时文件。

`pages` 的核心结构可按下面形式读取；实际响应还可能包含其他字段：

```json
{
  "pages": [
    {"index": 0, "markdown": "第一页内容"},
    {"index": 1, "markdown": "第二页内容"}
  ]
}
```

现有命令行脚本可以直接复用：

```bash
python3 projects/set_skill/skill-catalog/skills/mistral-ocr/scripts/mistral_ocr.py sample.pdf
```

它默认把识别正文写到 PDF 同目录的 `mistral_output/sample.md`，并在标准输出打印包含 `input`、`output`、`filename`、`total_pages`、`elapsed`、`skipped` 的 JSON。输出文件已存在时直接返回，`skipped=true`；失败时输出带 `error` 的 JSON 并以非零状态退出。密钥从环境变量 `MISTRAL_API_KEY` 或脚本同目录 `config.json` 读取。

## 三、两套现有客户端的区别

| 客户端 | 调用目标 | 成功返回 | 失败处理 |
| --- | --- | --- | --- |
| `scripts/oa/mistral_ocr.py` 的 `pdf_to_markdown(pdf_path)` | 项目自建服务 `/ocr` | Markdown 字符串 | 未配置或多次失败返回空字符串；本进程内按路径、修改时间和大小缓存成功结果 |
| `skills/mistral-ocr/scripts/mistral_ocr.py` 命令行 | Mistral 官方 API | Markdown 文件路径写入 JSON 标准输出，正文写入 `.md` 文件 | HTTP 错误直接上报；连接/超时错误最多重试 3 次 |

如果新功能需要稳定的机器可读结果，建议调用自建服务的 JSON 接口，并以 `markdown` 作为解析正文；如果需要页级数据或图片等官方完整响应字段，则直接接 Mistral API，并保留原始响应。
