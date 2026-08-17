#!/usr/bin/env python3
"""OA 分配工具 —— 后端路由（并入汇报信服务 report_server）。

第一阶段：全部返回 oa_assign_stub/ 下的测试数据并打印，不接真库/真 AI、不回写。
在 report_server.py 里 `app.include_router(oa_assign.router)` 挂载，页面走 /static/assign.html。

接口（与原型 web/assign.html 约定一致）：
  GET  /api/cases/pending            待分配案件列表(摘要)
  POST /api/assignment/analyze       {caseId} → 该案 AI 报告(detail)+分配建议(schemes)
  GET  /api/staff/list?role=         人员库(下拉搜索用)
  POST /api/assignment/submit        单案提交(打印，暂不回写)
  POST /api/assignment/submit/batch  批量提交(打印，暂不回写)

后续：submit 接 oainfo_cli 回写 Wiki「测试页面-写入新增OA」人员分配字段 + 立项分配表；
      analyze/cases 换真数据(邮件/NAS/TIP)+真 AI。
"""
import json
import os
import sys
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

_DIR = os.path.dirname(os.path.abspath(__file__))
_STUB_DIR = os.path.join(_DIR, "oa_assign_stub")

with open(os.path.join(_STUB_DIR, "stub_cases.json"), encoding="utf-8") as _f:
    STUB_CASES = json.load(_f)
with open(os.path.join(_STUB_DIR, "stub_staff.json"), encoding="utf-8") as _f:
    STUB_STAFF = json.load(_f)

# 左栏列表摘要字段（detail/schemes 打开案件时经 analyze 再取）
_SUMMARY_KEYS = ("id", "caseNo", "name", "urgency", "client",
                 "legalStatus", "daysLeft", "estimate", "submitted", "files")

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


@router.get("/api/cases/pending")
def cases_pending(page: int = 1, pageSize: int = 100):
    items = [{k: c.get(k) for k in _SUMMARY_KEYS} for c in STUB_CASES]
    _log(f"GET  /api/cases/pending page={page} → {len(items)} 件(测试数据)")
    return {"total": len(items), "items": items}


@router.post("/api/assignment/analyze")
async def assignment_analyze(req: Request):
    body = await req.json()
    cid = body.get("caseId")
    c = next((x for x in STUB_CASES if x.get("id") == cid), None)
    if not c:
        _log(f"POST /api/assignment/analyze caseId={cid} → 未找到")
        return JSONResponse({"error": f"案件不存在: {cid}"}, status_code=404)
    _log(f"POST /api/assignment/analyze caseId={cid} → 报告(测试数据)+{len(c.get('schemes', []))}组建议")
    return {"caseId": cid, "detail": c.get("detail"), "schemes": c.get("schemes", [])}


@router.get("/api/staff/list")
def staff_list(role: str = ""):
    _log(f"GET  /api/staff/list role={role or '(全部)'} → {len(STUB_STAFF)} 人")
    return {"role": role, "staff": STUB_STAFF}


@router.post("/api/assignment/submit")
async def assignment_submit(req: Request):
    body = await req.json()
    _log("POST /api/assignment/submit 收到：", json.dumps(body, ensure_ascii=False))
    wb = _write_back(body.get("caseId"), body.get("responder"), body.get("qc"))
    _log("    回写 Wiki 人员分配：", wb.get("msg"))
    return {"ok": True, "caseId": body.get("caseId"), "writeback": wb}


@router.post("/api/assignment/submit/batch")
async def assignment_submit_batch(req: Request):
    body = await req.json()
    assignments = body.get("assignments", []) or []
    _log(f"POST /api/assignment/submit/batch 收到 {len(assignments)} 件：")
    results = []
    for a in assignments:
        _log("    -", json.dumps(a, ensure_ascii=False))
        wb = _write_back(a.get("caseId"), a.get("responder"), a.get("qc"))
        _log("      回写：", wb.get("msg"))
        results.append({"caseId": a.get("caseId"), "writeback": wb})
    return {"ok": True, "count": len(assignments),
            "caseIds": [a.get("caseId") for a in assignments], "results": results}
