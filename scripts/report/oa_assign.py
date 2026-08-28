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
import sys
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse

_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(tags=["oa-assign"])


def _log(*a):
    print(f"[{datetime.now():%H:%M:%S}][oa-assign]", *a, file=sys.stderr, flush=True)


def _write_back(case_id, responder, qc):
    """按 case_id(=oa_id) 回写 Wiki 新增OA 人员分配格。best-effort：桩数据/无 Wiki 时返回失败也不抛。"""
    try:
        oa_dir = os.path.join(_DIR, "..", "oa")
        if oa_dir not in sys.path:
            sys.path.insert(0, oa_dir)
        from oainfo_cli import write_oa_assignment
        return write_oa_assignment(case_id, responder, qc)
    except Exception as e:
        return {"code": 1, "msg": f"回写调用失败: {e}"}


def _mark(case_id, responder, qc):
    """待分配表回填分配结果并置已分配。best-effort，不抛。"""
    st = _store()
    if st is None or not case_id:
        return
    try:
        st.mark_submitted(case_id, responder or "", qc or "")
    except Exception as e:
        _log("待分配表回填失败：", e)


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


def _row_to_summary(r):
    """待分配表行 → 前端摘要。"""
    return {
        "id": r.get("id", ""),
        "caseNo": r.get("case_volume", ""),
        "name": r.get("project_name", ""),
        "client": r.get("customer", ""),
        "region": r.get("region", ""),
        "legalStatus": "",
        "urgency": "",
        "daysLeft": None,
        "estimate": "",
        "deadline": r.get("project_deadline", ""),
        "submitted": bool(r.get("submitted")),
        "files": [],
    }


# 真实待分配案件暂无 AI 报告：给结构完整的占位报告(前端不崩) + 仅"自定义方案"供人工选人
_CUSTOM_SCHEME = {"id": "custom", "label": "自定义方案", "note": "", "responder": "", "qc": ""}


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
def cases_pending(page: int = 1, pageSize: int = 100):
    # 读真实待分配表（oa_assign_task JOIN projects）。
    st = _store()
    if st is None:
        return {"total": 0, "items": [], "error": "待分配库模块不可用"}
    try:
        rows = st.list_pending()
        items = [_row_to_summary(r) for r in rows]
        _log(f"GET  /api/cases/pending → {len(items)} 件(待分配表)")
        return {"total": len(items), "items": items}
    except Exception as e:
        _log("读待分配表失败：", e)
        return {"total": 0, "items": [], "error": f"读待分配表失败: {e}"}


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
    # AI 方案后始终追加「自定义方案」，供操作人手工选人
    if not any((s or {}).get("id") == "custom" for s in schemes):
        schemes = list(schemes) + [dict(_CUSTOM_SCHEME)]
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


@router.post("/api/assignment/submit")
async def assignment_submit(req: Request):
    body = await req.json()
    _log("POST /api/assignment/submit 收到：", json.dumps(body, ensure_ascii=False))
    cid, responder, qc = body.get("caseId"), body.get("responder"), body.get("qc")
    wb = _write_back(cid, responder, qc)                 # 回写 Wiki 人员分配格
    _mark(cid, responder, qc)                            # 待分配表回填结果+置已分配
    _log("    回写 Wiki 人员分配：", wb.get("msg"))
    return {"ok": True, "caseId": cid, "writeback": wb}


@router.post("/api/assignment/submit/batch")
async def assignment_submit_batch(req: Request):
    body = await req.json()
    assignments = body.get("assignments", []) or []
    _log(f"POST /api/assignment/submit/batch 收到 {len(assignments)} 件：")
    results = []
    for a in assignments:
        _log("    -", json.dumps(a, ensure_ascii=False))
        wb = _write_back(a.get("caseId"), a.get("responder"), a.get("qc"))
        _mark(a.get("caseId"), a.get("responder"), a.get("qc"))
        _log("      回写：", wb.get("msg"))
        results.append({"caseId": a.get("caseId"), "writeback": wb})
    return {"ok": True, "count": len(assignments),
            "caseIds": [a.get("caseId") for a in assignments], "results": results}
