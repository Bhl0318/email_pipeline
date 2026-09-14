#!/usr/bin/env python3
"""立项时读审查意见全文 → DeepSeek 判是否涉及新颖性/创造性。

用途：OA 立项时判断该案审意是否涉及新颖性(US §102 / EPC Art.54)或创造性(US §103 / EPC Art.56)。
命中任一 → 该案在「新增OA」页「其它备注事项」列标注、且不进 OA 分配（不进待分配、不发分配链接）。

提示词硬编码（见 _PROMPT，用户原文）；末尾额外要求输出一行 JSON 结论供程序判定。
绝不抛异常：审意为空 / DeepSeek 失败 → 返回 novelty=inventiveness=False（默认「无问题」，
不误跳过分配——宁可多分一件，不可漏分一件）。

  from analyze_oa_issue import analyze_novelty_inventiveness
  v = analyze_novelty_inventiveness(oa_text)
  # v = {"novelty": bool, "inventiveness": bool, "note": "一句话结论", "analysis": "完整分析"}
"""
import os
import sys
import re
import json

from openai import OpenAI

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "REDACTED_API_KEY")
DEEPSEEK_MODEL = "deepseek-chat"

# 审意全文截断上限（deepseek-chat 上下文足够；审意正文一般远小于此，扫描 OCR 偶有超长冗余）
_MAX_CHARS = 20000

# 用户原始提示词（硬编码，勿改措辞）
_PROMPT = """提示词：专利审查意见文档分析
角色
你是一位专利审查文档分析专家，熟悉USPTO和EPO的审查意见格式、法条体系及对比文件引用规则。

任务
分析用户提供的专利审查意见文档，输出以下内容：

文档类型识别：判断该文档属于哪一类（如：美国非最终驳回、美国最终驳回、EPO Art.94(3)审查意见、EPO补充检索报告、EPO检索意见等）。

法条适用分析：

美国体系：是否涉及 35 U.S.C. § 102（新颖性）和/或 § 103（创造性/显而易见性）。

欧洲体系：是否涉及 EPC Art. 54（新颖性）、Art. 56（创造性）、Art. 82（单一性）、Art. 83（充分公开）等。

明确说明每项法条是否被引用、针对哪些权利要求、驳回理由是什么。

对比文件识别：

列出文档中引用的所有对比文件（专利文献和非专利文献）。

对每篇对比文件，注明：简称、公开号/出处、引用目的（如：最接近现有技术、结合用于创造性论证等）。

明确说明：该文档本身是否附有对比文件全文（通常USPTO/EPO的审查意见只引用、不附全文）。

核心争议点总结：

审查员与申请人的主要分歧点。

审查员对申请人论点的回应（如有）。

驳回逻辑链（单篇公开 vs. 多篇组合 vs. 常规优化等）。

应对策略建议：

针对新颖性驳回：建议修改权利要求或论证区别特征。

针对创造性驳回：建议论证非显而易见性、意想不到的技术效果、技术问题的重新定义等。

针对其他缺陷（单一性、公开不充分、附图缺陷等）：给出相应处理建议。

输出格式要求：

以表格形式对比各法条的涉及情况。

以清单形式列出对比文件。

以结构化段落呈现分析和建议。

语言简洁、专业，避免冗余。"""

# 追加：要求末尾单独一行机器可读结论，供程序据此标注备注 + 决定是否分配
_VERDICT_INSTR = (
    "\n\n【额外要求】完成上述分析后，务必在最末尾单独另起一行输出如下 JSON（供程序判定，不要放进代码块、"
    "不要额外解释）：\n"
    '{"novelty": true/false, "inventiveness": true/false, "note": "一句话结论"}\n'
    "其中 novelty = 该审意是否以新颖性（US §102 / EPC Art.54）为由驳回/指出；"
    "inventiveness = 是否以创造性/显而易见性（US §103 / EPC Art.56）为由驳回/指出；"
    "note 用一句话概括（如「涉及新颖性、创造性」「仅形式缺陷，不涉及新颖性/创造性」）。"
)

# 从整段回复里取最后一个含 "novelty" 的扁平 JSON 对象
_VERDICT_RE = re.compile(r'\{[^{}]*"novelty"[^{}]*\}', re.DOTALL)


def _empty(note=""):
    return {"novelty": False, "inventiveness": False, "note": note, "analysis": ""}


def analyze_novelty_inventiveness(oa_text):
    """审意全文 → DeepSeek 分析，返回 {novelty, inventiveness, note, analysis}。
    审意为空 / 调用失败 → 全 False（默认无问题，不误跳过分配）。"""
    oa_text = (oa_text or "").strip()
    if not oa_text:
        return _empty()
    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        prompt = _PROMPT + _VERDICT_INSTR + "\n\n【审查意见全文】\n" + oa_text[:_MAX_CHARS]
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL, max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        content = (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"[审意分析] DeepSeek 调用失败: {e}", file=sys.stderr)
        return _empty()
    # 取最后一个含 novelty 的 JSON（分析正文里也可能出现 { }，故取末尾那个结论）
    matches = list(_VERDICT_RE.finditer(content))
    verdict = {}
    if matches:
        try:
            verdict = json.loads(matches[-1].group())
        except Exception:
            verdict = {}
    if not matches:
        print("[审意分析] 未从回复中解析到结论 JSON，按无问题处理", file=sys.stderr)
    return {
        "novelty": bool(verdict.get("novelty")),
        "inventiveness": bool(verdict.get("inventiveness")),
        "note": (verdict.get("note") or "").strip(),
        "analysis": content,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 analyze_oa_issue.py <审意文本文件>")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        _txt = f.read()
    r = analyze_novelty_inventiveness(_txt)
    print(json.dumps({k: r[k] for k in ("novelty", "inventiveness", "note")},
                     ensure_ascii=False, indent=2))
    print("\n--- 分析全文 ---\n" + r["analysis"])
