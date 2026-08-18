#!/usr/bin/env python3
"""OA 分配 —— 立项时生成 AI 案件报告(markdown)。

数据源（本轮做前四大类：基础/权项/技术/审意；第五类人事+人员方案下一步接 DB 再补）：
  申请文件目录 DS/email_pipeline/申请文件/（按案号匹配文件名）：
    *SPEC*{案号}*.docx                → 说明书 → 三、技术方案速览
    *Preliminary Amendment*{案号}*.docx / *CLAIM*{案号}*.docx → 权利要求书 → 二、权利要求结构解析
  审意 PDF：立项邮件官文附件（运行时传入 oa_pdf_path）→ 四、审查意见深度解析
  基础信息：从立项 item / projects 取（一、案件基础信息）

复用现有 DeepSeek（deepseek-chat，同一把 key，见 filter_oa_email）。
build_case_report 只返回 markdown 正文，绝不抛异常（失败返回带说明的 markdown），
避免拖垮立项主流程。生成结果由调用方经 oa_assign_store.save_report 按 oa_id 落库。
"""
import os
import re
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
# 申请文件目录：scripts/oa/ 上两级即 DS/email_pipeline/，再进 申请文件/
DEFAULT_APP_DIR = os.path.normpath(os.path.join(_DIR, "..", "..", "申请文件"))

# 测试期开关：False → 不按案号匹配，任何案号都用目录里现有的那份 SPEC / Amendment 当测试文档；
# True → 按文件名含案号匹配（接真实 NAS/多案号时切回 True）。
MATCH_BY_CASE_NO = False


def _original_project(item):
    """取真实案号（测试前缀替换时 item 里存了原客户码，用它还原前 5 位）。"""
    project = (item.get("project", "") or "")
    orig = item.get("_orig_customer_code", "")
    if orig and len(project) >= 5:
        return orig + project[5:]
    return project


def find_application_files(project, base_dir=None):
    """在申请文件目录里按案号匹配说明书 / 权利要求书。返回 {'spec': path|None, 'claims': path|None}。"""
    base = base_dir or DEFAULT_APP_DIR
    out = {"spec": None, "claims": None}
    if not os.path.isdir(base):
        return out
    for fn in sorted(os.listdir(base)):
        if not fn.lower().endswith(".docx"):
            continue
        # 测试期：MATCH_BY_CASE_NO=False 时忽略案号，直接取目录里的 SPEC / Amendment 当测试文档
        if MATCH_BY_CASE_NO and (not project or project not in fn):
            continue
        low = fn.lower()
        path = os.path.join(base, fn)
        if "spec" in low and not out["spec"]:
            out["spec"] = path
        elif ("amendment" in low or "claim" in low) and not out["claims"]:
            out["claims"] = path
    return out


def _docx_text(path):
    """docx → 纯文本。优先 python-docx，失败退回裸解压 document.xml。"""
    if not path or not os.path.isfile(path):
        return ""
    try:
        import docx
        d = docx.Document(path)
        return "\n".join(p.text for p in d.paragraphs if p.text.strip())
    except Exception:
        try:
            import zipfile
            z = zipfile.ZipFile(path)
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml)).strip()
        except Exception as e:
            print(f"[oa_report_ai] docx 读取失败 {path}: {e}", file=sys.stderr)
            return ""


def _pdf_text(path_or_list, max_pages=8):
    """审意 PDF → 文本（复用 parse_us_pdf._pdf_to_text）。
    入参可为单个路径或路径列表（CN/EP 邮件可能带多份官文附件，逐份抽取拼接）。
    扫描件无文本时返回空串。"""
    paths = path_or_list if isinstance(path_or_list, (list, tuple)) else [path_or_list]
    out = []
    for path in paths:
        if not path or not os.path.isfile(path):
            continue
        try:
            from parse_us_pdf import _pdf_to_text
            text, _scanned = _pdf_to_text(path, max_pages=max_pages)
            if text and text.strip():
                out.append(text)
        except Exception as e:
            print(f"[oa_report_ai] PDF 读取失败 {path}: {e}", file=sys.stderr)
    return "\n\n".join(out)


def _deepseek_report(basic, claims_text, spec_text, oa_text):
    """把三份材料喂给 DeepSeek，产出前四大类的中文 markdown 报告。失败返回 None。"""
    from openai import OpenAI
    from filter_oa_email import _DEEPSEEK_API_KEY, _DEEPSEEK_BASE_URL, _DEEPSEEK_MODEL

    def _blk(title, text, limit):
        text = (text or "").strip()
        return f"\n【{title}】\n{text[:limit] if text else '（未提供 / 未获取到该材料）'}\n"

    basic_lines = "\n".join(f"- {k}：{v}" for k, v in basic.items() if v)
    prompt = (
        "你是资深专利 OA 任务分配分析官。请根据下面提供的案件材料，生成一份**中文 markdown** 案件分析报告，"
        "仅用于辅助分配 OA 答复任务。\n"
        "严格要求：\n"
        "1. 只输出以下【前四大类】，不要输出人员档案、人员安排建议等内容：\n"
        "   一、案件基础信息（案号/发明名称/当前法律状态/客户名称/官方答复期限；结合剩余天数给出高/中/低紧急程度与建议分配时间）\n"
        "   二、权利要求结构解析（权项总数；独立权利要求列编号+主题名称+数量；从属权利要求列编号+引用关系+数量；保护主题类型）\n"
        "   三、技术方案速览（技术领域；方案要点，用 50 字以内概括核心手段与所解决的技术问题）\n"
        "   四、审查意见深度解析（(1)实体问题清单，按 创造性A22.3/新颖性A22.2/不清楚A26.4/支持A26.4/形式问题(细则) 归类并注明涉及权项；"
        "(2)可授权性预判：直接可授权权项 / 间接或合并可授权权项 / 需重点答复的争议权项；(3)附图问题、摘要问题）\n"
        "2. **只依据材料，缺料的项写「资料缺失」，严禁编造**。审意材料为空时，第四大类整体标注「未获取到审查意见，待补」。\n"
        "3. 用二级标题（## 一、…）分节，条目用列表；简洁专业。\n"
        + _blk("案件基础信息", basic_lines, 2000)
        + _blk("权利要求书（用于第二大类）", claims_text, 12000)
        + _blk("说明书（用于第三大类）", spec_text, 8000)
        + _blk("审查意见通知书（用于第四大类）", oa_text, 12000)
    )
    try:
        client = OpenAI(api_key=_DEEPSEEK_API_KEY, base_url=_DEEPSEEK_BASE_URL)
        resp = client.chat.completions.create(
            model=_DEEPSEEK_MODEL,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"[oa_report_ai] DeepSeek 生成失败: {e}", file=sys.stderr)
        return None


def build_case_report(item, oa_pdf_path=None, app_dir=None, with_personnel=True, execute=None):
    """生成一件的 AI 案件报告（markdown 正文）。绝不抛异常。

    item: 立项/待分配基础信息（需 project/project_name/customer/region 等）。
    oa_pdf_path: 该件审意官文 PDF 路径（US 下载 / CN·EP 邮件附件）；空则第四大类标注待补。
    with_personnel: 是否追加第五类「内部人员档案」（查 atw 库；DB 不可达时该段标注、不影响前四大类）。
    execute: 人员档案查询用的注入 execute（默认走 db_query.execute）。
    返回: markdown 字符串（失败时也返回一段带说明的 markdown）。
    """
    project = _original_project(item)
    basic = {
        "案号": project,
        "发明名称": item.get("project_name", ""),
        "客户名称": item.get("customer", ""),
        "地区": item.get("region", ""),
        "当前法律状态": item.get("legal_status", ""),
        "官方答复期限": item.get("deadline", "") or item.get("project_deadline", ""),
    }
    files = find_application_files(project, base_dir=app_dir)
    claims_text = _docx_text(files.get("claims"))
    spec_text = _docx_text(files.get("spec"))
    oa_text = _pdf_text(oa_pdf_path)

    md = _deepseek_report(basic, claims_text, spec_text, oa_text)
    if not md:
        # DeepSeek 失败兜底：前四大类给最基础的可读 markdown，不留空
        lines = ["## 一、案件基础信息", ""]
        lines += [f"- {k}：{v or '资料缺失'}" for k, v in basic.items()]
        lines += ["", "> ⚠️ 前四大类 AI 生成失败（DeepSeek 不可达或材料不足），以上为基础信息占位。"]
        md = "\n".join(lines)

    # 追加第五类「内部人员档案」（查库拼装，非 AI；DB 不可达时该段自带说明）
    if with_personnel:
        try:
            from oa_personnel import build_personnel_md
            md = md.rstrip() + "\n\n" + build_personnel_md(project, execute=execute)
        except Exception as e:
            print(f"[oa_report_ai] 人员档案追加失败: {e}", file=sys.stderr)
    return md


if __name__ == "__main__":
    # 本地自测：python3 oa_report_ai.py <案号> [审意PDF]
    _proj = sys.argv[1] if len(sys.argv) > 1 else "20618-0424US00"
    _pdf = sys.argv[2] if len(sys.argv) > 2 else None
    _files = find_application_files(_proj)
    print("匹配到申请文件：", _files, file=sys.stderr)
    _out = build_case_report(
        {"project": _proj, "project_name": "(自测)", "customer": "联影", "region": "US"},
        oa_pdf_path=_pdf)
    print(_out)
