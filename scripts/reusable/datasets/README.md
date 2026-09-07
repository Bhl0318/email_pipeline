# datasets —— 数据资产（模板 / 规则表 / 提示词）

把散在各处、被本库模块消费的数据资产归纳到一处，便于成套查看和复用。

```text
datasets/
├── templates/
│   ├── us_filing/        US 递交空白表单（POA/ADS/Transmittal×3/Declaration×2/Assignment）
│   └── report_letters/   汇报信模板（md/ + docx/，CN/US/EP 结项+OA 各类）
├── rules/
│   └── oa_report_rules.json   OA 分派规则表
└── prompts/
    └── README.md         模型指令（存在 DB 表里，非文件，说明见内）
```

| 数据资产 | 被哪个模块消费 | 真源（在跑的流水线仍读这里） |
|---|---|---|
| templates/us_filing/ | doc_generator 范式（submission 各生成器）、doc_utils.fill_pdf_form | `report/submission/templates/` |
| templates/report_letters/ | 汇报信生成 | `scripts/templates/`（由 `generate_templates.py` 生成） |
| rules/oa_report_rules.json | rule_engine | `report/oa_report_rules.json` |
| prompts/ | llm_client 的调用方（指令外置） | atw 表 `zxassist_result_instruction` |

> ⚠️ 这里是**归纳副本**，方便在库里成套查看。**在跑的流水线仍从上面"真源"路径读取**，改副本不生效；真源更新后需手动刷新本副本（或反之）。要把某套模板随模块打包给别的项目时，从这里取即可。
