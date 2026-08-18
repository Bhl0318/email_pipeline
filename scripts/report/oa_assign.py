#!/usr/bin/env python3
"""OA 分配工具 —— 后端路由（并入汇报信服务 report_server）。

在 report_server.py 里 `app.include_router(oa_assign.router)` 挂载，页面走 /static/assign.html。

接口（与 web/assign.html 约定一致）：
  GET  /api/cases/pending            待分配案件列表(摘要)——读 oa_assign_task JOIN projects
  POST /api/assignment/analyze       {caseId} → 该案 AI 报告(reportMd)+分配建议(schemes)——读 oa_assign_report
  GET  /api/staff/list?role=         人员库(下拉搜索用)——暂用桩数据 stub_staff，下一步接 DB
  POST /api/assignment/submit        单案提交——回写 Wiki 人员分配 + projects + 待分配表置已分配
  POST /api/assignment/submit/batch  批量提交（同上，逐案）

数据现状：案件列表/AI 报告已走真实库；仅人员下拉(staff)仍为桩，待接 DB 历史承办。
"""
import json
import os
import sys
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

_DIR = os.path.dirname(os.path.abspath(__file__))
_STUB_DIR = os.path.join(_DIR, "oa_assign_stub")

# 人员库暂用桩数据（选人下拉），下一步接 DB 后替换。案件/报告已走真实数据，不再用桩。
with open(os.path.join(_STUB_DIR, "stub_staff.json"), encoding="utf-8") as _f:
    STUB_STAFF = json.load(_f)

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


@router.post("/api/assignment/analyze")
async def assignment_analyze(req: Request):
    body = await req.json()
    cid = body.get("caseId")
    # 真实待分配案件：读立项时生成的 AI 案件报告(markdown)；无则给占位 md。
    st = _store()
    row = None
    if st is not None:
        try:
            row = next((r for r in st.list_pending() if r.get("id") == cid), None)
        except Exception as e:
            _log("analyze 读待分配表失败：", e)
    if row:
        summary = _row_to_summary(row)
        report_md, schemes, has_report = "", [], False
        try:
            rep = st.get_report(cid) if st is not None else None
            if rep and (rep.get("report_md") or "").strip():
                report_md = rep.get("report_md")
                schemes = rep.get("schemes") or []
                has_report = True
        except Exception as e:
            _log("analyze 读报告库失败：", e)
        if not report_md:
            report_md = _placeholder_md(summary)
        if not schemes:
            schemes = [dict(_CUSTOM_SCHEME)]     # 人员方案下一步接 DB 再补，先给自定义
        _log(f"POST /api/assignment/analyze caseId={cid} → {'AI报告' if has_report else '占位md(报告未生成)'}")
        return {"caseId": cid, "reportMd": report_md, "schemes": schemes,
                "detail": _placeholder_detail(summary)}
    _log(f"POST /api/assignment/analyze caseId={cid} → 未找到")
    return JSONResponse({"error": f"案件不存在: {cid}"}, status_code=404)


@router.get("/api/staff/list")
def staff_list(role: str = ""):
    _log(f"GET  /api/staff/list role={role or '(全部)'} → {len(STUB_STAFF)} 人")
    return {"role": role, "staff": STUB_STAFF}


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
