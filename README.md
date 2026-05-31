# email_pipeline

邮件统一调度：一封邮件**只读一次、只分类一次**，扇出给「OA 立项」和「汇报信」两条下游流程。
设计细节见 [DESIGN.md](DESIGN.md)。

## 目录

```
scripts/
├── main.py              # 入口：读+分类(一次) → 扇出两 sink → 归档(一次)
├── loader.py            # importlib 隔离加载 oa/ 与 report/（同名模块不串味）
├── pipeline_config.json # 账号列表 + sink 开关
├── email_config.json    # 共用邮箱凭据（gitignore，需本地放置）
├── oa/                  # 复制自 OA立项/scripts/（在副本上拆了函数）
└── report/              # 复制自 汇报信流程/scripts/（在副本上拆了函数）
```

> **原则**：原始 `OA立项/`、`汇报信流程/` 不改动，email_pipeline 自带副本。
> 副本会与原始脚本漂移，原始侧改了分类/字段需手动同步到 `oa/`、`report/`。

## 跑

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
cp /path/to/email_config.json scripts/email_config.json   # 放共用凭据
cd scripts && python3 main.py
```

⚠️ `main.py` 会连真实邮箱 + 数据库 + 发邮件，属有副作用脚本，请在受控环境运行。

## sink 开关（`pipeline_config.json`）

```json
{ "accounts": [{ "account": "docketing", "folder": "TEST" }],
  "sinks": { "oa": false, "report": true } }
```

- `sinks.report=true / oa=false`（默认）：先只跑汇报信，灰度验证调度框架。
- OA 验证无误后把 `oa` 置 true，两条一起跑。

## 副本来源 commit

| 副本 | 复制自 | 复制时 commit |
|------|--------|--------------|
| `scripts/report/` | `汇报信流程/scripts/` | 4e08db6 时点 |
| `scripts/oa/` | `OA立项/scripts/` | 214db50 时点 |
