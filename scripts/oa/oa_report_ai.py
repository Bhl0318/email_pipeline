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

# 测试期开关：False → 读扁平测试目录 DEFAULT_APP_DIR（任意案号取现有样例）；
# True → 走真实 NAS（Z:\）按案号+客户+地区定位（见 _resolve_app_dir）。
# 上线：report_server 所在机器需能挂 Z 盘 + 连 atw，置 True 走真实 NAS。
MATCH_BY_CASE_NO = True

# 申请文件 NAS 根（生产，仅能挂到 Z 盘的机器可读）
NAS_BASE_DIR = "Z:\\"                       # 普通案号：Z:\{码}-{简称}\{组内号}\{案号}\*递交文件*\
NAS_ZHUOHUI_DIR = "Z:\\众慧优创知识产权"      # 含 -H 案号：\{名字含码的目录}\{案号}\*递交文件*\
NAS_TOPLEVEL_CUSTOMERS = {"20608", "20615", "20618", "20633", "20735", "20849"}
# 各地区在「递交文件」目录里挑说明书文件的文件名关键词（取最新 .docx；EP 无关键词=取最新 .docx）
APP_FILE_KEYWORDS = {"US": ["spec"], "CN": ["说明书", "申请文件"], "EP": None}


def _original_project(item):
    """取真实案号（测试前缀替换时 item 里存了原客户码，用它还原前 5 位）。"""
    project = (item.get("project", "") or "")
    orig = item.get("_orig_customer_code", "")
    if orig and len(project) >= 5:
        return orig + project[5:]
    return project


def _customer_shortname(code):
    """atw customer 表：案号前5位 → 客户简称。查不到/连不上返回空串。"""
    code = (code or "")[:5]
    if not code:
        return ""
    try:
        from db_query import execute
        rows = execute(f"SELECT customer_shortname FROM customer WHERE customer_code = '{code.replace(chr(39), chr(92)+chr(39))}'")
        if rows and rows[0].get("customer_shortname"):
            return rows[0]["customer_shortname"]
    except Exception as e:
        print(f"[oa_report_ai] 查客户简称失败 {code}: {e}", file=sys.stderr)
    return ""


def _resolve_app_dir(project, region):
    """定位申请文件所在目录（NAS，生产）。找不到返回 None。
      含 -H： Z:\\众慧优创知识产权\\{名字含 project[:5] 的目录}\\{案号}\\*递交文件*\\
      普通：  Z:\\{码}-{简称}\\{组内号}\\{案号}\\*递交文件*\\   （EP 再进一层 *新申请*\\；
              列出客户在根，其余在 其他客户\\ 下）"""
    import glob
    if not project or len(project) < 10:
        return None
    if "-H" in project:
        parents = sorted(glob.glob(os.path.join(NAS_ZHUOHUI_DIR, f"*{project[:5]}*")))
        for parent in parents:
            case_dir = os.path.join(parent, project)
            if os.path.isdir(case_dir):
                submit = sorted(glob.glob(os.path.join(case_dir, "*递交文件*")))
                if submit:
                    return submit[0]
        return None
    # 普通案号
    code, zu = project[:5], project[:10]
    shortname = _customer_shortname(code)
    if not shortname:
        return None
    cust_dir = f"{code}-{shortname}"
    root = os.path.join(NAS_BASE_DIR, cust_dir) if code in NAS_TOPLEVEL_CUSTOMERS \
        else os.path.join(NAS_BASE_DIR, "其他客户", cust_dir)
    submit = sorted(glob.glob(os.path.join(root, zu, project, "*递交文件*")))
    if not submit:
        return None
    d = submit[0]
    if region == "EP":
        xin = sorted(glob.glob(os.path.join(d, "*新申请*")))
        return xin[0] if xin else None
    return d


def _pick_latest_docx(dirpath, keywords=None):
    """dir 下 .docx，(可选)文件名含任一关键词(大小写不敏感)，按 mtime 取最新。返回路径或 None。
    先在本层找；本层无匹配时，再递归子目录找。"""
    import glob
    if not dirpath or not os.path.isdir(dirpath):
        return None
    kws = [k.lower() for k in keywords] if keywords else None

    def _match(pattern):
        fs = [f for f in glob.glob(pattern, recursive=True)
              if os.path.isfile(f) and f.lower().endswith(".docx")]
        if kws:
            fs = [f for f in fs if any(k in os.path.basename(f).lower() for k in kws)]
        return fs

    files = _match(os.path.join(dirpath, "*.docx"))
    if not files:                                            # 本层没有 → 递归子目录
        files = _match(os.path.join(dirpath, "**", "*.docx"))
    if not files:
        return None
    return max(set(files), key=os.path.getmtime)


def find_application_files(project, region="", base_dir=None):
    """定位说明书文件。返回 {'spec': path|None}（权要由 _split_spec 从中切出）。
    测试期(MATCH_BY_CASE_NO=False)：读扁平 DEFAULT_APP_DIR 里含 spec 的 docx；
    生产(True)：走 NAS，按地区在「递交文件」目录取最新 .docx（US 含 spec / CN 含 说明书|申请文件 / EP 最新）。"""
    out = {"spec": None}
    if not MATCH_BY_CASE_NO:
        base = base_dir or DEFAULT_APP_DIR
        if os.path.isdir(base):
            for fn in sorted(os.listdir(base)):
                if fn.lower().endswith(".docx") and "spec" in fn.lower():
                    out["spec"] = os.path.join(base, fn)
                    break
        return out
    # 生产：NAS
    d = _resolve_app_dir(project, region)
    if d:
        out["spec"] = _pick_latest_docx(d, APP_FILE_KEYWORDS.get(region))
    return out


# 官文统一目录：US 下载件本就落这里(us_deadline.DOWNLOAD_DIR)；CN/EP 邮件附件也复制进来，
# 使各地区官文都在 attachment/{案号}/ 下，OA 分配按案号直接读。
ATTACHMENT_DIR = os.path.normpath(os.path.join(_DIR, "..", "..", "attachment"))


def case_docs_dir(project):
    return os.path.join(ATTACHMENT_DIR, project) if project else None


def persist_email_official_docs(project, src_paths):
    """把 CN/EP 邮件官文附件(_inbox)复制到 attachment/{案号}/，与 US 下载件同目录。
    已在目标目录内的文件跳过。返回复制数量。绝不抛。"""
    dest_dir = case_docs_dir(project)
    if not dest_dir:
        return 0
    paths = src_paths if isinstance(src_paths, (list, tuple)) else [src_paths]
    cnt = 0
    try:
        import shutil
        for src in paths:
            if not src or not os.path.isfile(src):
                continue
            if os.path.normpath(os.path.dirname(src)) == os.path.normpath(dest_dir):
                continue  # 已在目标目录
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copyfile(src, os.path.join(dest_dir, os.path.basename(src)))
            cnt += 1
    except Exception as e:
        print(f"[oa_report_ai] 官文复制到 attachment 失败 {project}: {e}", file=sys.stderr)
    return cnt


def find_case_official_pdfs(project):
    """读 attachment/{案号}/ 下的官文 PDF（顶层，跳过 _stamped 盖章副本子目录）。返回路径列表。"""
    d = case_docs_dir(project)
    if not d or not os.path.isdir(d):
        return []
    import glob
    hits = glob.glob(os.path.join(d, "*.pdf")) + glob.glob(os.path.join(d, "*.PDF"))
    return sorted(set(hits))


# 邮件官文附件暂存目录（report 读取层 _save_pdf_attachments_to_inbox 落这里，按 message_id 分子目录）
INBOX_DIR = os.path.normpath(os.path.join(_DIR, "..", "output", "_inbox"))


def find_inbox_official_pdfs(project):
    """兜底：attachment/{案号}/ 没有官文时，去 _inbox 里按「文件名含案号」找。返回路径列表。
    _inbox 按 message_id 分子目录，故只能靠附件文件名含案号来匹配该案。"""
    if not project or not os.path.isdir(INBOX_DIR):
        return []
    import glob
    hits = [f for f in glob.glob(os.path.join(INBOX_DIR, "*", "*.pdf")) + glob.glob(os.path.join(INBOX_DIR, "*", "*.PDF"))
            if project in os.path.basename(f)]
    return sorted(set(hits))


def find_oa_pdf(project, base_dir=None):
    """在申请文件目录里找审查意见 PDF（.pdf）。测试期(MATCH_BY_CASE_NO=False)取目录里任一 PDF；
    案号匹配期取文件名含案号的 PDF。找不到返回 None。"""
    base = base_dir or DEFAULT_APP_DIR
    if not os.path.isdir(base):
        return None
    for fn in sorted(os.listdir(base)):
        if not fn.lower().endswith(".pdf"):
            continue
        if MATCH_BY_CASE_NO and (not project or project not in fn):
            continue
        return os.path.join(base, fn)
    return None


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


_CLAIMS_START_RE = re.compile(r"(WHAT\s+IS\s+CLAIMED\s+IS|^\s*CLAIMS\s*$|We\s+claim|I\s+claim|权\s*利\s*要\s*求\s*书?)",
                              re.IGNORECASE | re.MULTILINE)
_CLAIMS_END_RE = re.compile(r"(^\s*ABSTRACT\s*$|说\s*明\s*书\s*摘\s*要|^\s*摘\s*要\s*$)",
                            re.IGNORECASE | re.MULTILINE)


def _split_spec(spec_text):
    """把说明书全文切成 (说明部分, 权利要求部分)。
    权要以「WHAT IS CLAIMED IS / CLAIMS / 权利要求」起，到「ABSTRACT / 摘要」止。
    切不出权要时 claims 返回空串、description 返回全文。"""
    text = spec_text or ""
    ms = _CLAIMS_START_RE.search(text)
    if not ms:
        return text, ""
    desc = text[:ms.start()].strip()
    rest = text[ms.start():]
    me = _CLAIMS_END_RE.search(rest, 1)     # 从权要标题之后再找摘要，避免匹配到标题自身
    claims = (rest[:me.start()] if me else rest).strip()
    return desc, claims


def _ocr_pdf(path, max_pages=6):
    """扫描件（无文本层）→ 用 qwen-vl 逐页 OCR 成纯文本。失败返回空串。"""
    try:
        import base64
        import fitz
        from openai import OpenAI
        from parse_us_pdf import QWEN_API_KEY, QWEN_BASE_URL, QWEN_VL_MODEL
    except Exception as e:
        print(f"[oa_report_ai] OCR 依赖缺失: {e}", file=sys.stderr)
        return ""
    try:
        doc = fitz.open(path)
        content = [{"type": "text", "text":
                    "这些是专利审查意见通知书/官方文件的扫描页。请逐字识别其中全部文字，"
                    "按阅读顺序输出为纯文本，保留条目/编号；不要总结、不要翻译、不要加任何解释。"}]
        for i in range(min(max_pages, len(doc))):
            pix = doc[i].get_pixmap(dpi=150)
            b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
        doc.close()
        client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
        resp = client.chat.completions.create(
            model=QWEN_VL_MODEL, max_tokens=4000,
            messages=[{"role": "user", "content": content}])
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"[oa_report_ai] qwen-vl OCR 失败 {path}: {e}", file=sys.stderr)
        return ""


def _pdf_text(path_or_list, max_pages=8):
    """审意 PDF → 文本。先用文本层（parse_us_pdf._pdf_to_text）；扫描件无文本层则 qwen-vl OCR 兜底。
    入参可为单个路径或路径列表（CN/EP 邮件可能带多份官文附件，逐份抽取拼接）。"""
    paths = path_or_list if isinstance(path_or_list, (list, tuple)) else [path_or_list]
    out = []
    for path in paths:
        if not path or not os.path.isfile(path):
            continue
        try:
            from parse_us_pdf import _pdf_to_text
            text, scanned = _pdf_to_text(path, max_pages=max_pages)
            if text and text.strip():
                out.append(text)
            else:  # 扫描件（无文本层）→ OCR
                print(f"[oa_report_ai] {os.path.basename(path)} 无文本层，转 qwen-vl OCR", file=sys.stderr)
                ocr = _ocr_pdf(path, max_pages=min(max_pages, 6))
                if ocr:
                    out.append(ocr)
        except Exception as e:
            print(f"[oa_report_ai] PDF 读取失败 {path}: {e}", file=sys.stderr)
    return "\n\n".join(out)


# 报告生成默认指令（外部编辑系统未配置时回退，= 原硬编码，行为不变）。材料由代码在其后追加。
DEFAULT_REPORT_INSTRUCTION = (
    "你是资深专利 OA 任务分配分析官。请根据下面提供的案件材料，生成一份**中文 markdown** 案件分析报告，"
    "仅用于辅助分配 OA 答复任务。\n"
    "【申请文件】是一篇专利申请文件全文，**其中同时包含说明书与权利要求书**——权利要求通常以"
    "“WHAT IS CLAIMED IS / We claim / I claim / 权利要求”起头。请你**自行从中识别**权利要求部分与说明书部分，"
    "分别用于第二、第三大类。\n"
    "严格要求：\n"
    "1. 先输出以下【前四大类】，不要输出人员档案、人员安排建议：\n"
    "   一、案件基础信息（案号/发明名称/当前法律状态/客户名称/官方答复期限；结合剩余天数给出高/中/低紧急程度与建议分配时间）\n"
    "   二、权利要求结构解析（权项总数；独立权利要求列编号+主题名称+数量；从属权利要求列编号+引用关系+数量；保护主题类型）\n"
    "   三、技术方案速览（技术领域；方案要点，用 50 字以内概括核心手段与所解决的技术问题）\n"
    "   四、审查意见深度解析（(1)实体问题清单，按 创造性A22.3/新颖性A22.2/不清楚A26.4/支持A26.4/形式问题(细则) 归类并注明涉及权项；"
    "(2)可授权性预判：直接可授权权项 / 间接或合并可授权权项 / 需重点答复的争议权项；(3)附图问题、摘要问题）\n"
    "2. 前四大类之后，**另起一行原样输出一行标记 `===预估工作量===`**，再输出「预估工作量」：给出预估答复工时"
    "（按小时，可给区间，如 8~12 小时）并简要说明依据（结合权项数量与复杂度、审查意见问题的数量与类型、OA 轮次等）。"
    "这部分只写工时与依据的列表条目，**不要再加二级标题**。审意缺失时按权项与申请文件复杂度给区间并注明依据不足。\n"
    "3. **只依据材料，缺料的项写「资料缺失」，严禁编造**。审意材料为空时，第四大类整体标注「未获取到审查意见，待补」。\n"
    "4. 用二级标题（## 一、…）分节，条目用列表；简洁专业。"
)


def _report_instruction():
    """报告生成指令：优先读外部编辑系统写入的 zxassist_result_instruction(mtype='oaInstruct') 的 instruction；
    读不到/为空/DB 异常回退 DEFAULT_REPORT_INSTRUCTION（重新生成时即用最新编辑的指令）。"""
    try:
        from db_query import execute
        rows = execute("SELECT instruction FROM zxassist_result_instruction WHERE mtype = 'oaInstruct'")
        if rows and (rows[0].get("instruction") or "").strip():
            return rows[0]["instruction"]
    except Exception as e:
        print(f"[oa_report_ai] 读外部指令失败，用默认: {e}", file=sys.stderr)
    return DEFAULT_REPORT_INSTRUCTION


def _deepseek_report(basic, application_text, oa_text):
    """把申请文件全文(含说明书+权利要求)与审意材料喂给 DeepSeek，由其自行识别权要/说明，
    产出前四大类的中文 markdown 报告。失败返回 None。指令取自 _report_instruction()。"""
    from openai import OpenAI
    from filter_oa_email import _DEEPSEEK_API_KEY, _DEEPSEEK_BASE_URL, _DEEPSEEK_MODEL

    def _blk(title, text, limit):
        text = (text or "").strip()
        return f"\n【{title}】\n{text[:limit] if text else '（未提供 / 未获取到该材料）'}\n"

    basic_lines = "\n".join(f"- {k}：{v}" for k, v in basic.items() if v)
    prompt = (
        _report_instruction().rstrip() + "\n"
        + _blk("案件基础信息", basic_lines, 2000)
        + _blk("申请文件全文（含说明书与权利要求，请自行识别）", application_text, 130000)
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
    files = find_application_files(project, region=item.get("region", ""), base_dir=app_dir)
    spec_full = _docx_text(files.get("spec"))
    # 申请文件全文直接交给 DeepSeek 自行识别权要/说明；仅当超大(超上下文风险)才切分保头尾权要。
    APP_CAP = 120000
    if len(spec_full) <= APP_CAP:
        application_text = spec_full
    else:
        desc_text, claims_text = _split_spec(spec_full)
        application_text = ((desc_text[:70000] + "\n\n……（说明书中段略）……\n\n" + claims_text)
                            if claims_text else spec_full[:APP_CAP])
        print(f"[oa_report_ai] 申请文件超 {APP_CAP} 字，已切分保头尾权要", file=sys.stderr)
    # 审意 PDF：未显式传入时，① attachment/{案号}/（US 下载件/CN·EP 已复制进来）→
    # ② _inbox 里文件名含案号的附件（兜底，attachment 缺件时）→ ③ 申请文件目录（测试期）。扫描件走 OCR。
    if not oa_pdf_path:
        oa_pdf_path = find_case_official_pdfs(project)
        if oa_pdf_path:
            print(f"[oa_report_ai] 审意 PDF 按案号取自 attachment/{project}/：{len(oa_pdf_path)} 份", file=sys.stderr)
        else:
            oa_pdf_path = find_inbox_official_pdfs(project)
            if oa_pdf_path:
                print(f"[oa_report_ai] 审意 PDF attachment 无，回退 _inbox 按案号：{len(oa_pdf_path)} 份", file=sys.stderr)
            else:
                oa_pdf_path = find_oa_pdf(project, base_dir=app_dir)
                if oa_pdf_path:
                    print(f"[oa_report_ai] 审意 PDF 回退申请文件目录：{os.path.basename(oa_pdf_path)}", file=sys.stderr)
    oa_text = _pdf_text(oa_pdf_path)

    md = _deepseek_report(basic, application_text, oa_text)
    workload_md = ""
    if md:
        # 拆出 DeepSeek 附带的「预估工作量」(标记后的内容)，放到第六节
        main_md, sep, tail = md.partition("===预估工作量===")
        md = main_md.rstrip()
        workload_md = tail.strip()
    else:
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

    # 第六节：预估工作量（附加分配辅助信息，AI 依据报告内容判断）
    if workload_md:
        md = md.rstrip() + "\n\n## 六、预估工作量（附加分配辅助信息）\n\n" + workload_md
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
