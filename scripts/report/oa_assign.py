#!/usr/bin/env python3
"""OA 分配工具 —— 后端路由（并入汇报信服务 report_server）。

在 report_server.py 里 `app.include_router(oa_assign.router)` 挂载，页面走 /static/assign.html。

接口（与 web/assign.html 约定一致）：
  GET  /api/cases/pending            待分配案件列表(摘要)——读 oa_assign_task JOIN projects
  POST /api/assignment/analyze       {caseId} → 该案 AI 报告(reportMd)+分配建议(schemes)——读 oa_assign_report
  GET  /api/staff/list?q=&role=      人员库(下拉搜索)——查真实 users(status<>'离职')，支持 q 搜索
  POST /api/assignment/submit        单案提交——回写 Wiki 人员分配 + projects + 待分配表置已分配
  POST /api/assignment/submit/batch  批量提交（同上，逐案）

数据现状：案件列表/AI 报告已走真实库；仅人员下拉(staff)仍为桩，待接 DB 历史承办。
"""
import json
import os
import re
import sys
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse

_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(tags=["oa-assign"])


def _log(*a):
    print(f"[{datetime.now():%H:%M:%S}][oa-assign]", *a, file=sys.stderr, flush=True)


def _write_back(case_id, responder, qc, postscript="", custom_note="", aqc=""):
    """按 case_id(=oa_id) 回写 Wiki 新增OA 人员分配格（负责人/QC/AQC 分开标；+分配人历史页）。
    best-effort：桩数据/无 Wiki 时返回失败也不抛。"""
    try:
        oa_dir = os.path.join(_DIR, "..", "oa")
        if oa_dir not in sys.path:
            sys.path.insert(0, oa_dir)
        from oainfo_cli import write_oa_assignment
        return write_oa_assignment(case_id, responder, qc,
                                   postscript=postscript, custom_note=custom_note, aqc=aqc)
    except Exception as e:
        return {"code": 1, "msg": f"回写调用失败: {e}"}


def _write_back_batch(assignments):
    """批量回写 Wiki 新增OA页（一次取页一次存页）+ 分配人历史页（按页合并）。返回 {caseId: {code,msg}}。"""
    try:
        oa_dir = os.path.join(_DIR, "..", "oa")
        if oa_dir not in sys.path:
            sys.path.insert(0, oa_dir)
        from oainfo_cli import write_oa_assignments_batch
        items = [{"oa_id": a.get("caseId"), "responder": a.get("responder"),
                  "qc": a.get("qc"), "aqc": a.get("aqc", ""),   # Wiki 里 QC/AQC 分开标
                  "project": a.get("caseNo", ""),          # 案号用于双重比对（前端 _assignmentOf 已带）
                  "postscript": a.get("postscript", ""), "custom_note": a.get("customNote", "")}
                 for a in assignments]
        return write_oa_assignments_batch(items)
    except Exception as e:
        return {a.get("caseId"): {"code": 1, "msg": f"批量回写调用失败: {e}"} for a in assignments}


def _mark(case_id, responder, qc):
    """待分配表回填分配结果并置已分配 + 写 tip_budgetperformance_role。best-effort，不抛。"""
    st = _store()
    if st is None or not case_id:
        return
    try:
        st.mark_submitted(case_id, responder or "", qc or "")
    except Exception as e:
        _log("待分配表回填失败：", e)
    try:
        st.write_perf_roles(case_id, responder or "", qc or "")   # 答复负责人/QC → tip_budgetperformance_role
    except Exception as e:
        _log("写 tip_budgetperformance_role 失败：", e)


def _invalid_names(*names):
    """返回给定人名里不在 users.username_zn 的名字列表；DB 不可用则不拦（返回 []）。"""
    st = _store()
    if st is None:
        return []
    bad = []
    for n in names:
        n = (n or "").strip()
        if n and not st.user_exists(n):
            bad.append(n)
    return bad


def _combine_qc(qc, aqc):
    """QC 与 AQC 用「,」拼接写库/Wiki（AQC 只自定义方案有）。缺哪个省哪个。"""
    qc = (qc or "").strip()
    aqc = (aqc or "").strip()
    return f"{qc},{aqc}" if (qc and aqc) else (qc or aqc)


def _save_submission(body):
    """把提交的分配结果+附言(附言 postscript / 原因 customNote)存入 oa_assign_report.submit_json。best-effort。"""
    st = _store()
    cid = body.get("caseId")
    if st is None or not cid:
        return
    try:
        st.save_submission(cid, {
            "scheme_id": body.get("schemeId", "") or "",
            "responder": body.get("responder", "") or "",
            "qc": body.get("qc", "") or "",
            "aqc": body.get("aqc", "") or "",                  # AQC（供分享页展示）
            "postscript": body.get("postscript", "") or "",   # 分配附言
            "reason": body.get("customNote", "") or "",        # 分配原因
            "submitted_at": f"{datetime.now():%Y-%m-%d %H:%M}",
        })
    except Exception as e:
        _log("保存提交结果(submit_json)失败：", e)


def _store():
    """取待分配库(oa 侧)模块；不可用返回 None，调用方回退桩数据。"""
    try:
        oa_dir = os.path.join(_DIR, "..", "oa")
        if oa_dir not in sys.path:
            sys.path.insert(0, oa_dir)
        import oa_assign_store
        return oa_assign_store
    except Exception as e:
        _log("待分配库不可用：", e)
        return None


_CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
           "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def _oa_seq_of(name):
    """从立项名解析 OA 次数：US/EP「OA{数字}-…」→数字；CN「第N次…」→N；取不到返回 0。"""
    name = name or ""
    m = re.search(r'OA(\d+)', name)
    if m:
        return int(m.group(1))
    m = re.search(r'第([一二三四五六七八九十]+)次', name)
    if m:
        cn = m.group(1)
        if cn == "十":
            return 10
        if "十" in cn:
            l, _, rr = cn.partition("十")
            return (_CN_NUM.get(l, 1) if l else 1) * 10 + (_CN_NUM.get(rr, 0) if rr else 0)
        return _CN_NUM.get(cn, 0)
    return 0


def _row_to_summary(r):
    """待分配表行 → 前端摘要。"""
    return {
        "id": r.get("id", ""),
        "caseNo": r.get("case_volume", ""),
        "name": r.get("project_name", ""),
        "oaSeq": _oa_seq_of(r.get("project_name", "")),   # OA 次数（0=无/非答复类）
        "client": r.get("customer", ""),
        "region": r.get("region", ""),
        "legalStatus": "",
        "urgency": "",
        "daysLeft": None,
        "estimate": "",
        "deadline": r.get("project_deadline", ""),
        "submitted": bool(r.get("submitted")),
        "statusCode": int(r.get("submitted") or 0),       # 原始状态 0待分配/1已分配/2无需处理
        "linkSentAt": str(r.get("link_sent_at") or ""),   # 立项/发分配链接时刻(要求分配的时间)
        "files": [],
    }


# 真实待分配案件暂无 AI 报告：给结构完整的占位报告(前端不崩) + 仅"自定义方案"供人工选人
_CUSTOM_SCHEME = {"id": "custom", "label": "自定义方案", "note": "", "responder": "", "qc": ""}
_SKIP_SCHEME = {"id": "skip", "label": "无需处理", "responder": "", "qc": "",
                "note": "标记此案不需人员分配；提交时从待分配列表移除，不写人员/Wiki/绩效表。"}


def _placeholder_md(summary):
    """报告库暂无该案报告时的占位 markdown（立项报告未生成/失败时兜底）。"""
    return (
        "## 一、案件基础信息\n\n"
        f"- 案号：{summary.get('caseNo','') or '—'}\n"
        f"- 发明名称：{summary.get('name','') or '—'}\n"
        f"- 客户名称：{summary.get('client','') or '—'}\n"
        f"- 官方答复期限：{summary.get('deadline','') or '—'}\n\n"
        "> ⚠️ 该案 AI 报告尚未生成（立项时未生成或生成失败）。"
    )


def _placeholder_detail(summary):
    return {
        "basicInfo": {"caseNo": summary.get("caseNo", ""), "name": summary.get("name", ""),
                      "legalStatus": summary.get("legalStatus", ""), "client": summary.get("client", "")},
        "claimsInfo": {"total": 0, "independent": [], "dependentGroups": [], "protectionTypes": []},
        "techInfo": {"field": "", "summary": "（AI 案件报告待接入，当前为占位）"},
        "oaInfo": {"substantiveIssues": [],
                   "patentability": {"directGrantable": [], "indirectGrantable": [], "keyDispute": []},
                   "otherIssues": []},
        "personnelInfo": {"currentCase": {"writer": "", "qc": "", "oaHistory": []},
                          "relatedCase": {"caseNo": "", "writer": "", "qc": "", "oaHistory": []}},
    }


@router.get("/api/cases/pending")
def cases_pending(page: int = 1, pageSize: int = 100, assignee: str = ""):
    # 读真实待分配表（oa_assign_task JOIN projects）。assignee 非空则只留分配给该人的案件。
    st = _store()
    if st is None:
        return {"total": 0, "items": [], "error": "待分配库模块不可用"}
    try:
        rows = st.list_pending()
        if assignee:
            rows = [r for r in rows if _assignee_of(r) == assignee]
        items = [_row_to_summary(r) for r in rows]
        _log(f"GET  /api/cases/pending assignee={assignee or '(全部)'} → {len(items)} 件")
        return {"total": len(items), "items": items, "assignee": assignee}
    except Exception as e:
        _log("读待分配表失败：", e)
        return {"total": 0, "items": [], "error": f"读待分配表失败: {e}"}


def _assignee_of(row):
    """该案分配人姓名（=收到分配链接的人，按案号+OA类别路由，与发信同源）。取不到返回 ""。"""
    try:
        oa_dir = os.path.join(_DIR, "..", "oa")
        if oa_dir not in sys.path:
            sys.path.insert(0, oa_dir)
        from forward_oa import assign_person_name
        return assign_person_name(row.get("case_volume", ""), row.get("project_name", ""))
    except Exception:
        return ""


def _derive_region(project):
    """从案号推地区（20618-0424US00 → US）。取不到返回空串。"""
    p = (project or "").upper()
    for r in ("US", "EP", "CN", "WO", "JP", "KR"):
        if r in p:
            return r
    return ""


def _row_to_item(row):
    """待分配行 → build_case_report 需要的 item（基础信息）。"""
    proj = row.get("case_volume", "") or ""
    return {
        "project": proj,
        "project_name": row.get("project_name", ""),
        "customer": row.get("customer", ""),
        "region": _derive_region(proj),
        "deadline": row.get("project_deadline", ""),
    }


def _generate_report(cid, row):
    """现场生成 AI 报告并落库（阻塞：读文档 + DeepSeek）。返回 (report_md, schemes)。
    审意 PDF 在分配页这一刻不在手边（邮件已归档），第四大类会标待补，
    待后续在立项时按 oa_id 持久化审意 PDF 再补。"""
    oa_dir = os.path.join(_DIR, "..", "oa")
    if oa_dir not in sys.path:
        sys.path.insert(0, oa_dir)
    from oa_report_ai import build_case_report
    item = _row_to_item(row)
    # 审意 PDF 不显式传：build_case_report 会按案号读 attachment/{案号}/（生产），
    # 取不到再回退申请文件目录（测试期）。
    md = build_case_report(item, oa_pdf_path=None)
    # 先生成真实人员安排方案（白名单+负荷），再把方案渲染成「六、本次OA人员安排建议」追加进报告
    schemes = []
    try:
        from oa_schemes import build_assignment_schemes, render_schemes_md
        schemes = build_assignment_schemes(item.get("project", ""), region=item.get("region", ""), report_md=md)
        sec = render_schemes_md(schemes)
        if sec:
            md = md.rstrip() + "\n\n" + sec
    except Exception as e:
        _log("方案生成失败：", e)
    try:
        st = _store()
        if st is not None:
            st.save_report(cid, md, schemes)
    except Exception as e:
        _log("生成后落库失败：", e)
    return md, schemes


@router.post("/api/assignment/analyze")
async def assignment_analyze(req: Request):
    from starlette.concurrency import run_in_threadpool
    body = await req.json()
    cid = body.get("caseId")
    force = bool(body.get("force"))        # 「重新生成」按钮传 true：无视缓存强制重出
    st = _store()
    row = None
    if st is not None:
        try:
            row = next((r for r in st.list_pending() if r.get("id") == cid), None)
        except Exception as e:
            _log("analyze 读待分配表失败：", e)
    if not row:
        _log(f"POST /api/assignment/analyze caseId={cid} → 未找到")
        return JSONResponse({"error": f"案件不存在: {cid}"}, status_code=404)

    summary = _row_to_summary(row)
    report_md, schemes, source = "", [], ""
    # 非强制时先读缓存（oa_assign_report）
    if not force:
        try:
            rep = st.get_report(cid) if st is not None else None
            if rep and (rep.get("report_md") or "").strip():
                report_md = rep.get("report_md")
                schemes = rep.get("schemes") or []
                source = "缓存"
        except Exception as e:
            _log("analyze 读报告库失败：", e)
    # 首次打开(无缓存) 或 强制重新生成 → 现场生成并落库
    if not report_md:
        try:
            report_md, schemes = await run_in_threadpool(_generate_report, cid, row)
            source = "重新生成" if force else "首次生成"
        except Exception as e:
            _log("现场生成失败：", e)
            report_md = _placeholder_md(summary)
            source = "占位(生成失败)"
    # AI 方案后始终追加「自定义方案」+「无需处理」，供操作人手工选人/标记不处理
    if not any((s or {}).get("id") == "custom" for s in schemes):
        schemes = list(schemes) + [dict(_CUSTOM_SCHEME)]
    if not any((s or {}).get("id") == "skip" for s in schemes):
        schemes = list(schemes) + [dict(_SKIP_SCHEME)]
    _log(f"POST /api/assignment/analyze caseId={cid} → {source}，方案 {len(schemes)} 组")
    return {"caseId": cid, "reportMd": report_md, "schemes": schemes,
            "detail": _placeholder_detail(summary)}


@router.get("/oa-record/{cid}")
def oa_record_redirect(cid: str):
    """跳转到该案的 `案号-OA信息记录表` Wiki 页。由 cid(=oa_id) 找案号 → 解析 URL → 302。"""
    st = _store()
    proj = ""
    if st is not None:
        try:
            row = next((r for r in st.list_pending() if r.get("id") == cid), None)
            proj = (row or {}).get("case_volume", "") or ""
        except Exception as e:
            _log("oa-record 读待分配表失败：", e)
    url = ""
    if proj:
        try:
            oa_dir = os.path.join(_DIR, "..", "oa")
            if oa_dir not in sys.path:
                sys.path.insert(0, oa_dir)
            from oainfo_cli import oa_record_url
            url = oa_record_url(proj)
        except Exception as e:
            _log("oa-record 解析URL失败：", e)
    if url:
        return RedirectResponse(url)
    return JSONResponse({"error": f"未找到 OA信息记录表：{cid}/{proj or '案号未知'}"}, status_code=404)


@router.get("/api/staff/list")
def staff_list(q: str = "", role: str = ""):
    """人员下拉：查真实 users（status<>'离职'），返回姓名(username_zn)数组；支持 q 关键字搜索。
    DB 异常直接返回空（前端空栏），不回退桩数据。"""
    kw = (q or "").strip()
    try:
        oa_dir = os.path.join(_DIR, "..", "oa")
        if oa_dir not in sys.path:
            sys.path.insert(0, oa_dir)
        from db_query import execute
        # 在职判定：status<>'离职' 且 usermail 有值（无 usermail 视同离职）
        where = ("status <> '离职' AND username_zn IS NOT NULL AND username_zn <> '' "
                 "AND usermail IS NOT NULL AND usermail <> ''")
        if kw:
            where += f" AND username_zn LIKE '%{kw.replace(chr(39), chr(92)+chr(39))}%'"
        rows = execute(f"SELECT DISTINCT username_zn FROM users WHERE {where} "
                       f"ORDER BY username_zn LIMIT 50")
        names = [r.get("username_zn") for r in (rows or []) if r.get("username_zn")]
        _log(f"GET  /api/staff/list q='{kw}' → {len(names)} 人(users)")
        return {"role": role, "staff": names}
    except Exception as e:
        _log("查 users 失败，返回空：", e)
        return {"role": role, "staff": []}     # DB 异常直接空栏，不回退桩


_SHARE_DEFAULT_TO = "yan.li@metis-ip.com"


def _esc(s):
    """HTML 转义（用于分享邮件 HTML 正文，& 先转）。"""
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _send_share_email(to_list, cc_list, subject, body, html_body=None):
    """用 pa 账号发分享邮件（复用 read_email 的 SMTP + 共享 email_config）。返回 (ok, msg)。
    传 html_body 时发 multipart/alternative（纯文本 + HTML），链接以真正的 <a> 超链接显示。"""
    try:
        oa_dir = os.path.join(_DIR, "..", "oa")
        if oa_dir not in sys.path:
            sys.path.insert(0, oa_dir)
        import read_email as RE
        RE.set_config_path(os.path.join(_DIR, "..", "email_config.json"))
        pa = (RE.load_config().get("accounts", {}) or {}).get("pa")
        if not pa:
            return False, "未配置 PA 账号"
        import smtplib
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        msg = MIMEMultipart("alternative") if html_body else MIMEMultipart()
        msg["From"] = pa["user"]
        msg["To"] = ", ".join(to_list)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        msg["Subject"] = subject
        # alternative：纯文本在前、HTML 在后（客户端优先渲染 HTML，纯文本兜底）
        msg.attach(MIMEText(body, "plain", "utf-8"))
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))
        smtp = smtplib.SMTP(pa["smtp_host"], pa["smtp_port"])
        smtp.ehlo(); smtp.starttls(); smtp.ehlo()
        token = RE._get_smtp_oauth2_token(pa)
        if token:
            auth = f"user={pa['user']}\x01auth=Bearer {token}\x01\x01"
            try:
                smtp.docmd("AUTH", "XOAUTH2 " + base64.b64encode(auth.encode()).decode())
            except smtplib.SMTPAuthenticationError:
                smtp.login(pa["user"], pa["password"])
        else:
            smtp.login(pa["user"], pa["password"])
        smtp.sendmail(pa["user"], to_list + cc_list, msg.as_string())
        smtp.quit()
        return True, "ok"
    except Exception as e:
        return False, str(e)


@router.post("/api/assignment/share")
async def assignment_share(req: Request):
    """分享：先把当前所选人员写库（=提交分配），再发分享邮件到指定邮箱。
    邮件正文写「案号 分配情况 + 人员 + 只读分享链接」；分享页只显示中栏报告 + 已选人员。"""
    body = await req.json()
    cid = body.get("caseId")
    case_no = body.get("caseNo", "") or ""
    responder, qc, aqc = body.get("responder"), body.get("qc"), body.get("aqc", "")
    to_list = [e.strip() for e in (body.get("to") or []) if e and e.strip()] or [_SHARE_DEFAULT_TO]
    cc_list = [e.strip() for e in (body.get("cc") or []) if e and e.strip()]
    if not cid:
        return {"ok": False, "msg": "缺 caseId"}
    if not (responder and qc):
        return {"ok": False, "msg": "请先选择分配人员"}
    bad = _invalid_names(responder, qc, aqc)
    if bad:
        return {"ok": False, "msg": f"以下人员不在 users 库：{'、'.join(bad)}，请改选"}
    # 1. 写库（等同提交分配：回写 Wiki + projects/绩效表 + submit_json）
    wb = _write_back(cid, responder, qc, body.get("postscript", ""), body.get("customNote", ""), aqc)
    _mark(cid, responder, _combine_qc(qc, aqc))
    _save_submission(body)
    _write_share_file(cid, [cid], batch=False)   # 提交时把内容写死成静态页
    # 2. 只读分享链接（base 优先环境变量，其次 pipeline_config.oa_assign_base_url）
    base = os.environ.get("OA_ASSIGN_BASE_URL", "").strip().rstrip("/")
    if not base:
        try:
            with open(os.path.join(_DIR, "..", "pipeline_config.json"), encoding="utf-8") as f:
                base = (json.load(f).get("oa_assign_base_url") or "").strip().rstrip("/")
        except Exception:
            base = ""
    link = f"{base}/oa-assign/share?oaid={cid}"
    # 3. 发分享邮件
    ppl = f"负责人：{responder}；QC：{qc}" + (f"；AQC：{aqc}" if aqc else "")
    subject = f"【OA分配情况】{case_no}"
    mail_body = (f"{case_no} 分配情况：\n{ppl}\n\n"
                 f"点击查看案件分析报告及分配人员（只读）：\n{link}\n")
    html_body = (f"<p>{_esc(case_no)} 分配情况：<br>{_esc(ppl)}</p>"
                 f"<p>点击查看案件分析报告及分配人员（只读）：<br>"
                 f'<a href="{_esc(link)}">{_esc(link)}</a></p>')
    ok, msg = _send_share_email(to_list, cc_list, subject, mail_body, html_body)
    _log(f"POST /api/assignment/share caseId={cid} → 写库+发邮件 to={to_list} cc={cc_list} ok={ok}")
    return {"ok": ok, "caseId": cid, "writeback": wb, "link": link, "mail": msg}


def _share_base():
    """只读分享链接 base：环境变量 OA_ASSIGN_BASE_URL 优先，其次 pipeline_config.oa_assign_base_url。"""
    base = os.environ.get("OA_ASSIGN_BASE_URL", "").strip().rstrip("/")
    if not base:
        try:
            with open(os.path.join(_DIR, "..", "pipeline_config.json"), encoding="utf-8") as f:
                base = (json.load(f).get("oa_assign_base_url") or "").strip().rstrip("/")
        except Exception:
            base = ""
    return base


# ── 只读分享页「静态化」：提交/分享时把内容渲染成一份自包含 HTML 写死到磁盘 ──
# output/oa-share/{key}.html（单案 key=oaid、批量 key=batch_id）。打开时 report_server
# 优先返回该文件（零查库/零 API/不依赖 CDN）；文件缺失才回退到 assign.html 动态 shareView。
def _share_dir():
    d = os.path.join(_DIR, "..", "output", "oa-share")
    os.makedirs(d, exist_ok=True)
    return d


def _case_for_share(cid):
    """从 store 读某案的报告(report_md)+已选人员(submit) + projects 案号/OA次数，拼成静态页所需 dict。"""
    st = _store()
    data = {}
    if st is not None:
        try:
            data = st.get_report(cid) or {}
        except Exception as e:
            _log("静态分享读 report 失败：", e)
    case_no, oa_seq = "", 0
    try:
        from db_query import execute as dbx
        rows = dbx(f"SELECT project, project_name FROM projects WHERE id='{cid}'")
        if isinstance(rows, list) and rows:
            case_no = rows[0].get("project", "") or ""
            oa_seq = _oa_seq_of(rows[0].get("project_name", "") or "")
    except Exception as e:
        _log("静态分享读 projects 失败：", e)
    return {"oaid": cid, "caseNo": case_no, "oaSeq": oa_seq,
            "reportMd": data.get("report_md", "") or "", "submit": data.get("submit") or {}}


def _write_share_file(key, oaids, shared_at="", batch=False):
    """生成并写死静态分享页到 output/oa-share/{key}.html。best-effort，失败返 False（打开时回退动态页）。"""
    try:
        import share_html
        cases = [_case_for_share(c) for c in oaids if c]
        html = share_html.build_share_html(cases, shared_at=shared_at, batch=batch)
        with open(os.path.join(_share_dir(), f"{key}.html"), "w", encoding="utf-8") as f:
            f.write(html)
        return True
    except Exception as e:
        _log("写静态分享页失败：", e)
        return False


@router.post("/api/assignment/share/batch")
async def assignment_share_batch(req: Request):
    """批量分享：把每件当前所选人员写库（=提交分配），各案只读链接汇总到「一封」邮件发到指定邮箱。
    body: { items:[{caseId,caseNo,responder,qc,aqc,postscript,customNote}], to:[], cc:[] }。
    邮件失败则整体标失败（但写库已完成，不回滚）。"""
    body = await req.json()
    items = body.get("items") or []
    to_list = [e.strip() for e in (body.get("to") or []) if e and e.strip()] or [_SHARE_DEFAULT_TO]
    cc_list = [e.strip() for e in (body.get("cc") or []) if e and e.strip()]
    base = _share_base()
    results, sections, html_sections, ok_oaids = [], [], [], []
    for it in items:
        cid = it.get("caseId")
        case_no = it.get("caseNo", "") or ""
        responder, qc, aqc = it.get("responder"), it.get("qc"), it.get("aqc", "")
        if not cid:
            results.append({"caseId": cid, "ok": False, "msg": "缺 caseId"}); continue
        if not (responder and qc):
            results.append({"caseId": cid, "ok": False, "msg": "未选分配人员"}); continue
        bad = _invalid_names(responder, qc, aqc)
        if bad:
            results.append({"caseId": cid, "ok": False, "msg": f"人员不在 users 库：{'、'.join(bad)}"}); continue
        try:
            _write_back(cid, responder, qc, it.get("postscript", ""), it.get("customNote", ""), aqc)
            _mark(cid, responder, _combine_qc(qc, aqc))
            _save_submission(it)
        except Exception as e:
            results.append({"caseId": cid, "ok": False, "msg": f"写库失败：{e}"}); continue
        ok_oaids.append(cid)
        ppl = f"负责人：{responder}；QC：{qc}" + (f"；AQC：{aqc}" if aqc else "")
        sections.append(f"{case_no}：{ppl}")
        html_sections.append(f"<li>{_esc(case_no)}：{_esc(ppl)}</li>")
        results.append({"caseId": cid, "ok": True})
    ok_n = len(ok_oaids)
    mail = "（无成功案件，未发邮件）"
    link = ""
    if ok_oaids:
        # 一批次一链接：存批次(batch_id→oaid列表+分享时间)，邮件只放这一条链接
        import uuid
        batch_id = uuid.uuid4().hex[:12]
        shared_at = f"{datetime.now():%Y-%m-%d %H:%M}"
        st = _store()
        if st is not None:
            try:
                st.save_share_batch(batch_id, ok_oaids, shared_at)
            except Exception as e:
                _log("保存分享批次失败：", e)
        _write_share_file(batch_id, ok_oaids, shared_at=shared_at, batch=True)  # 提交时写死成静态页
        link = f"{base}/oa-assign/share?batch={batch_id}"
        subject = f"【OA分配情况】{shared_at} 共 {ok_n} 件"
        mail_body = (f"本批次（{shared_at}）共 {ok_n} 件案件的 OA 分配情况：\n\n"
                     + "\n".join(sections)
                     + f"\n\n点击查看全部案件分析报告及分配人员（只读，可在左栏切换案件）：\n{link}\n")
        html_body = (f"<p>本批次（{_esc(shared_at)}）共 {ok_n} 件案件的 OA 分配情况：</p>"
                     f"<ul>{''.join(html_sections)}</ul>"
                     f"<p>点击查看全部案件分析报告及分配人员（只读，可在左栏切换案件）：<br>"
                     f'<a href="{_esc(link)}">{_esc(link)}</a></p>')
        sok, mail = _send_share_email(to_list, cc_list, subject, mail_body, html_body)
        if not sok:
            _log(f"POST /api/assignment/share/batch 邮件失败：{mail}")
            return {"ok": False, "results": results, "mail": mail, "link": link, "msg": f"发送失败：{mail}"}
    _log(f"POST /api/assignment/share/batch 共{len(items)} 成功{ok_n} to={to_list} cc={cc_list} link={link}")
    return {"ok": ok_n > 0, "results": results, "mail": mail, "link": link}


@router.get("/api/assignment/shared/{oaid}")
def assignment_shared(oaid: str):
    """分享页只读数据：中栏报告(reportMd) + 已选人员(submit_json)。"""
    st = _store()
    data = {}
    if st is not None:
        try:
            data = st.get_report(oaid) or {}
        except Exception as e:
            _log("分享页读 report 失败：", e)
    case_no, oa_seq = "", ""
    try:
        from db_query import execute as dbx
        rows = dbx(f"SELECT project, project_name FROM projects WHERE id='{oaid}'")
        if isinstance(rows, list) and rows:
            case_no = rows[0].get("project", "") or ""
            oa_seq = _oa_seq_of(rows[0].get("project_name", "") or "")
    except Exception as e:
        _log("分享页读 projects 失败：", e)
    return {"oaid": oaid, "caseNo": case_no, "oaSeq": oa_seq,
            "reportMd": data.get("report_md", "") or "", "submit": data.get("submit") or {}}


@router.get("/api/assignment/shared-batch/{batch_id}")
def assignment_shared_batch(batch_id: str):
    """批量分享只读页：返回该批次的分享时间 + 案件清单（左栏用；每案报告/人员点开时再按 oaid 拉）。"""
    st = _store()
    batch = None
    if st is not None:
        try:
            batch = st.get_share_batch(batch_id)
        except Exception as e:
            _log("分享批次读取失败：", e)
    if not batch:
        return {"batchId": batch_id, "sharedAt": "", "cases": []}
    oaids = batch.get("oaids") or []
    cases = []
    try:
        from db_query import execute as dbx
        for oid in oaids:
            case_no, oa_seq = "", ""
            rows = dbx(f"SELECT project, project_name FROM projects WHERE id='{oid}'")
            if isinstance(rows, list) and rows:
                case_no = rows[0].get("project", "") or ""
                oa_seq = _oa_seq_of(rows[0].get("project_name", "") or "")
            cases.append({"oaid": oid, "caseNo": case_no, "oaSeq": oa_seq})
    except Exception as e:
        _log("分享批次读 projects 失败：", e)
        cases = [{"oaid": oid, "caseNo": "", "oaSeq": ""} for oid in oaids]
    return {"batchId": batch_id, "sharedAt": batch.get("shared_at", "") or "", "cases": cases}


@router.post("/api/assignment/submit")
async def assignment_submit(req: Request):
    body = await req.json()
    _log("POST /api/assignment/submit 收到：", json.dumps(body, ensure_ascii=False))
    cid, responder, qc = body.get("caseId"), body.get("responder"), body.get("qc")
    aqc = body.get("aqc", "")
    bad = _invalid_names(responder, qc, aqc)             # 校验 责任人/QC/AQC 都在 users.username_zn
    if bad:
        return {"ok": False, "caseId": cid,
                "writeback": {"code": 1, "msg": f"以下人员不在 users 库：{'、'.join(bad)}，请改选"}}
    wb = _write_back(cid, responder, qc, body.get("postscript", ""),
                     body.get("customNote", ""), aqc)    # Wiki: QC/AQC 分开标
    _mark(cid, responder, _combine_qc(qc, aqc))          # projects/绩效表: QC,AQC 逗号拼
    _save_submission(body)                               # 选中结果+附言(附言/原因)存 oa_assign_report.submit_json
    _log("    回写 Wiki 人员分配：", wb.get("msg"))
    return {"ok": True, "caseId": cid, "writeback": wb}


@router.post("/api/assignment/skip")
async def assignment_skip(req: Request):
    """标记某案「不需处理」：只置 oa_assign_task.status=2（从待分配列表移除），不写 Wiki/projects/绩效表。"""
    body = await req.json()
    cid = body.get("caseId")
    st = _store()
    if st is None or not cid:
        return {"ok": False, "msg": "待分配库不可用或缺 caseId"}
    try:
        ok = st.mark_skipped(cid)
        st.save_submission(cid, {"skipped": True,
                                 "submitted_at": f"{datetime.now():%Y-%m-%d %H:%M}"})  # 留痕
        _log(f"POST /api/assignment/skip caseId={cid} → 不需处理")
        return {"ok": bool(ok), "caseId": cid}
    except Exception as e:
        _log("标记不需处理失败：", e)
        return {"ok": False, "caseId": cid, "msg": str(e)}


@router.post("/api/assignment/skip/batch")
async def assignment_skip_batch(req: Request):
    """批量标记「无需处理」：逐案置 oa_assign_task.status=2（从待分配移除），不写 Wiki/projects/绩效表。"""
    body = await req.json()
    ids = [i for i in (body.get("caseIds", []) or []) if i]
    st = _store()
    if st is None:
        return {"ok": False, "count": 0, "msg": "待分配库不可用"}
    n = 0
    for cid in ids:
        try:
            st.mark_skipped(cid)
            st.save_submission(cid, {"skipped": True,
                                     "submitted_at": f"{datetime.now():%Y-%m-%d %H:%M}"})
            n += 1
        except Exception as e:
            _log("批量标记不需处理失败：", cid, e)
    _log(f"POST /api/assignment/skip/batch → {n}/{len(ids)} 件不需处理")
    return {"ok": True, "count": n}


@router.post("/api/assignment/submit/batch")
async def assignment_submit_batch(req: Request):
    body = await req.json()
    assignments = body.get("assignments", []) or []
    _log(f"POST /api/assignment/submit/batch 收到 {len(assignments)} 件：")
    # 人名校验（责任人/QC/AQC 都要在 users）：不合格的案子不写，单独报错
    bad_map = {}   # caseId -> [不存在的名字]
    valid = []
    for a in assignments:
        bad = _invalid_names(a.get("responder"), a.get("qc"), a.get("aqc"))
        if bad:
            bad_map[a.get("caseId")] = bad
        else:
            valid.append(a)
    # Wiki 回写：一次性批量（QC/AQC 分开标；一次取页一次存页）
    wb_map = _write_back_batch(valid)
    # DB 回写（projects / oa_assign_task / tip_budgetperformance_role）+ submit_json：逐案，QC 用 QC,AQC 逗号拼
    for a in valid:
        _mark(a.get("caseId"), a.get("responder"), _combine_qc(a.get("qc"), a.get("aqc")))
        _save_submission(a)
    results = []
    for a in assignments:
        cid = a.get("caseId")
        if cid in bad_map:
            results.append({"caseId": cid, "writeback": {"code": 1,
                            "msg": f"以下人员不在 users 库：{'、'.join(bad_map[cid])}，请改选"}})
        else:
            results.append({"caseId": cid, "writeback": wb_map.get(cid, {"code": 1, "msg": "无回写结果"})})
    return {"ok": not bad_map, "count": len(valid), "invalid": bad_map,
            "caseIds": [a.get("caseId") for a in valid], "results": results}
