# OA前端分析 · 外部解析接口

**给谁看**：需要把案件材料推给本系统、让它预先做好 OA前端分析的外部应用开发者。

**做什么**：推一个案号 + 已解析好的 md 材料，本系统从案号识别 CN/US/EP，调用
BoxCheck 同源模型与指令生成 wiki 页面，再解析出权利要求特征对比表并跑完真假档位评分，
产出一个「解析版本」。也可兼容传入已有 wiki 链接，跳过自动生成。该案号对应项目的 OA前端分析模块
**首次进入时自动加载这一版**，代理人不用再自己上传材料解析（省掉 40~60 分钟等待）。

```
外部应用                        本系统
   │  POST /qdfx/external/parse   │
   ├─────────────────────────────>│ 材料落库，自动生成模式立即转后台
   │<─── 202 {parseId, version} ──┤ 生成 wiki → 解析表格 → 评分
   │                              │
   │  GET  /qdfx/external/status  │
   ├─────────────────────────────>│
   │<── {status: processing…}  ───┤   轮询建议 5~10 分钟一次
   │<── {status: completed}    ───┤   完成 → 代理人进模块即可看到评分结果
```

- 服务地址：**前端地址** + `/assist`，前端会把 `/assist` 转发到后端；后端端口不对外开放，
  请勿直接调后端
  - 测试环境：`http://10.10.70.88:8082/assist`
  - 正式环境：`http://10.10.70.88:8088/assist`
- 鉴权：请求头 `X-Api-Token`，值来自本系统 `backend/config.py` 的 `QDFX_API_TOKEN`；
  该项留空表示接口未启用，一律回 503
- **成败同时看 HTTP 状态和响应体 `code`**：自动生成任务受理成功返回 HTTP/code 202；
  兼容 Wiki 模式成功返回 200；鉴权失败 401，未启用 503。

---

## 1. 触发解析 + 评分

`POST /assist/qdfx/external/parse`　Content-Type: `multipart/form-data`

| 参数 | 必填 | 说明 |
|---|---|---|
| `caseNo` | 是 | 案号，≤100 字符。解析按它归档，模块靠它命中 |
| `wikiUrl` | 否 | 兼容参数。提供时直接解析该页面；未提供时根据案号自动生成 wiki |
| `createdBy` | 否 | 发起方标识，≤50 字符，默认 `external`；显示在版本列表的解析人处 |
| 材料文件 | 是 | **字段名 = 文件类型**，值是解析好的 md 文件；同名字段可重复传多份 |

材料字段名取值：`scyj` 审查意见 / `sqwj` 申请文件 / `qlqy` 权利要求 / `jiaodi` 交底书 /
`claim` 权利要求书 / `dbwj` 对比文件 / `other` 其他。

**三类必须齐备**，缺任一类回 400：审查意见（`scyj`）、申请文件（`sqwj`/`qlqy`/`jiaodi`
任选其一）、对比文件（`dbwj`）。`other` 等额外材料可随意追加，一并喂给评分 AI。

### curl

```bash
curl -X POST http://10.10.70.88:8082/assist/qdfx/external/parse \
  -H "X-Api-Token: <token>" \
  -F "caseNo=20615-0011US00" \
  -F "createdBy=writeSYS" \
  -F "scyj=@审查意见.md" \
  -F "sqwj=@申请文件.md" \
  -F "dbwj=@对比文件1.md" \
  -F "dbwj=@对比文件2.md" \
  -F "other=@检索报告.md"
```

### Python

```python
import requests

API = 'http://10.10.70.88:8082/assist'   # 正式环境换成 http://10.10.70.88:8088/assist
HEAD = {'X-Api-Token': '<token>'}

files = [
    ('scyj', ('审查意见.md', open('审查意见.md', 'rb'), 'text/markdown')),
    ('sqwj', ('申请文件.md', open('申请文件.md', 'rb'), 'text/markdown')),
    ('dbwj', ('对比文件1.md', open('对比文件1.md', 'rb'), 'text/markdown')),
    ('dbwj', ('对比文件2.md', open('对比文件2.md', 'rb'), 'text/markdown')),
]
res = requests.post(f'{API}/qdfx/external/parse', headers=HEAD, files=files, data={
    'caseNo': '20615-0011US00',
    'createdBy': 'writeSYS',
}).json()

if res['code'] not in (200, 202):
    raise RuntimeError(res['msg'])          # 400/401/409 的原因都在 msg 里
parse_id = res['data']['parseId']
```

### 成功返回

自动生成模式立即返回 HTTP 202：

```json
{"code": 202, "msg": "任务已提交，Wiki生成及AI评分进行中",
 "data": {
   "parseId": "bfe04aa8-3c63-43cd-aff4-27e66ad64667",
   "caseNo":  "20615-0011US00",
   "region":  "US",
   "version": 3,
   "status":  "processing",
   "fileIds": ["52d9fb9a-b233-11f1-a28c-f9a14fa312ef", "52d9fb9b-…"]
 }}
```

提供 `wikiUrl` 的兼容模式仍在同步解析页面后返回 `code: 200`、`rows` 和 `title`。

| 字段 | 说明 |
|---|---|
| `parseId` | 本次解析的 id，查状态用它 |
| `version` | 该案号下的版本号。案号还没有任何解析时是 1，否则接在最大版本号之后 |
| `fileIds` | 各材料在本系统里的文件 id，顺序同上传顺序 |

### 错误码

| code | 含义 | 处理建议 |
|---|---|---|
| 400 | 缺参数 / 材料不齐 / 案号无法识别地区 / wiki 链接无 pageId / 页面无特征表 | 按 `msg` 修正后重发 |
| 401 | token 无效 | 检查 `X-Api-Token` |
| 409 | 同案号已有一版在解析中（`data.parseId` 是那一版） | 等那一版跑完再提，勿重试 |
| 500 | wiki 页面获取失败 / 入库失败 | 可重试；连续失败找本系统维护者看 `logs/qdfx/<parseId>.log` |
| 503 | 外部接口 token 或 BoxCheck 自动生成服务未配置 | 联系本系统维护者开启 |

自动生成仅支持案号以 `CN00`、`US00`、`EP00` 等“地区代码 + 两位数字”结尾；无法识别时
不会默认成 US。自动生成服务未配置时同样返回 HTTP 503，已有 `wikiUrl` 的兼容链路不受影响。

---

## 2. 查进度与结果

`GET /assist/qdfx/external/status/<parseId>`，同样带 `X-Api-Token`。
加 `?detail=1` 时附带整张评分结果表 `tableData`。

```bash
curl "http://10.10.70.88:8082/assist/qdfx/external/status/bfe04aa8-…?detail=1" \
  -H "X-Api-Token: <token>"
```

```python
import time

while True:
    st = requests.get(f'{API}/qdfx/external/status/{parse_id}', headers=HEAD).json()['data']
    if st['status'] in ('completed', 'failed'):
        break
    time.sleep(600)          # 自动生成+评分可能需60~100分钟，10分钟轮询一次足够

if st['status'] == 'failed':
    raise RuntimeError(st['failReason'])
```

```json
{"code": 200, "data": {
  "parseId": "bfe04aa8-…", "caseNo": "20615-0011US00", "version": 3,
  "title": "XX案权利要求特征对比", "wikiUrl": "http://...pageId=123456",
  "status": "processing", "stage": "scoring", "region": "US", "failReason": "",
  "rows": 42, "createdBy": "writeSYS", "parsedAt": "2026-09-17 09:12"}}
```

| 字段 | 说明 |
|---|---|
| `status` | `processing` 评分中 / `completed` 已完成 / `failed` 失败 |
| `stage` | `generating_wiki` / `parsing_wiki` / `scoring` / `completed` / `failed` |
| `wikiUrl` | 自动生成或调用方传入的 wiki 页面；生成完成前为空 |
| `failReason` | 失败原因，仅 `failed` 时非空，末尾附「，可重新解析」 |
| `rows` | 已入库的特征行数 |
| `parsedAt` | 发起解析的时间 |

`parseId` 不存在时返回 `{"code": 404, "msg": "解析不存在"}`（HTTP 仍是 200）。

### `?detail=1` 的 tableData

每个元素是特征对比表的一行：

| 字段 | 说明 |
|---|---|
| `id` | 行号（对应 wiki 表格里的 OA 理由序号） |
| `claim` / `oaReason` / `refContent` | 权利要求特征 / 审查意见理由 / 对比文件内容（wiki 原文） |
| `rowSpan` | 首列合并行数；**0 表示本行是上一行的续行**，不是 1 |
| `isSeparator` | 是否权要分组的分隔行，分隔行没有评分 |
| `isSkip` | AI 标记本行跳过评分；此时档位与 `trueSlot` 全为空，跳过理由在 `reasonA` |
| `tierA` / `tierB` | A、B 两槽的抗辩档位原文 |
| `ordinalA` / `ordinalB` | 对应档位的强弱序号，**仅用于排序着色，不能反查档位名** |
| `trueSlot` | `A` 或 `B`，指出哪一槽是**真实档位**，另一槽是对照用的假档位 |
| `reasonA` / `reasonB` | 两槽各自的理由 |
| `examinerComment` | 该权要对应的审查员评述原文 |
| `aiRawTrue` / `aiRawFake` | 真 / 假档位的 AI 原始 JSON，排查用 |

档位共五档，由强到弱：`直接抗辩-充分`、`直接抗辩-争取`、`修改后抗辩-充分`、
`修改后抗辩-争取`、`暂不抗辩`。

> **真假两槽是做什么的**：系统对每一行同时生成一个真实档位和一个干扰档位，随机放进
> A/B 两槽，让代理人先自己判断再看答案。**真假档位允许相同**，所以不能靠分值差异
> 识别真栏，只能看 `trueSlot`。外部只想要结论时，取 `trueSlot` 指向那一槽的
> `tier*` 和 `reason*` 即可。

---

## 3. 调用方需要知道的四件事

1. **评分跑完之前，模块那边看不到这一版**。自动匹配只认 `completed`；提供现成 Wiki 时
   通常需 40~60 分钟，自动生成 Wiki 后再评分可能需 60~100 分钟。跑失败的版本永远不会
   被匹配到，但会占用一个版本号。
2. **只有"还没用过解析数据"的模块会自动加载**。模块一旦绑定过某一版（自己解析过或
   之前匹配过），就钉住不动，新推的版本不会顶替它 —— 这是为了不让代理人已做的评估
   对不上表格行。所以预处理要赶在代理人自己动手之前推。
3. **材料只需 md 正文，不必传原件**。系统据此建资料页、供 AI 引用；代价是模块里
   「查看原文件」、附图提取、抗辩时喂 PDF 原件这三处降级，不影响解析与评分结果。
4. **别并发推同一个案号**。409 只挡已经在跑的那一版，几乎同时到达的两个请求可能各建
   一版。定时批跑请串行触发。

---

## 4. 自动生成服务部署

BoxCheck 与 zx-sys 配置同一个高强度内部 token：

```bash
cd /root/code/boxcheck
python3 -m pip install -r internal_qdfx_requirements.txt
BOXCHECK_INTERNAL_TOKEN='<token>' python3 run_box_check.py
```

该命令仍按原方式启动邮件轮询服务，并会同时在同一进程启动内部 HTTP 服务，默认监听
`0.0.0.0:9180`。启动 zx-sys 前配置同一个环境变量；服务地址非默认值时再配置
`BOXCHECK_QDFX_URL`：

```bash
export BOXCHECK_INTERNAL_TOKEN='<同一个token>'
export BOXCHECK_QDFX_URL='http://218.4.127.70:9180'
```

健康检查：`GET /internal/frontend-analysis/health`。正式部署应由进程管理器托管，且不要把
token 提交到仓库；如果两套服务不在同一主机，只允许在受控内网访问该端口。

如需临时不启动该接口，可设置 `BOXCHECK_INTERNAL_SERVICE_ENABLED=0`；单独排障时也可直接运行
`internal_qdfx_service.py`，但常规运维不需要增加第二个启动进程。
