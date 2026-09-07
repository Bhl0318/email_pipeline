# prompts —— 模型指令（提示词）

模型指令没有以文件形式存在，而是放在数据库表里，可外部编辑、改库即生效、读不到回退代码内默认值。因此无法作为文件放入本目录，在此说明其位置与用法。

- 存放：atw 库 `zxassist_result_instruction` 表，按 `mtype` 区分（如 `oa_schemes`、`oaInstruct`）。
- 消费方：`oa/oa_schemes.py`、`oa/oa_report_ai.py`（读取该表的 instruction，读不到用硬编码默认）。
- 复用模式："提示词存库、改库即生效、回退默认"——见 llm_client 及待抽取的"指令外置"。
