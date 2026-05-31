# email_pipeline — 邮件统一调度方案

> 创建日期：2026-05-31
> 目标：一封邮件**只读一次、只分类一次**，扇出给「OA 立项」和「汇报信」两条下游流程。
> 状态：方案设计（未写代码）

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
    ├── loader.py              # importlib 隔离加载工具（解决同名模块冲突）
    └── pipeline_config.json   # 调度配置：账号列表 / 开关 OA sink / 开关汇报信 sink
```

不复制业务逻辑。读取/分类/两个 sink 全部**复用两侧现有代码**。

---

## 五、调用机制：importlib 隔离加载

### 5.1 为什么不能直接 import

`OA立项/scripts/` 和 `汇报信流程/scripts/` 下都有同名文件：
`read_email.py`、`db_query.py`、`us_deadline.py`、`email_config.json`。
直接 `import read_email` 两次只会拿到先入 `sys.modules` 的那一份，后者被屏蔽。

### 5.2 方案：每个 sink 在自己的目录上下文里加载

`loader.py` 提供一个工具，按目录隔离加载模块：

```python
# 伪代码（待实现）
def load_module_from(dir_path, module_name, alias):
    """把 dir_path/module_name.py 以唯一 alias 注册进 sys.modules，
    加载时临时把 dir_path 插到 sys.path[0]，使其内部 import 解析到本目录的同名文件。"""
    ...
```

`main.py` 用它分别拿到：

```python
OA   = load_dir("DS/OA立项/scripts")        # 内部 import filter_oa_email / us_deadline / oainfo_cli 都解析到 OA 目录
RPT  = load_dir("DS/汇报信流程/scripts")     # 内部 import classify_report / db_query / enrich 都解析到汇报信目录

emails, results = RPT.read_and_classify()    # 读取层用汇报信版（超集）
OA.dispatch_oa(results)                       # OA 下游
RPT.dispatch_report(results, emails)          # 汇报信下游
RPT.archive_emails(emails)                     # 单次归档（只在这里 move）
```

> 隔离加载的细节（`sys.path` 现场切换、`sys.modules` 命名空间、相对 import）在实现时统一封进 `loader.py`，main.py 只见到干净的 `OA.xxx` / `RPT.xxx`。

---

## 六、两侧需要的改动（重构，不改逻辑）

原则：**把现有 `__main__` 块原样搬进函数，逻辑 byte-for-byte 不动**，只是从"脚本直接跑"变成"可被调用"。每侧 `__main__` 仍保留，改为调用同一个新函数 → 两侧仍可独立跑（备查/单测）。

### 6.1 `OA立项/scripts/read_email.py`

新增三个函数（内容来自现 L663-825 的 `__main__`）：

| 函数 | 来源 | 职责 |
|--|--|--|
| `read_and_classify_oa()` | L663-710 | 读邮件 + checkpoint + `process_emails`（OA 单独跑时用） |
| `dispatch_oa(results)` | L732-825 | US 期限 → Wiki → `projects`（注释保持）→ `send_notification` |

`__main__` 改为：`emails, results = read_and_classify_oa(); dispatch_oa(results); archive...`

### 6.2 `汇报信流程/scripts/read_email.py`

| 函数 | 来源 | 职责 |
|--|--|--|
| `read_and_classify()` | L848-902 | 读邮件 + `process_emails` + 建 `msgid_to_saved_pdfs` 索引；**返回 (emails, results)** |
| `dispatch_report(results, emails)` | L910-1026 | PDF 入 `output/{案号}/source` → `INSERT report_tasks` → 收集并发审核链接邮件 |
| `archive_emails(emails)` | L904-908 | 单次 `move_emails` → `TEST_AUTO` + `update_checkpoint` |

`__main__` 改为：`emails, results = read_and_classify(); dispatch_report(results, emails); archive_emails(emails)`

> ⚠️ 现 `dispatch_report` 段里 `INSERT projects` 与汇报信写库混在一个循环里（L910-1024）。重构时**整段照搬**，不拆不改。其中测试硬编码 `v = '90009-0003US03'`（L942）维持原状，上线前另行处理（见 §九）。

### 6.3 归档归谁

`email_pipeline` 模式下：**只有 `archive_emails()` 执行一次 move**。两个 sink 内部**不再调 move_emails**。
- 实现上：`dispatch_oa` 现有结尾若含 move（OA L706-710 在 read 循环里），需在重构时把 move 从 sink 里剥离，统一交给 `archive_emails`。
- 单独跑某一侧时，该侧 `__main__` 自己负责归档（保持现状）。

---

## 七、改动清单

| 文件 | 改动 | 类型 |
|--|--|--|
| `email_pipeline/scripts/main.py` | 新建：入口 + 扇出 | 新增 |
| `email_pipeline/scripts/loader.py` | 新建：importlib 隔离加载 | 新增 |
| `email_pipeline/scripts/pipeline_config.json` | 新建：账号/sink 开关 | 新增 |
| `email_pipeline/requirements.txt` | 新建：合并两侧依赖 | 新增 |
| `OA立项/scripts/read_email.py` | `__main__` → `read_and_classify_oa()` + `dispatch_oa()`，move 剥离 | 重构 |
| `汇报信流程/scripts/read_email.py` | `__main__` → `read_and_classify()` + `dispatch_report()` + `archive_emails()` | 重构 |

> 超过 3 个文件，按工作规则需拆分子任务确认。建议执行顺序：
> 1. 重构汇报信侧 `read_email.py`（拆函数，`__main__` 调用，自测仍可独立跑）
> 2. 重构 OA 侧 `read_email.py`（同上）
> 3. 写 `loader.py` + `main.py` + 配置 + requirements
> 每步单独 commit，跑通一步再下一步。

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

## 十、待确认

1. `pipeline_config.json` 里 OA sink / 汇报信 sink 是否要做**独立开关**（先只开汇报信、OA 跑通后再开）？
2. 两侧 `email_config.json` 是各用各的，还是 email_pipeline 统一指定一份？（涉及读取用哪个账号凭据）
3. 通知邮件：OA 的「立项通知」与汇报信的「审核链接」是分别发两封，还是合并一封？（现状是两封，建议维持）
