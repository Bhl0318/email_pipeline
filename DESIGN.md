# email_pipeline — 邮件统一调度方案

> 创建日期：2026-05-31
> 目标：一封邮件**只读一次、只分类一次**，扇出给「OA 立项」和「汇报信」两条下游流程。
> 状态：已落地（`scripts/main.py`、`loader.py`、两 sink 副本均已实现）。本文档为设计依据，实现细节以代码为准。

---

## 一、要解决的问题

当前 `DS/OA立项/scripts/read_email.py` 和 `DS/汇报信流程/scripts/read_email.py` 是两个**各自独立**的入口：

- 各自登录 docketing 邮箱、各自读 `TEST` 文件夹
- 各自维护 `checkpoint.json`
- 各自把处理完的邮件 `move_emails` 到 `TEST_AUTO`

**冲突隐患**：两条流程读的是**同一个邮箱、同一批邮件**。谁先跑，谁就把邮件归档到 `TEST_AUTO`，另一条流程再读时邮件已不在 `TEST`，于是漏处理。

**业务事实**：同一封邮件（如 CN 审查意见通知书）**既要立项、又要发汇报信**——不是二选一，而是**一份输入扇出两个下游**。

`email_pipeline` 就是这个统一入口：**独占邮箱读取 + 单次分类 + 扇出两个 sink + 单次归档**。

---

## 二、关键前提（已核对代码）

### 2.1 前半段（读 + 分类）两侧几乎相同

`汇报信流程/scripts/classify_report.py` 与 `OA立项/scripts/filter_oa_email.py` 去注释后**只差 2 行**：

```
> item["message_id"] = email_data.get("message_id", "")  # 汇报信侧用：关联 saved_pdfs
> "message_id", "email_subject", "email_from",           # OUTPUT_FIELDS 多了 message_id
```

→ **汇报信版分类模块是 OA 版的严格超集**，用它做单次分类，两个 sink 都够用。

### 2.2 读邮件逻辑：汇报信版多了官文 PDF 保存

`汇报信流程/scripts/read_email.py` 比 OA 版多：

- `_save_pdf_attachments_to_inbox()`（L448）：把转达邮件里的官文 PDF 存到 `output/_inbox/`
- `parse_message` 里 `parsed["saved_pdfs"]`（L752）

OA 侧的 US 官文是另走 USPTO API 下载（`us_deadline.py`），与这里的"邮件附件 PDF"是两回事，互不影响。

→ **email_pipeline 的读取层采用汇报信版（超集）**，OA sink 不用 `saved_pdfs` 字段，无副作用。

### 2.3 后半段（sink）才真正不同

| | OA 立项 sink（现 `OA立项/read_email.py` L712-825） | 汇报信 sink（现 `汇报信流程/read_email.py` L910-1026） |
|--|--|--|
| US 期限 | `us_deadline.get_us_deadline()` 下载+解析 PDF | 不涉及 |
| Wiki | `oainfo_cli.append_oa_to_wiki()` | 不涉及 |
| 主数据库 | `INSERT projects`（当前注释） | `INSERT projects`（当前注释）+ `INSERT report_tasks` |
| 附件 | 不涉及 | 官文 PDF 从 `_inbox` 移到 `output/{案号}/source/` |
| 通知邮件 | `send_notification()` 发立项汇总 | `send_review_links_email()` 发审核链接 |

---

## 三、目标架构

```
                 docketing 邮箱（唯一读取方：email_pipeline）
                          │ IMAP + OAuth2
                          ▼
        ┌─────────────────────────────────────────────┐
        │ email_pipeline/main.py                        │
        │                                               │
        │ ① read_and_classify()                         │
        │    复用「汇报信版」read_email + classify       │
        │    产出 (emails, results)                     │
        │       results: list[result_dict]（含 region/ │
        │       notification_type/project/message_id…） │
        │       emails:  原始邮件（含 saved_pdfs）       │
        │                                               │
        │ ② 扇出（同一份 results 喂两个 sink）           │
        │    ├─ dispatch_oa(results)                    │
        │    └─ dispatch_report(results, emails)        │
        │                                               │
        │ ③ archive_emails()                            │
        │    单一 checkpoint + 单次 move → TEST_AUTO     │
        └───────────────┬───────────────┬───────────────┘
                        │               │
              ┌─────────▼──────┐  ┌─────▼──────────────┐
              │ OA 立项 sink    │  │ 汇报信 sink         │
              │ US期限→Wiki→    │  │ PDF入库→report_     │
              │ projects→立项   │  │ tasks→审核链接邮件  │
              │ 通知邮件        │  │                    │
              └────────────────┘  └────────────────────┘
```

**扇出语义**：每个 sink 自己决定"这条 result 我管不管"——
- OA sink 处理所有 `region∈{CN,EP,US}` 且命中立项规则的（现有逻辑）
- 汇报信 sink 处理 `REPORT_TYPE_TO_TEMPLATE` 命中的（现有逻辑）
- 同一条 result 可被两个 sink 都接走，互不干扰。

---

## 四、目录结构

```
DS/email_pipeline/
├── DESIGN.md                  # 本文档
├── README.md                  # 跑法 + 上线注意（后补）
├── requirements.txt           # 合并两侧依赖
└── scripts/
    ├── main.py                # ★ 唯一入口：read_and_classify → 扇出 → archive
    ├── loader.py              # importlib 隔离加载工具（解决 oa/report 子包同名模块冲突）
    ├── pipeline_config.json   # 调度配置：账号列表 / sink 独立开关
    ├── email_config.json      # ★ 共用：唯一邮箱凭据 + 通知收件人（gitignore）
    ├── oa/                    # ← 复制自 OA立项/scripts/，在副本上拆函数
    │   ├── read_email.py          # 拆出 read_and_classify_oa() / dispatch_oa()
    │   ├── filter_oa_email.py     # 分类引擎（原样复制）
    │   ├── db_query.py            # 原样复制
    │   ├── us_deadline.py / downloadByAPI.py / parse_us_pdf.py / oainfo_cli.py
    │   └── ...
    └── report/                # ← 复制自 汇报信流程/scripts/，在副本上拆函数
        ├── read_email.py          # 拆出 read_and_classify() / dispatch_report() / archive_emails()
        ├── classify_report.py     # 分类引擎（原样复制）
        ├── db_query.py / us_deadline.py / enrich_report.py / report_server.py
        └── ...
```

**核心原则（2026-05-31 修订）**：
**两个原始文件夹 `OA立项/` 和 `汇报信流程/` 一律不动。**
email_pipeline **自带一份副本**（`oa/` + `report/` 两个子目录），所有"拆 __main__ 为函数"的改造只在副本上做。
这与项目既有做法一致——`汇报信流程/` 本身就是 `OA立项/` 脚本的副本（见 7.6 主流程一致原则）。

> ⚠️ **同步成本**：副本会随时间与原始脚本漂移。后续原始侧改了分类规则/字段，需手动同步到 `email_pipeline/scripts/{oa,report}/`。在 README 标注每个子目录"复制自哪个 commit"以便追踪。

### 4.1 `pipeline_config.json`（sink 独立开关）

```json
{
  "accounts": [
    { "account": "docketing", "folder": "TEST" },
    { "account": "attorneys", "folder": "TEST" }
  ],
  "sinks": {
    "oa":     true,
    "report": true
  },
  "oa_test_project_prefix": "90009"
}
```

`main.py` 按 `sinks.oa` / `sinks.report` 决定是否调用对应 dispatch。
分阶段灰度上线设计：初期 `oa:false, report:true` 先只开汇报信验证调度框架，OA 验证无误后把 `oa` 置 true。
**当前状态：灰度已完成，两 sink 均开**；`oa_test_project_prefix` 限定 OA sink 落库的案号前缀范围。

### 4.2 `email_config.json`（副本共用一份）

原始两侧各有一份 `scripts/email_config.json`（邮箱 OAuth2 凭据 + 通知收件人）。
**决策：email_pipeline 用 `email_pipeline/scripts/email_config.json` 这一份，`oa/` 和 `report/` 两个副本都读它。**

实现：副本脚本里 `CONFIG_PATH = os.path.join(SCRIPT_DIR, "email_config.json")` 指向自己子目录。
在副本上加一个 `set_config_path()`，由 `main.py` 注入上层那份共用 config，使 `oa/` 和 `report/` 读同一份凭据。

---

## 五、调用机制：importlib 隔离加载（作用于副本）

### 5.1 为什么不能直接 import

副本 `email_pipeline/scripts/oa/` 和 `report/` 下仍有同名文件：
`read_email.py`、`db_query.py`、`us_deadline.py`、`email_config.json`。
直接 `import read_email` 两次只会拿到先入 `sys.modules` 的那一份，后者被屏蔽。

### 5.2 方案：每个子包在自己的目录上下文里加载

`loader.py` 提供一个工具，按目录隔离加载模块：

```python
# 伪代码（待实现）
def load_module_from(dir_path, module_name, alias):
    """把 dir_path/module_name.py 以唯一 alias 注册进 sys.modules，
    加载时临时把 dir_path 插到 sys.path[0]，使其内部 import 解析到本目录的同名文件。"""
    ...
```

`main.py` 用它分别拿到（注意：加载的是 email_pipeline 自带的副本，不碰原始文件夹）：

```python
OA   = load_dir("email_pipeline/scripts/oa")      # 内部 import filter_oa_email / us_deadline / oainfo_cli 都解析到 oa/ 副本
RPT  = load_dir("email_pipeline/scripts/report")   # 内部 import classify_report / db_query / enrich 都解析到 report/ 副本

OA.set_config_path(SHARED_CONFIG)             # 注入共用 email_config.json
RPT.set_config_path(SHARED_CONFIG)

emails, results = RPT.read_and_classify()    # 读取层用 report 副本（分类是 OA 的超集）
if cfg.sinks.oa:     OA.dispatch_oa(results)          # OA 下游（默认关）
if cfg.sinks.report: RPT.dispatch_report(results, emails)  # 汇报信下游（默认开）
RPT.archive_emails(emails)                     # 单次归档（只在这里 move）
```

> 隔离加载的细节（`sys.path` 现场切换、`sys.modules` 命名空间）在实现时统一封进 `loader.py`，main.py 只见到干净的 `OA.xxx` / `RPT.xxx`。

---

## 六、副本上的改造（复制 + 在副本上拆函数，原始文件夹不动）

原则：**先把两侧 scripts 整目录复制到 `email_pipeline/scripts/{oa,report}/`，再在副本上把 `__main__` 拆成函数，逻辑 byte-for-byte 不动。** 原始 `OA立项/`、`汇报信流程/` 零改动。

### 6.1 `oa/`（复制自 `OA立项/scripts/`）

整目录复制后，在 `oa/read_email.py` 上拆出（内容来自原 `__main__` L663-825）：

| 函数 | 来源 | 职责 |
|--|--|--|
| `read_and_classify_oa()` | L663-710 | 读邮件 + checkpoint + `process_emails` |
| `dispatch_oa(results)` | L732-825 | US 期限 → Wiki → `projects`（注释保持）→ `send_notification` |
| `set_config_path()` | 新增 | 供 main.py 注入共用 config |

### 6.2 `report/`（复制自 `汇报信流程/scripts/`）

整目录复制后，在 `report/read_email.py` 上拆出：

| 函数 | 来源 | 职责 |
|--|--|--|
| `read_and_classify()` | L848-902 | 读邮件 + `process_emails` + 建 `msgid_to_saved_pdfs` 索引；**返回 (emails, results)** |
| `dispatch_report(results, emails)` | L910-1026 | PDF 入 `output/{案号}/source` → `INSERT report_tasks` → 发审核链接邮件 |
| `archive_emails(emails)` | L904-908 | 单次 `move_emails` → `TEST_AUTO` |
| `set_config_path()` | 新增 | 供 main.py 注入共用 config |

> ⚠️ 副本里 `dispatch_report` 段的 `INSERT projects` 与汇报信写库混在一个循环（L910-1024），**整段照搬不拆**。测试硬编码 `v = '90009-0003US03'`（L942）维持原状，上线前处理（见 §九）。

### 6.3 归档归谁

`email_pipeline` 模式下：**只有 `archive_emails()` 执行一次 move**，两个 sink 内部不再 move。
`dispatch_oa` 副本里若含 move（OA 原 L706-710 在读取循环内），改造副本时把 move 剥离交给 `archive_emails`。

---

## 七、改动清单（全部在 email_pipeline 内，原始两文件夹零改动）

| 文件 | 改动 | 类型 |
|--|--|--|
| `email_pipeline/scripts/oa/**` | 复制自 `OA立项/scripts/`，在副本 `read_email.py` 上拆 `read_and_classify_oa`/`dispatch_oa`/`set_config_path` | 新增（副本+改副本） |
| `email_pipeline/scripts/report/**` | 复制自 `汇报信流程/scripts/`，在副本 `read_email.py` 上拆 `read_and_classify`/`dispatch_report`/`archive_emails`/`set_config_path` | 新增（副本+改副本） |
| `email_pipeline/scripts/loader.py` | 新建：importlib 隔离加载 | 新增 |
| `email_pipeline/scripts/main.py` | 新建：入口 + 扇出 | 新增 |
| `email_pipeline/scripts/pipeline_config.json` | 新建：账号/sink 开关 | 新增 |
| `email_pipeline/requirements.txt` | 新建：合并两侧依赖 | 新增 |
| `OA立项/**`、`汇报信流程/**` | **不动** | — |

> 建议执行顺序（每步单独 commit）：
> 1. 复制 `汇报信/scripts` → `report/`，在副本上拆函数 + 自测能独立跑
> 2. 复制 `OA立项/scripts` → `oa/`，在副本上拆函数 + 自测
> 3. 写 `loader.py` + `main.py` + `pipeline_config.json` + `requirements.txt`，串起来

---

## 八、风险与测试用例

| # | 风险 | 测试用例 |
|--|--|--|
| 1 | importlib 隔离失败：两侧同名模块（db_query/us_deadline）串味 | 加载后断言 `OA.db_query.__file__` 与 `RPT.db_query.__file__` 指向各自目录 |
| 2 | 单次分类用汇报信版，OA sink 拿不到期望字段 | 对同一批邮件，分别跑「OA 独立入口」与「email_pipeline」，diff `results`（除 message_id 外应一致） |
| 3 | 归档被执行两次 / 完全没执行 | 跑一次后查 `TEST` 与 `TEST_AUTO`：每封邮件应恰好 move 一次 |
| 4 | 一封邮件被两个 sink 处理时，PDF/通知重复或互删 | CN OA 邮件：验证 `report_tasks` 有行 + 立项通知含该案，且官文 PDF 未被 OA sink 误删 |
| 5 | 某个 sink 抛异常拖垮整条流水线 | dispatch 用 try/except 包裹，单 sink 失败不影响另一 sink 与归档 |
| 6 | checkpoint 由谁更新——双写导致回退 | 确认只有 `archive_emails` 更新 checkpoint，sink 内不动 |

---

## 九、上线前清理（沿用两侧现有 TODO，不在本方案范围）

- 汇报信 `INSERT projects` 测试硬编码 `90009-0003US03`（read_email L942）
- 两侧 `ACCOUNTS` 读的是 `TEST` 文件夹、归档到 `TEST_AUTO`（测试残留）
- OA 侧 `projects` INSERT / Wiki OA 信息记录表 / US PDF 等当前注释项的启用，由各自流程负责，email_pipeline 不擅自开启。

---

## 十、已确认决策（2026-05-31）

1. **sink 独立开关：加。** `pipeline_config.json` 用 `sinks.oa` / `sinks.report` 两个布尔位，灰度初期先只开汇报信（`oa:false, report:true`），OA 跑通后再开 → 见 §4.1。**现状：两 sink 均已开。**
2. **email_config.json 共用一份：是。** 统一用 `email_pipeline/scripts/email_config.json`，配置路径由 main.py 注入到两侧 → 见 §4.2。
3. **通知邮件分别发两封：是（维持现状）。** OA sink 走 `send_notification()` 发立项汇总；汇报信 sink 走 `send_review_links_email()` 发审核链接。两封独立，互不合并。
