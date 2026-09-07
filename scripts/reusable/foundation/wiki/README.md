# wiki —— Confluence 读写客户端（接口说明）

**做什么用**：读写 Confluence Wiki 页面的客户端——按标题或 pageId 读页、搜页、在父页下建子页、更新页面内容、给页面传附件。地址和账号走配置，不写死。

从 `oa/oainfo_cli.py` 的 WikiClient 抽出，逻辑不变；改动：base_url/账号由硬编码改走配置，去掉 headers 里残留的无效 `Authorization: Bearer <access_token>` 占位（实际是 basic auth）。依赖：requests。

可运行示例：`python3 scripts/reusable/examples/wiki_demo.py`。

## 如何 import + 配置

```python
import os, sys
sys.path.insert(0, "<...>/scripts/reusable/foundation")
from wiki import WikiClient
wc = WikiClient()          # 走配置/环境变量；也可 WikiClient(base_url=..., user=..., password=...)
```

连接优先级：构造参数 > 环境变量 `WIKI_BASE_URL`/`WIKI_USER`/`WIKI_PASSWORD` > `scripts/email_config.json` 的 `wiki` 段（base_url/user/password）。

## 接口

`WikiClient(base_url=None, user=None, password=None)` 构造（都可选，缺则走环境变量/配置）。

| 方法 | 作用 | 输入 | 返回 |
|---|---|---|---|
| `search_page(title)` | 按标题搜页 | title: str | results 列表；失败→[] |
| `get_page(title)` | 按标题取页（storage 格式） | title: str | `{id, version, body, space_key}` 或 None |
| `get_page_by_id(page_id)` | 按 pageId 取页 | page_id: str | `{id, title, version, body, space_key}` 或 None |
| `update_page(page_id, title, content, version)` | 更新页面内容 | page_id；title；content: storage HTML；version: 当前版本号（内部 +1） | HTTP 状态码（200 成功） |
| `create_child_page(title, content, space_key, parent_id)` | 在父页下建子页 | title；content: storage HTML；space_key；parent_id | HTTP 状态码 |
| `upload_attachment(page_id, filepath)` | 给页面传附件（同名自动更新版本） | page_id；filepath | True/False |

## 使用示例

```python
from wiki import WikiClient
wc = WikiClient()

page = wc.get_page_by_id("241276196")               # 读页 -> {id,title,version,body,space_key}
wc.update_page(page["id"], page["title"], new_html, page["version"])  # 改内容(version内部+1)
wc.create_child_page("OA信息记录表-新案", storage_html, space_key="ZU123", parent_id="123456")
wc.upload_attachment("241276196", "/path/官文.pdf")  # 传附件
```

> storage HTML 的拼装（如 OA 记录表格）是业务逻辑，不在本客户端；本模块只负责读写页面本身。

## 来源与改动

- 抽自：`oa/oainfo_cli.py` 的 `WikiClient`。
- 改动：base_url/账号由硬编码改走 参数/环境变量/`email_config.json` 的 wiki 段；去掉无效的 Authorization 占位头。逻辑不变。
