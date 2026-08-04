# 汇报信 OA 规则开发流程

> 依据 `汇报信规则矩阵-2026-07-30.md`（源 `2026-07-30-汇报信规则-V4.xlsx`）落地 **OA 官文** 的汇报信规则。
> 范围：`CN-OA官文` / `US-OA官文` / `EP-OA官文` 三张表。
> 分两期：**一期做"判对＋分配准备人"，二期做"转发接口邮箱"**。
> 创建：2026-07-30

---

## 一、总体思路

把"读到一封 OA 官文邮件后**要不要发汇报信、发给谁**"从当前的**只按国别**升级为**按 `客户码 × 官文类型 × 次数` 的矩阵**。

- **一期**：规则表 + 判定逻辑，`分配→准备人`（真发），`不分配/不处理→跳过并记录应转发去向`。
- **二期**：把"不分配→转发接口邮箱+抄送公邮"这一动作自动化（待关键项明确后再做，见 §五）。

**分期理由**：判定逻辑规则清晰、可立即做且是净收益（先把错发/漏发修对）；转发涉及"转发什么内容/形式"和"对应案件接口从哪查"两个未定项，猜错会误发官方文件，风险高，单独一期谨慎做。

---

## 二、一期范围与deliverable

| # | 交付物 | 说明 |
|---|---|---|
| 1 | `report/oa_report_rules.json` | OA 三表的**机器可读规则**（单一真源） |
| 2 | `_resolve_oa_action(region, ntype, project, item)` | 按 `(国别,类型,客户码,次数)` 查规则，返回动作 |
| 3 | `dispatch_report` 接入 | OA 类型改走规则表：分配→建 report_tasks+路由准备人；不分配/不处理→跳过+日志记录应转发去向 |
| 4 | 准备人常量扩充 | 胡梅 mei.hu / 任惠 hui.ren / 王晶 jing.wang |
| 5 | 自测脚本 | dry-run 构造各客户×类型样例，校验决策命中 |

**不在一期**：真正的转发发送、接口人查库、`US官文其他`/`CN-其他官文`/`结项通知`/`PCT` 各表。

---

## 三、规则表设计（`oa_report_rules.json`）

按 `国别 → 官文类型 → 客户码 → 动作` 组织：

```jsonc
{
  "CN": {
    "审查意见通知书@1": {          // 第一次(N=1)
      "20615": {"action": "assign", "preparer": "mei.hu@metis-ip.com"},
      "20608": {"action": "assign", "preparer": "hui.ren@metis-ip.com"},
      "其他":  {"action": "assign", "preparer": "hui.ren@metis-ip.com"},
      "20618": {"action": "skip", "forward": {"to": ["report@metis-ip.com"], "cc": ["ui_pa@metis-ip.com"]}},
      "20735": {"action": "ignore"},
      "…": "…"
    },
    "审查意见通知书@2+": { "…": "…" },   // 第二次及以上(N>=2)
    "补正通知书":  { "…": "…" },
    "驳回决定":    { "…": "…" },
    "复审通知书":  { "…": "…" }
  },
  "US": { "CTNF": {...}, "CTFR": {...}, "CTAV": {...}, "CTRS": {...}, "CTEQ": {...} },
  "EP": { "European search report": {...}, "Communication A.94(3)": {...}, "…": "…" }
}
```

**动作三态**：
- `assign` —— 分配汇报信，`preparer` 为收链接的准备人邮箱。
- `skip` —— 不分配汇报信；`forward.to/cc` 记录**表格要求的转发去向**（一期只记录+日志，不真发）。
- `ignore` —— 不处理（表格"邮件不用处理"）。

**类型 key 与 classify 对齐**：
- CN：`补正通知书 / 驳回决定 / 复审通知书` 直接对应；`审查意见通知书` 按已抽出的**次数 N** 拆成 `@1`(N=1) 与 `@2+`(N≥2)。
- US：Document Type 代码 `CTNF/CTFR/CTAV/CTRS/CTEQ`。（补正类 NT.CR.APP.PA/M327/NTC.MISS.PRT/PETDEC → 表格"无需分配"，见 §四）
- EP：用矩阵表 `备注` 列映射到 classify 通信类型（`European search report`=R.70(2)、`Communication A.94(3)`、`Further search fee`、`Intention to grant`=Decision to grant A.97(1)、`Summons to oral proceedings`、`Communication R.62a(1)`）。

**特殊分支**（一期需处理）：
- CN 驳回决定「其他客户」：`20849/20633 → assign 任惠`，其余 → skip。→ 规则表里对 20633 单列，20849 单列。
- CN 补正通知书「其他客户」：表写"询问接口是否需要分配"→ 一期按 **skip** 处理（存疑，见 §五 待确认）。

---

## 四、与现状的差异（一期会修正）

| 场景 | 现状代码 | 一期后（按表） |
|---|---|---|
| 联影 20618 CN/US OA | 发给任惠 / 王晶（误发） | **不分配**（skip，记录转发 report+ui_pa） |
| US 补正类 NT.CR.APP.PA/M327/NTC.MISS.PRT/PETDEC | 生成 US_补正通知转达 汇报信 | **移除**（无需分配） |
| CN 20615 审查意见 | 统一任惠 | 第一次→胡梅；第二次+→skip |
| EP 20618/20633 | 统一王晶 | ESR/R.70(2)/A.94(3)→skip；Summons/DtG/R.62a→王晶 |
| CN 5开头 | 已跳过 | 保持跳过（表一致，记录转发李艳青+patents_pa） |

> 现有 `REPORT_TYPE_TO_TEMPLATE` 仍决定"用哪个模板"；新规则表叠加在其上决定"分配/跳过/忽略 + 准备人"。US 补正类从 `REPORT_TYPE_TO_TEMPLATE` 移除。

---

## 五、开工前待确认（阻塞项）

1. **客户判定**：客户码＝**案号前 5 位**；"5开头案号"＝首位为 5；"其他客户"＝未在列表中的 → 确认无误？
2. **审查意见次数**：用系统抽出的 **N**，N=1 走"第一次"、N≥2 走"第二次及以上" → 确认？
3. **CN 补正通知书「其他客户」**"询问接口是否需要分配"——一期按 **skip** 处理，对吗？
4. **规则表放置与维护**：放 `report/oa_report_rules.json`，以后改规则改这个文件（不改代码）→ 认可？

（转发相关的"转发什么内容/形式"、"对应案件接口数据源"属**二期**待确认，本期不阻塞。）

---

## 六、实施步骤（一期）

1. 据 OA 三表 + §三/§四，生成 `oa_report_rules.json`，**先给用户核对规则表**（不接代码）。
2. `read_email.py` 加载规则 + `_resolve_oa_action()`；准备人常量补齐。
3. `dispatch_report`：OA 类型改走规则表——
   - `assign` → 建 report_tasks + 该准备人收链接（沿用现有分组发送）；
   - `skip` → 不建，`print("[规则] {案号} {类型} 应转发 {to}+cc{cc}（二期实现）")`；
   - `ignore` → 不建、不记录。
4. 保留 5开头 跳过、抄送 hailing.bi+dandan.cheng 等既有逻辑，纳入规则表统一表达。
5. 自测：dry-run 跑构造样例，逐格核对决策与日志。
6. commit + 部署（Windows：覆盖文件 → 删 `__pycache__` → 重启 bat）。

---

## 七、测试用例（一期）

| 输入(客户码/国别/类型/N) | 期望 |
|---|---|
| 20615 / CN / 审查意见 / N=1 | assign 胡梅 |
| 20615 / CN / 审查意见 / N=2 | skip（记录转发滴滴接口） |
| 20618 / US / CTNF | skip（记录转发 report+ui_pa），不建汇报信 |
| 其他客户 / US / CTNF | assign 王晶 |
| 其他客户 / US / NT.CR.APP.PA | ignore（补正类无需分配） |
| 20633 / EP / Summons | assign 王晶 |
| 20633 / EP / A.94(3) | skip |
| 20849 / CN / 驳回决定 | assign 任惠 |
| 其他客户 / CN / 驳回决定 | skip |
| 5开头 / 任意 CN OA | skip（记录转发李艳青+patents_pa） |

---

## 八、二期（转发接口邮箱）预告

- 定义"转发"具体动作（原邮件转发 / 新建带 PDF 邮件；发给谁 = 表中固定接口 + "对应案件接口"查库）。
- 接口人数据源（IPEasy 联系人？固定映射表？）。
- 把 §三规则里 `skip.forward` 从"仅日志"变为"真发转发邮件"。
- 覆盖 `US官文其他 / CN-其他官文 / PCT / 结项通知` 各表。
