# email_pipeline

邮件统一调度：一封邮件**只读一次、只分类一次**，扇出给「OA 立项」和「汇报信」两条下游流程。
设计细节见 [DESIGN.md](DESIGN.md)。

## OA 立项现状（2026-07 已上线）

`main.py` 每 30 分钟一轮（Windows `scripts/run_pipeline.bat` → 激活 venv → `python main.py --interval 30`）。
当前 `sinks.oa=true`、`sinks.report=false`（只跑 OA 立项）。

**链路**：读 INBOX + docketing 的 `Metis+Porus+Poseidon/Done`（Done 标 `no_archive` 只读不移）
→ 分类 → **已结案案件跳过立项**（查 IPEasy `p_case_info JOIN i_case_status`，状态 ∈ {终止,维持,结案}）
→ 立项（建 Wiki OA 信息表页 / US 官文下载算期限 / CN 解析对比文件写回 / 写 `projects` / 写新增OA登记页）
→ **转OA**：逐案发给 OA 团队（收件人 = 杨姣+薄佳璐+客户公共邮箱；抄送 = 固定8人(含张琴)+客户接口人；正文 OP02 模板落款“系统”；附官文 PDF；pa 账号发）。

**关键规则**（`oa/filter_oa_email.py` 顶部常量 + `oa/forward_oa.py`）：
- US NOA 仅 `{20608,20618,20849,20633,20609}` 立项；`M327`/`PREDOCK.NTF`/eGrant 不立项
- CN 办理登记手续通知书 仅 `{20618,20735}` 立项
- 全局排除：主题含 `reminder` / `向外国申请专利保密审查意见通知书` → 不立项
- 无 checkpoint 时回溯窗口 1 天；checkpoint 已开，按 message_id 去重
- 类型/期限详表见 [oa/OA类型与期限规则.md](scripts/oa/OA类型与期限规则.md)；转OA SOP 见 [oa/OP02-转达OA人员.md](scripts/oa/OP02-转达OA人员.md)

**先验证**：`python main.py --dry-run`（不写库/不发信/不移邮件，逐封打印转OA的收件人/抄送/附件）。

## 目录

```
scripts/
├── main.py              # 批处理入口：读+分类(一次) → 扇出两 sink → 归档(一次)
├── loader.py            # importlib 隔离加载 oa/ 与 report/（同名模块不串味）
├── pipeline_config.json # 账号列表 + sink 开关
├── email_config.json    # 共用邮箱凭据（gitignore，需本地放置）
├── web/                 # 审核页前端（prototype.html / submission.html + js）
├── templates/           # 汇报信模板（md/ + docx/）
├── oa/                  # 复制自 OA立项/scripts/（在副本上拆了函数）
└── report/              # 复制自 汇报信流程/scripts/（在副本上拆了函数）
    ├── report_server.py     # ★FastAPI 审核服务（含 /submission 路由组）
    ├── submission/          # US 递交文件生成（含 templates/ docx+pdf）
    └── email_config.json    # 审核服务独用凭据（gitignore，standalone 跑时放这）
```

> **原则**：原始 `OA立项/`、`汇报信流程/` 是上游源，只在那里改，再手动同步下来。
> email_pipeline 自带全部副本，是**唯一运行入口**——批处理（`main.py`）和审核服务
> （`report/report_server.py`）都在这里跑。

## 跑

### ① 批处理（读邮件 → 扇出 → 归档）

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
cp /path/to/email_config.json scripts/email_config.json   # 放共用凭据
cd scripts && python3 main.py
```

⚠️ `main.py` 会连真实邮箱 + 数据库 + 发邮件，属有副作用脚本，请在受控环境运行。

### ② 审核服务（汇报信 + US 递交在线审核）

```bash
cp /path/to/email_config.json scripts/report/email_config.json   # standalone 独用
cd scripts/report && python3 report_server.py                    # 监听 :8501
```

- 路径基准：`ROOT = scripts/`，服务读 `scripts/web/`、`scripts/templates/md/`，
  预览/官文 PDF 挂载 `scripts/output/`——与 `main.py` 批处理写官文 PDF 的目录**同一棵树**，
  pipeline 存的 PDF 审核页可直接预览。
- 系统依赖：PDF 预览需 `libreoffice`（`apt install libreoffice-writer --no-install-recommends`），
  非 pip 依赖。

## sink 开关（`pipeline_config.json`）

```json
{ "accounts": [
    { "account": "docketing", "folder": "INBOX" },
    { "account": "docketing", "folder": "Metis+Porus+Poseidon/Done", "no_archive": true },
    { "account": "attorneys", "folder": "INBOX" }
  ],
  "sinks": { "oa": true, "report": false },
  "oa_test_project_prefix": null }
```

- `sinks.report` / `sinks.oa`：两个 sink 独立开关。**当前 `oa:true, report:false`**（只跑 OA 立项；汇报信线待启用）。
- `accounts`：读 `docketing` 的 `INBOX`（CN）+ `Metis+Porus+Poseidon/Done`（US，`no_archive` 只读不移）、`attorneys` 的 `INBOX`（EP）。
- `oa_test_project_prefix`：测试期案号前缀替换开关，**当前 `null`（已停用）**。

## 副本来源 commit

| 副本 | 复制自 | 复制时 commit |
|------|--------|--------------|
| `scripts/report/` | `汇报信流程/scripts/` | 4e08db6 时点 |
| `scripts/oa/` | `OA立项/scripts/` | 214db50 时点 |
| `scripts/report/report_server.py`+`submission/`、`scripts/web/`、`scripts/templates/` | `汇报信流程/`（同步审核服务全量依赖，email_pipeline 成唯一运行入口） | f5b3229 时点 |
