#!/usr/bin/env python3
"""OA 分配白名单维护 —— 后端路由（并入 report_server）。

维护页 web/whitelist.html 同源调用，实时写 atw 表 oa_assign_whitelist。
  GET  /api/whitelist/list             全量
  POST /api/whitelist/add   {biz_type,tier,grade,field,name_raw,note,flag}
  POST /api/whitelist/delete {id}
  POST /api/whitelist/update {id, ...COLS}
"""
import os
import sys
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

_DIR = os.path.dirname(os.path.abspath(__file__))
router = APIRouter(tags=["oa-whitelist"])


def _log(*a):
    print(f"[{datetime.now():%H:%M:%S}][oa-whitelist]", *a, file=sys.stderr, flush=True)


def _store():
    try:
        oa_dir = os.path.join(_DIR, "..", "oa")
        if oa_dir not in sys.path:
            sys.path.insert(0, oa_dir)
        import oa_whitelist_store
        return oa_whitelist_store
    except Exception as e:
        _log("白名单库不可用：", e)
        return None


@router.get("/api/whitelist/list")
def whitelist_list():
    st = _store()
    if st is None:
        return {"total": 0, "items": [], "error": "白名单库模块不可用"}
    try:
        rows = st.list_all()
        _log(f"GET  /api/whitelist/list → {len(rows)} 条")
        return {"total": len(rows), "items": rows}
    except Exception as e:
        _log("读白名单失败：", e)
        return {"total": 0, "items": [], "error": f"读白名单失败: {e}"}


@router.post("/api/whitelist/add")
async def whitelist_add(req: Request):
    body = await req.json()
    st = _store()
    if st is None:
        return JSONResponse({"ok": False, "error": "白名单库不可用"}, status_code=500)
    try:
        ok = st.add(body)
        _log(f"POST /api/whitelist/add {body.get('name_raw')} → {'成功' if ok else '缺必填(biz_type/tier/name_raw)'}")
        return {"ok": bool(ok)}
    except Exception as e:
        _log("新增失败：", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.post("/api/whitelist/delete")
async def whitelist_delete(req: Request):
    body = await req.json()
    st = _store()
    if st is None:
        return JSONResponse({"ok": False, "error": "白名单库不可用"}, status_code=500)
    try:
        ok = st.delete(body.get("id"))
        _log(f"POST /api/whitelist/delete id={body.get('id')} → {'成功' if ok else '无效id'}")
        return {"ok": bool(ok)}
    except Exception as e:
        _log("删除失败：", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.post("/api/whitelist/update")
async def whitelist_update(req: Request):
    body = await req.json()
    st = _store()
    if st is None:
        return JSONResponse({"ok": False, "error": "白名单库不可用"}, status_code=500)
    try:
        rid = body.pop("id", None)
        ok = st.update(rid, body)
        _log(f"POST /api/whitelist/update id={rid} → {'成功' if ok else '无变更/无效id'}")
        return {"ok": bool(ok)}
    except Exception as e:
        _log("更新失败：", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
