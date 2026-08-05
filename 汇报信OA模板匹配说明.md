# OA 汇报信模板匹配说明

> 讲清楚：一封 OA 官文邮件，系统怎么决定**用哪个汇报信模板**。
> 对应代码：`scripts/report/read_email.py` 的 `REPORT_TYPE_TO_TEMPLATE`（模板映射）与 `oa_report_rules.json`（分派规则）；模板文件在 `scripts/templates/md/`。
> 最后更新：2026-08-04

---

## 一、两层分离（先记住这个）

OA 汇报信的处理分**两层，各管各的**：

| 层 | 决定什么 | 依据 | 代码 |
|---|---|---|---|
| **模板层** | **用哪个汇报信模板** | 只看 **(国别, 通知类型)** | `REPORT_TYPE_TO_TEMPLATE` |
| **分派层** | **发不发、发给谁** | **客户 × 通知类型 × 次数** | `oa_report_rules.json` |

**要点：模板只由"国别+类型"决定，与客户、次数无关。** 客户/次数只影响"发不发、发给谁"，不改变用哪个模板。

---

## 二、模板匹配（模板层）

匹配逻辑（`dispatch_report`）：

```python
tpl_info = REPORT_TYPE_TO_TEMPLATE.get(region, {}).get(notification_type)
if tpl_info:
    template, attach_pdf = tpl_info    # 命中即用这个模板；attach_pdf 决定是否附官文 PDF
# 未命中 → 该类型不发汇报信
```

- **命中** → 拿到 `(模板名.md, 是否附官文PDF)`。
- **没命中** → 该类型不生成汇报信。

### 当前 OA 类型 → 模板对照

**CN**（4 类，通知类型＝主题关键字）
| 通知类型 | 模板 | 附 PDF |
|---|---|:--:|
| 审查意见通知书 | `CN_官方审查意见转达.md` | 是 |
| 补正通知书 | `CN_补正通知.md` | 是 |
| 驳回决定 | `CN_驳回决定.md` | 是 |
| 复审通知书 | `CN_复审通知书.md` | 是 |

**US**（通知类型＝正文 Document Type 代码）
| 类型 | 模板 | 附 PDF |
|---|---|:--:|
| CTNF / CTFR / CTAV / CTRS / CTEQ | `US_官方审查意见转达.md` | 是 |
| NT.CR.APP.PA / M327 / NTC.MISS.PRT / PETDEC | `US_补正通知转达.md` | 是 |

**EP**（通知类型＝主题【…】通信类型）
| 通信类型 | 模板 | 附 PDF |
|---|---|:--:|
| Communication A.94(3) | `EP_官方审查意见转达.md` | 是 |
| Communication R.62a(1) | `EP_官方审查意见转达.md` | 是 |
| European search report | `EP_扩展检索报告.md` | 是 |
| Further search fee | `EP_部分检索报告.md` | 是 |
| Intention to grant | `EP_预授权通知.md` | 是 |
| Summons to oral proceedings | `EP_庭审邀请.md` | 是 |

---

## 三、几个容易混淆的点

1. **同类型不同客户 → 同一个模板**。模板只看类型；发给联影还是滴滴、发不发，是分派层的事，模板不变。
2. **审查意见第一次 / 第二次 → 同一个模板**（都是 `CN_官方审查意见转达.md`）。次数 N 只填进模板里的 `{{N}}` 占位（"第 N 次审查意见"），不换模板。
3. **US 补正类的衔接**：`NT.CR.APP.PA / M327 / NTC.MISS.PRT / PETDEC` 在 `REPORT_TYPE_TO_TEMPLATE` 里**仍映射着** `US_补正通知转达.md`，但 `oa_report_rules.json` 里是 `ignore` → **分派层先拦下、`tpl_info` 置空 → 实际不生成**。即"模板映射还在，但被判为不处理，所以不发"。

---

## 四、完整判定顺序（OA 一封邮件）

```
一封 OA 官文邮件
  │
  ① classify_report：发件人定国别；类型(CN/EP 取主题、US 取正文 Document Type)
  │      → region + notification_type
  ▼
  ② REPORT_TYPE_TO_TEMPLATE[region][type]  ←【模板层】
  │      命中 → (模板.md, 附PDF)；未命中 → 不发
  ▼
  ③ oa_report_rules.json 查 客户码×类型×次数  ←【分派层】
  │      assign → 建 report_tasks(用②的模板) + 发给规则里的准备人
  │      skip   → 不建汇报信（记录应转发去向，二期真转发）
  │      ignore → 不建、不处理
  ▼
  ④ assign 命中 → 审核页用②选中的模板渲染汇报信 → 准备人核对/发出
```

> 一句话：**②决定"长什么样"（模板），③决定"发不发、发给谁"**。两步都过、且③是 assign，才会生成这封汇报信。

---

## 五、代码位置

- 模板映射：`scripts/report/read_email.py` 的 `REPORT_TYPE_TO_TEMPLATE`
- 分派规则：`scripts/report/oa_report_rules.json` + `_resolve_oa_action()`
- 模板文件：`scripts/templates/md/`（如 `CN_官方审查意见转达.md`）
- 分类识别：`scripts/report/classify_report.py`
- 相关文档：`汇报信类型与匹配规则.md`（类型识别）、`汇报信OA规则开发流程.md`（分派分期）、`汇报信规则矩阵-2026-07-30.md`（V4 全量规则）
