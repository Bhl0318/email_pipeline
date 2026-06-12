# email_pipeline

邮件统一调度：一封邮件**只读一次、只分类一次**，扇出给「OA 立项」和「汇报信」两条下游流程。
设计细节见 [DESIGN.md](DESIGN.md)。

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
    { "account": "docketing", "folder": "TEST" },
    { "account": "attorneys", "folder": "TEST" }
  ],
  "sinks": { "oa": true, "report": true },
  "oa_test_project_prefix": "90009" }
```

- `sinks.report` / `sinks.oa`：两个 sink 独立开关。灰度已完成，**当前两条都开**（曾以 `oa:false, report:true` 先验证调度框架，OA 跑通后置 true）。
- `accounts`：当前读 `docketing`（CN+US）与 `attorneys`（EP）两个账号。
- `oa_test_project_prefix`：OA sink 测试期只对该案号前缀的案件落库，限定灰度范围。

## 副本来源 commit

| 副本 | 复制自 | 复制时 commit |
|------|--------|--------------|
| `scripts/report/` | `汇报信流程/scripts/` | 4e08db6 时点 |
| `scripts/oa/` | `OA立项/scripts/` | 214db50 时点 |
| `scripts/report/report_server.py`+`submission/`、`scripts/web/`、`scripts/templates/` | `汇报信流程/`（同步审核服务全量依赖，email_pipeline 成唯一运行入口） | f5b3229 时点 |
