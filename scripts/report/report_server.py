#!/usr/bin/env python3
"""
汇报信审核服务（FastAPI）

启动:
  cd /root/metisip-hlbi/DS/汇报信流程/scripts
  python3 report_server.py

端口: 8501

路由:
  GET  /                            健康检查
  GET  /review/{task_id}            返回 prototype.html
  GET  /api/tasks                   列表（侧栏用）；?status=pending,skipped
  GET  /api/tasks/{task_id}         查 report_tasks + LEFT JOIN projects
  GET  /templates/{name}            返回 templates/md/{name} 原文
  POST /api/tasks/{task_id}/save    UPDATE fields_json
  POST /api/tasks/{task_id}/confirm UPDATE status='done', reviewer
  POST /api/tasks/{task_id}/skip    UPDATE status='skipped'

"""
import json
import mimetypes
import os
import shutil
import sys
import re
from urllib.parse import quote
import base64
import smtplib
import uuid
from datetime import datetime
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from email.utils import getaddresses, formataddr

import requests
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent                       # DS/汇报信流程/
TEMPLATES_DIR = ROOT / "templates" / "md"


def _resolve_template(name):
    """按文件名在 templates/md/ 及其分类子目录(md/OA/、以后 md/其他类别/…)中查找模板。
    模板已按类别分子目录存放、文件名唯一，故跨目录按 basename 解析；找不到返回 None。
    （name 已由调用方校验为纯文件名，不含 / \\ ..）"""
    direct = TEMPLATES_DIR / name
    if direct.is_file():
        return direct
    for p in TEMPLATES_DIR.rglob(name):
        if p.is_file():
            return p
    return None


def _template_text(name):
    """模板正文：先读 report_template 表（维护页真源），查不到/读库失败 → 回退 templates/md/ 文件。
    返回正文字符串；都没有返回 None。"""
    try:
        rows = execute_params("SELECT content FROM report_template WHERE name=%s AND status=1 LIMIT 1", (name,))
        if rows and (rows[0].get("content") or "").strip():
            return rows[0]["content"]
    except Exception as e:
        print(f"[模板] 读 report_template 失败 {name}，回退文件: {e}", file=sys.stderr)
    p = _resolve_template(name)
    if p:
        try:
            return p.read_text(encoding="utf-8")
        except Exception:
            return None
    return None


WEB_DIR = ROOT / "web"
PROTOTYPE_HTML = WEB_DIR / "prototype.html"
TEMPLATES_PREVIEW_HTML = WEB_DIR / "templates_preview.html"
EMAIL_CONFIG_PATH = SCRIPT_DIR / "email_config.json"

sys.path.insert(0, str(SCRIPT_DIR))
from db_query import execute_params  # noqa: E402


app = FastAPI(title="汇报信审核服务", version="0.1")
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# OA 分配工具（第一阶段桩）：REST 接口并入本服务；页面 web/assign.html 走 /static，入口 /oa-assign
from oa_assign import router as oa_assign_router  # noqa: E402
app.include_router(oa_assign_router)

# OA 白名单维护：REST 接口并入本服务；页面 web/whitelist.html 走 /static，入口 /oa-whitelist
from oa_whitelist import router as oa_whitelist_router  # noqa: E402
app.include_router(oa_whitelist_router)

# output/ 目录只读挂载，供审核页预览官文 PDF
_OUTPUT_DIR_FOR_MOUNT = ROOT / "output"
_OUTPUT_DIR_FOR_MOUNT.mkdir(parents=True, exist_ok=True)
app.mount("/output", StaticFiles(directory=str(_OUTPUT_DIR_FOR_MOUNT)), name="output")


# ─── 健康检查 ────────────────────────────────────────────

@app.get("/")
def root():
    return {"service": "report-review", "version": "0.1", "status": "ok"}


@app.get("/oa-assign")
def oa_assign_page(assignee: str = "", oaid: str = ""):
    """OA 分配三栏页入口 → /static/assign.html。
    带 oaid 时：过滤到该分配人(assignee)的案件并直达该案(openId)；无 oaid 则显示汇总(全部)。"""
    from urllib.parse import urlencode
    if oaid:
        q = urlencode({"assignee": assignee, "openId": oaid}) if assignee else urlencode({"openId": oaid})
        return RedirectResponse(f"/static/assign.html?{q}")
    return RedirectResponse("/static/assign.html")


_OA_SHARE_DIR = ROOT / "output" / "oa-share"   # 与 oa_assign._share_dir() 同一目录(scripts/output/oa-share)


@app.get("/oa-assign/share")
def oa_assign_share_page(oaid: str = "", batch: str = ""):
    """只读分享页：优先返回提交时写死的静态 HTML（output/oa-share/{key}.html，零查库/零 API）；
    静态文件不存在（老链接）才回退 assign.html 动态 shareView。
    单案 ?oaid=..；批量 ?batch=..（左栏案件列表可切换 + 中栏，标批次时间）。"""
    key = batch or oaid
    if key and "/" not in key and "\\" not in key and ".." not in key:
        f = _OA_SHARE_DIR / f"{key}.html"
        if f.is_file():
            return FileResponse(str(f), media_type="text/html; charset=utf-8")
    if batch:
        return RedirectResponse(f"/static/assign.html?shareView=1&batch={quote(batch)}")
    return RedirectResponse(f"/static/assign.html?shareView=1&oaid={quote(oaid)}")


@app.get("/oa-assign/{oa_id}")
def oa_assign_page_by_id(oa_id: str):
    """按 oa_id 打开分配页：加载完整待分配列表并自动定位到该案（?openId= 由前端读取）。"""
    return RedirectResponse(f"/static/assign.html?openId={oa_id}")


@app.get("/oa-whitelist")
def oa_whitelist_page():
    """OA 白名单维护页入口 → /static/whitelist.html（同源调 /api/whitelist/*，实时写 atw）。"""
    return RedirectResponse("/static/whitelist.html")


# ─── 审核页 ──────────────────────────────────────────────

@app.get("/review/{task_id}")
def review_page(task_id: str):
    """返回审核页 HTML。前端自己从 URL 抠 id 再 fetch /api/tasks/{id}。"""
    if not PROTOTYPE_HTML.exists():
        raise HTTPException(500, f"prototype.html not found at {PROTOTYPE_HTML}")
    return FileResponse(PROTOTYPE_HTML, media_type="text/html; charset=utf-8")


# ─── 任务列表（侧栏用） ──────────────────────────────────

@app.get("/api/tasks")
def list_tasks(status: str = "pending,skipped"):
    """侧栏列表用：返回精简字段。status 支持逗号分隔，如 pending / pending,skipped / pending,skipped,done。"""
    wanted = [s.strip() for s in status.split(",") if s.strip()]
    if not wanted:
        wanted = ["pending"]
    placeholders = ", ".join(["%s"] * len(wanted))
    sql = f"""
        SELECT t.id, t.status, t.fields_json, t.reviewer, t.rule_domain, t.close_combination,
               p.project       AS p_project,
               p.oa_doc_date   AS p_oa_doc_date
        FROM report_tasks t
        LEFT JOIN projects p ON p.id = t.id
        WHERE t.status IN ({placeholders})
        ORDER BY FIELD(t.status, 'pending', 'skipped', 'done'), t.id DESC
    """
    rows = execute_params(sql, tuple(wanted))
    items = []
    for r in rows:
        fj = {}
        if r.get("fields_json"):
            try:
                fj = json.loads(r["fields_json"])
            except Exception:
                fj = {}
        project = r.get("p_project") or fj.get("代理所案号", "")
        close = r.get("rule_domain") == "close"
        items.append({
            "id": r["id"],
            "status": r["status"],
            "project": project,
            "ntype": (r.get("close_combination") or fj.get("通知类型", ""))
                     if close else fj.get("通知类型", ""),
            "issue_date": str(r["p_oa_doc_date"]) if r.get("p_oa_doc_date") else fj.get("发文日期", ""),
            "reviewer": r.get("reviewer"),
        })
    return {"items": items, "total": len(items)}


# ─── 任务数据 ────────────────────────────────────────────

@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    """
    读 report_tasks + LEFT JOIN projects。
    projects 字段作为默认值，被 fields_json 里同名键覆盖。
    """
    sql = """
        SELECT t.id, t.template, t.attach_pdf, t.fields_json, t.source_attachments, t.status, t.reviewer, t.rule_domain, t.close_combination,
               p.project          AS p_project,
               p.project_name     AS p_project_name,
               p.oa_doc_date      AS p_oa_doc_date,
               p.entrust_date     AS p_entrust_date,
               p.project_deadline AS p_project_deadline,
               p.dueDate          AS p_dueDate,
               p.oaNum            AS p_oaNum,
               p.applytype        AS p_applytype
        FROM report_tasks t
        LEFT JOIN projects p ON p.id = t.id
        WHERE t.id = %s
    """
    rows = execute_params(sql, (task_id,))
    if not rows:
        raise HTTPException(404, f"task {task_id} not found")
    row = rows[0]

    # 1) projects 默认字段（OA 立项写入的权威数据）
    p_defaults = {}
    if row.get("p_project"):
        p_defaults["代理所案号"] = row["p_project"]
    if row.get("p_oa_doc_date"):
        p_defaults["发文日期"] = str(row["p_oa_doc_date"])
    if row.get("p_project_deadline"):
        p_defaults["截止日期"] = str(row["p_project_deadline"])

    # 2) fields_json（read_email.py 写入的 + 审核人改过的）
    user_fields = {}
    if row.get("fields_json"):
        try:
            user_fields = json.loads(row["fields_json"])
        except Exception as e:
            print(f"[warn] task {task_id} fields_json 解析失败: {e}", file=sys.stderr)

    # 3) enrich 案件主数据（实时查 customer + p_case_info，拿最新值）
    #    用 projects.project，没有就用 fields_json 里的代理所案号
    project = row.get("p_project") or user_fields.get("代理所案号", "")
    enriched = {}
    customer_demands = []
    interface_contacts = []   # 接口人[{name,email}]，供联系人下拉
    if project:
        try:
            from enrich_report import enrich_cn_fields, query_customer_demands, query_case_interface
            enriched = enrich_cn_fields(
                project, include_divisional_date=row.get("rule_domain") == "close")
            customer_demands = query_customer_demands(project)
            interface_contacts = query_case_interface(project)
        except Exception as e:
            print(f"[warn] task {task_id} enrich 失败: {e}", file=sys.stderr)

    # 合并优先级（低→高）：projects 默认 < enrich 主数据 < fields_json（审核人改过的最优先）
    # 注：fields_json 里值为 ""/None 的是占位，不应覆盖 enrich 查到的真实值
    effective_user = {k: v for k, v in user_fields.items() if v not in ("", None)}
    merged = {**p_defaults, **enriched, **effective_user}
    if row.get("rule_domain") == "close":
        # 结项汇报信的专利申请名称只以 IPEasy p_case_info.case_name 为准；
        # 即使 fields_json 已有值，或 IPEasy 返回空值，也不沿用 TIP 的名称。
        merged["申请名称"] = enriched.get("申请名称") or ""
        # TIP 的结项日期和 p_case_info.app_date 都不是本申请递交日。
        # 结项审核仅使用 IPEasy p_case_advance_info.divisional_date 作为默认值。
        merged["本申请递交日"] = enriched.get("本申请递交日") or ""

    # 联系人：审核人没填过（仍是占位/空）时，默认填第一个接口人（姓名+邮箱）
    if interface_contacts:
        if merged.get("联系人") in ("", None, "请提供"):
            merged["联系人"] = interface_contacts[0]["name"]
        if merged.get("联系人邮箱") in ("", None, "请提供"):
            merged["联系人邮箱"] = interface_contacts[0]["email"]
        if merged.get("联系人手机") in ("", None, "请提供"):
            merged["联系人手机"] = interface_contacts[0].get("phone", "")

    # 解析官文附件路径列表
    source_attachments = []
    if row.get("source_attachments"):
        try:
            source_attachments = json.loads(row["source_attachments"])
        except Exception as e:
            print(f"[warn] task {task_id} source_attachments 解析失败: {e}", file=sys.stderr)

    return {
        "id": row["id"],
        "rule_domain": row.get("rule_domain") or "oa",
        "matched_close_key": (row.get("close_combination") or user_fields.get("通知类型", ""))
                             if row.get("rule_domain") == "close" else "",
        "template": row["template"],
        "attach_pdf": bool(row.get("attach_pdf", 1)),
        "source_attachments": source_attachments,
        "status": row["status"],
        "reviewer": row.get("reviewer"),
        "fields": merged,
        "customer_demands": customer_demands,
        "interface_contacts": interface_contacts,   # [{name,email}] 供联系人下拉
    }


# ─── 模板内容 ────────────────────────────────────────────

@app.get("/templates/{name}")
def get_template(name: str):
    """返回模板 {name} 正文（report_template 表优先，回退 templates/md/ 文件）。审核页取此渲染汇报信。"""
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(400, "invalid template name")
    text = _template_text(name)
    if text is None:
        raise HTTPException(404, f"template {name} not found")
    return PlainTextResponse(text, media_type="text/plain; charset=utf-8")


@app.get("/api/templates")
def list_templates():
    """列出所有 md 模板，按一级子目录(OA / 结项通知 / …)分组，供模板预览页浏览。"""
    cats = {}
    if TEMPLATES_DIR.exists():
        for p in TEMPLATES_DIR.rglob("*.md"):
            rel = p.relative_to(TEMPLATES_DIR)
            cat = rel.parts[0] if len(rel.parts) > 1 else "(根目录)"
            cats.setdefault(cat, []).append(p.name)
    return {"categories": [{"name": k, "files": sorted(v)}
                           for k, v in sorted(cats.items())]}


@app.get("/templates-preview")
def templates_preview_page():
    """模板预览页：浏览/核对所有 md 模板的渲染效果。"""
    if not TEMPLATES_PREVIEW_HTML.exists():
        raise HTTPException(500, "templates_preview.html not found")
    return FileResponse(TEMPLATES_PREVIEW_HTML, media_type="text/html; charset=utf-8")


# ─── 规则管理页（文件式：UI 读写 oa_report_rules.json / close_report_rules.json）───
RULES_EDITOR_HTML = WEB_DIR / "rules_editor.html"
_RULES_READONLY = True   # True=只读预览，禁止 UI/API 写入规则；要放开编辑改回 False
_RULES_FILES = {
    "oa": SCRIPT_DIR / "oa_report_rules.json",
    "close": SCRIPT_DIR / "close_report_rules.json",
}
_EMAIL_RE = re.compile(r'^[A-Za-z0-9_.+-]+@[A-Za-z0-9_.-]+\.[A-Za-z]{2,}$')


def _validate_action(a, path, errs):
    """校验单条动作 {action, preparer?/forward?}。"""
    if not isinstance(a, dict):
        errs.append(f"{path}: 不是对象"); return
    act = a.get("action")
    if act not in ("assign", "skip", "ignore"):
        errs.append(f"{path}: action 须为 assign/skip/ignore（现 {act!r}）"); return
    if act == "assign":
        p = a.get("preparer", "")
        if not _EMAIL_RE.match(p or ""):
            errs.append(f"{path}: assign 的 preparer 邮箱非法（{p!r}）")
    if act == "skip":
        fwd = a.get("forward") or {}
        for kk in ("to", "cc"):
            for e in (fwd.get(kk) or []):
                if e and not e.startswith("对应") and not _EMAIL_RE.match(e):
                    errs.append(f"{path}: forward.{kk} 邮箱非法（{e!r}）")
    for sub in ("also_forward",):  # 双动作也校验
        if a.get(sub):
            fwd = a[sub]
            for kk in ("to", "cc"):
                for e in (fwd.get(kk) or []):
                    if e and not _EMAIL_RE.match(e):
                        errs.append(f"{path}: {sub}.{kk} 邮箱非法（{e!r}）")


def _validate_rules(kind, data):
    """基础校验：结构 + action 枚举 + 邮箱。返回错误列表（空=通过）。"""
    errs = []
    if not isinstance(data, dict):
        return ["顶层须为对象"]
    regions = [k for k in data if not k.startswith("_")]
    if kind == "oa":
        for reg in regions:
            for nt, custs in (data[reg] or {}).items():
                for code, a in (custs or {}).items():
                    if code.startswith("_"):
                        continue
                    _validate_action(a, f"{reg}/{nt}/{code}", errs)
    elif kind == "close":
        for reg in regions:
            rules = (data[reg] or {}).get("rules", {})
            for cls, r in rules.items():
                for code, a in (r.get("rules") or {}).items():
                    _validate_action(a, f"{reg}/{cls}/{code}", errs)
    return errs[:50]


@app.get("/rules-editor")
def rules_editor_page():
    """规则管理页：查看/编辑 OA 与结项 汇报信规则。"""
    if not RULES_EDITOR_HTML.exists():
        raise HTTPException(500, "rules_editor.html not found")
    return FileResponse(RULES_EDITOR_HTML, media_type="text/html; charset=utf-8")


@app.get("/api/rules-config")
def rules_config():
    """前端读此判断是否只读预览。"""
    return {"readonly": _RULES_READONLY}


@app.get("/api/rules/{kind}")
def get_rules(kind: str):
    p = _RULES_FILES.get(kind)
    if not p:
        raise HTTPException(404, f"未知规则类型 {kind}")
    if not p.is_file():
        raise HTTPException(404, f"{p.name} 不存在")
    return json.loads(p.read_text(encoding="utf-8"))


class RulesSaveReq(BaseModel):
    data: dict


@app.post("/api/rules/{kind}")
def save_rules(kind: str, req: RulesSaveReq):
    if _RULES_READONLY:
        raise HTTPException(403, "规则管理页当前为只读预览模式，暂不支持编辑保存")
    p = _RULES_FILES.get(kind)
    if not p:
        raise HTTPException(404, f"未知规则类型 {kind}")
    errs = _validate_rules(kind, req.data)
    if errs:
        raise HTTPException(400, "校验未通过：\n" + "\n".join(errs))
    # 备份一份（.bak，覆盖上次）再写
    try:
        if p.is_file():
            (p.parent / (p.name + ".bak")).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    except Exception:
        pass
    p.write_text(json.dumps(req.data, ensure_ascii=False, indent=2), encoding="utf-8")
    # 失效批处理进程的规则缓存（若同进程加载过）；模板层同步重建
    try:
        import read_email as _re
        _re._OA_RULES_CACHE = None
        if kind == "oa":
            _re.REPORT_TYPE_TO_TEMPLATE = _re._load_report_templates()
    except Exception:
        pass
    return {"ok": True, "message": "已保存"}


# ─── report_recipient 收件人表 增删改查（Web 维护入口）───
RECIPIENTS_HTML = WEB_DIR / "recipients_editor.html"
_RCP_FIELDS = ["customer_code", "family_code", "customer_name", "interface",
               "contact_name", "email", "phone", "send_type", "seq", "remark"]


@app.get("/recipients")
def recipients_page():
    """汇报信收件人维护页。"""
    if not RECIPIENTS_HTML.exists():
        raise HTTPException(500, "recipients_editor.html not found")
    return FileResponse(RECIPIENTS_HTML, media_type="text/html; charset=utf-8")


@app.get("/api/recipients")
def list_recipients(customer_code: str = "", family_code: str = "", interface: str = "",
                    q: str = "", limit: int = 500):
    where = ["status = 1"]
    params = []
    if customer_code.strip():
        where.append("customer_code = %s"); params.append(customer_code.strip())
    if family_code.strip():
        where.append("family_code = %s"); params.append(family_code.strip())
    if interface.strip():
        where.append("interface = %s"); params.append(interface.strip())
    if q.strip():
        where.append("(customer_name LIKE %s OR contact_name LIKE %s OR email LIKE %s "
                     "OR interface LIKE %s OR remark LIKE %s)")
        params += ["%" + q.strip() + "%"] * 5
    sql = ("SELECT id, " + ", ".join(_RCP_FIELDS) + " FROM report_recipient WHERE "
           + " AND ".join(where) + " ORDER BY customer_code, family_code, send_type, seq LIMIT %s")
    params.append(min(int(limit or 500), 2000))
    try:
        rows = execute_params(sql, tuple(params))
    except Exception as e:
        raise HTTPException(500, f"查询失败: {e}")
    return {"rows": rows or []}


class RecipientReq(BaseModel):
    id: int = 0
    customer_code: str = ""
    family_code: str = ""
    customer_name: str = ""
    interface: str = ""
    contact_name: str = ""
    email: str = ""
    phone: str = ""
    send_type: str = "to"
    seq: int = 0
    remark: str = ""


def _validate_recipient(r):
    errs = []
    if not re.fullmatch(r'\S{5}', (r.customer_code or "").strip()):
        errs.append("客户号须5位，不能包含空格")
    fam = (r.family_code or "").strip()
    if fam and not re.fullmatch(r'\S{5}-\w+', fam):
        errs.append("族号格式须『客户号-XXXX』或留空")
    if not _EMAIL_RE.match((r.email or "").strip()):
        errs.append("邮箱格式非法")
    if r.send_type not in ("to", "cc"):
        errs.append("类型须 to(收件人)/cc(抄送)")
    return errs


@app.post("/api/recipients")
def upsert_recipient(req: RecipientReq):
    errs = _validate_recipient(req)
    if errs:
        raise HTTPException(400, "；".join(errs))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fam = (req.family_code or "").strip() or None
    vals = (req.customer_code.strip(), fam, req.customer_name.strip(), req.interface.strip(),
            req.contact_name.strip(), req.email.strip(), req.phone.strip(),
            req.send_type, int(req.seq or 0), req.remark.strip())
    try:
        if req.id:
            execute_params(
                "UPDATE report_recipient SET customer_code=%s, family_code=%s, customer_name=%s, "
                "interface=%s, contact_name=%s, email=%s, phone=%s, send_type=%s, seq=%s, remark=%s, "
                "modifier='web', modification_time=%s WHERE id=%s",
                vals + (now, req.id))
            return {"ok": True, "id": req.id, "message": "已更新"}
        execute_params(
            "INSERT INTO report_recipient (customer_code, family_code, customer_name, interface, "
            "contact_name, email, phone, send_type, seq, remark, status, create_by, create_time) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,'web',%s)",
            vals + (now,))
        return {"ok": True, "message": "已新增"}
    except Exception as e:
        raise HTTPException(500, f"写入失败: {e}")


@app.post("/api/recipients/{rid}/delete")
def delete_recipient(rid: int):
    """软删除（status=0）。用 POST 而非 DELETE，避免部分代理拦 DELETE。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        execute_params("UPDATE report_recipient SET status=0, modifier='web', modification_time=%s WHERE id=%s",
                       (now, rid))
    except Exception as e:
        raise HTTPException(500, f"删除失败: {e}")
    return {"ok": True, "message": "已删除"}


# ═══ 汇报信规则维护（读写四表 report_rule/_template/_map + report_template）═══
# 页面 web/rules_admin.html 走 /static，入口 /rules-admin。表结构见 DS/汇报信流程/汇报信规则数据表设计.md。
RULES_ADMIN_HTML = WEB_DIR / "rules_admin.html"
_RULE_DOMAINS = {"oa": "OA官文规则", "close": "结项规则"}
_RULE_VIEW_DOMAINS = {**_RULE_DOMAINS, "official": "其他官文规则"}
_RULE_ACTIONS = {"assign", "skip", "ignore"}


def _now_s():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _jload(s):
    """把库里 forward_to/cc（JSON 数组字符串）解析成 list；空/坏 → []。"""
    s = (s or "").strip()
    if not s:
        return []
    try:
        v = json.loads(s)
        return v if isinstance(v, list) else [v]
    except Exception:
        return [x.strip() for x in s.split(",") if x.strip()]


@app.get("/rules-admin")
def rules_admin_page():
    if not RULES_ADMIN_HTML.exists():
        raise HTTPException(404, "rules_admin.html 未部署")
    return FileResponse(RULES_ADMIN_HTML, media_type="text/html; charset=utf-8")


@app.get("/api/radmin/keys")
def radmin_keys(domain: str = "", region: str = "", q: str = ""):
    """某规则域下的规则键清单（region+规则键，带模板名/attach）。用于左栏切换。"""
    if domain not in _RULE_VIEW_DOMAINS:
        raise HTTPException(400, "domain 需为 oa/close/official")
    try:
        if domain == "official":
            rule_rows = execute_params(
                "SELECT DISTINCT region, rule_key FROM report_rule WHERE rule_domain=%s", (domain,)) or []
            tpl_rows = execute_params(
                "SELECT region, rule_key, template, attach_pdf, status FROM report_rule_template WHERE rule_domain=%s",
                (domain,)) or []
            map_rows = execute_params(
                "SELECT region, rule_key, status FROM report_rule_map WHERE rule_domain=%s", (domain,)) or []
        else:
            rule_rows = execute_params(
                "SELECT DISTINCT region, rule_key FROM report_rule WHERE rule_domain=%s AND status=1", (domain,)) or []
            tpl_rows = execute_params(
                "SELECT region, rule_key, template, attach_pdf FROM report_rule_template WHERE rule_domain=%s AND status=1",
                (domain,)) or []
            map_rows = []
    except Exception as e:
        raise HTTPException(500, f"查询失败: {e}")
    tpl = {(r["region"], r["rule_key"]): r for r in tpl_rows}
    mapping = {(r["region"], r["rule_key"]): r for r in map_rows}
    keys = {(r["region"], r["rule_key"]) for r in rule_rows} | set(tpl.keys()) | set(mapping.keys())
    out = []
    for reg, rk in keys:
        if region and reg != region:
            continue
        if q and q.lower() not in rk.lower():
            continue
        t = tpl.get((reg, rk), {})
        out.append({"region": reg, "rule_key": rk,
                    "template": t.get("template", ""), "attach_pdf": int(t.get("attach_pdf", 0) or 0),
                    "status": int(mapping.get((reg, rk), {}).get("status", 1) or 0)})
    out.sort(key=lambda x: (x["region"], x["rule_key"]))
    return {"domain": domain, "keys": out}


@app.get("/api/radmin/detail")
def radmin_detail(domain: str = "", region: str = "", rule_key: str = ""):
    """某 (域,region,规则键) 的完整维护数据：分派规则行 + 模板映射 + 模板正文 + (结项)组合映射。"""
    if domain not in _RULE_VIEW_DOMAINS:
        raise HTTPException(400, "domain 需为 oa/close/official")
    active = "" if domain == "official" else " AND status=1"
    try:
        rules = execute_params(
            "SELECT id, rule_variant, customer_code, action, preparer, forward_to, forward_cc, "
            "extra_json, seq, status, remark FROM report_rule "
            "WHERE rule_domain=%s AND region=%s AND rule_key=%s" + active + " ORDER BY rule_variant, seq, id",
            (domain, region, rule_key)) or []
        tpl = execute_params(
            "SELECT template, attach_pdf, status FROM report_rule_template "
            "WHERE rule_domain=%s AND region=%s AND rule_key=%s" + active + " LIMIT 1",
            (domain, region, rule_key)) or []
        maps = execute_params(
            "SELECT id, match_key, status, remark FROM report_rule_map "
            "WHERE rule_domain=%s AND region=%s AND rule_key=%s" + active + " ORDER BY match_key",
            (domain, region, rule_key)) or []
    except Exception as e:
        raise HTTPException(500, f"查询失败: {e}")
    for r in rules:
        r["forward_to"] = _jload(r.get("forward_to"))
        r["forward_cc"] = _jload(r.get("forward_cc"))
        if domain == "official":
            if isinstance(r.get("extra_json"), str):
                try:
                    r["extra_json"] = json.loads(r["extra_json"])
                except (ValueError, TypeError):
                    r["extra_json"] = {}
        else:
            r.pop("extra_json", None)
    tpl0 = tpl[0] if tpl else {"template": "", "attach_pdf": 0}
    content = ""
    tname = (tpl0.get("template") or "").strip()
    if tname:
        try:
            c = execute_params("SELECT content FROM report_template WHERE name=%s AND status=1 LIMIT 1", (tname,))
            content = (c[0]["content"] if c else "") or ""
        except Exception as e:
            raise HTTPException(500, f"查模板正文失败: {e}")
    return {"domain": domain, "region": region, "rule_key": rule_key,
            "template": tname, "attach_pdf": int(tpl0.get("attach_pdf", 0) or 0),
            "template_status": int(tpl0.get("status", 0) or 0),
            "content": content, "rules": rules, "maps": maps}


@app.get("/api/radmin/templates")
def radmin_templates():
    """模板名清单（供模板下拉选择）。"""
    try:
        rows = execute_params("SELECT name FROM report_template WHERE status=1 ORDER BY name") or []
    except Exception as e:
        raise HTTPException(500, f"查询失败: {e}")
    return {"names": [r["name"] for r in rows]}


@app.get("/api/radmin/content")
def radmin_content_get(name: str = ""):
    """按模板名取正文（供下拉切换到任意模板时预览/编辑）。"""
    name = (name or "").strip()
    if not name:
        return {"name": "", "content": ""}
    try:
        rows = execute_params("SELECT content FROM report_template WHERE name=%s AND status=1 LIMIT 1", (name,))
    except Exception as e:
        raise HTTPException(500, f"查询失败: {e}")
    return {"name": name, "content": (rows[0]["content"] if rows else "")}


class RadminRule(BaseModel):
    id: int = 0
    rule_domain: str
    region: str
    rule_key: str
    rule_variant: str = ""
    customer_code: str
    action: str
    preparer: str = ""
    forward_to: list = []
    forward_cc: list = []
    seq: int = 0
    remark: str = ""


def _validate_rule(r: "RadminRule"):
    errs = []
    if r.rule_domain not in _RULE_DOMAINS:
        errs.append("rule_domain 非法")
    if not r.region:
        errs.append("region 必填")
    if not r.rule_key.strip():
        errs.append("rule_key 必填")
    if not r.customer_code.strip():
        errs.append("客户码必填（如 20618/5开头/其他/*）")
    if r.action not in _RULE_ACTIONS:
        errs.append("action 需为 assign/skip/ignore")
    if r.action == "assign" and not _EMAIL_RE.match((r.preparer or "").strip()):
        errs.append("assign 需填合法准备人邮箱")
    if r.action == "skip":
        alle = [e.strip() for e in (list(r.forward_to) + list(r.forward_cc)) if e and e.strip()]
        if not alle:
            errs.append("skip 需至少一个 forward 收件/抄送邮箱")
        for e in alle:
            if not _EMAIL_RE.match(e):
                errs.append(f"forward 邮箱非法: {e}")
    return errs


@app.post("/api/radmin/rule")
def radmin_rule_save(r: RadminRule):
    errs = _validate_rule(r)
    if errs:
        raise HTTPException(400, "；".join(errs))
    fto = json.dumps([e.strip() for e in r.forward_to if e and e.strip()], ensure_ascii=False) if r.action == "skip" else ""
    fcc = json.dumps([e.strip() for e in r.forward_cc if e and e.strip()], ensure_ascii=False) if r.action == "skip" else ""
    preparer = r.preparer.strip() if r.action == "assign" else ""
    now = _now_s()
    try:
        if r.id:
            execute_params(
                "UPDATE report_rule SET rule_variant=%s, customer_code=%s, action=%s, preparer=%s, "
                "forward_to=%s, forward_cc=%s, seq=%s, remark=%s, modifier='web', modification_time=%s WHERE id=%s",
                (r.rule_variant.strip(), r.customer_code.strip(), r.action, preparer, fto, fcc,
                 r.seq, r.remark.strip(), now, r.id))
        else:
            execute_params(
                "INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, "
                "preparer, forward_to, forward_cc, seq, status, remark, create_by, create_time) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s,'web',%s)",
                (r.rule_domain, r.region.strip(), r.rule_key.strip(), r.rule_variant.strip(),
                 r.customer_code.strip(), r.action, preparer, fto, fcc, r.seq, r.remark.strip(), now))
    except Exception as e:
        raise HTTPException(500, f"保存失败（可能与既有 域/region/规则键/变体/客户码 唯一键冲突）: {e}")
    return {"ok": True, "message": "已保存"}


@app.post("/api/radmin/rule/{rid}/delete")
def radmin_rule_delete(rid: int):
    try:
        execute_params("UPDATE report_rule SET status=0, modifier='web', modification_time=%s WHERE id=%s",
                       (_now_s(), rid))
    except Exception as e:
        raise HTTPException(500, f"删除失败: {e}")
    return {"ok": True, "message": "已删除"}


class RadminTpl(BaseModel):
    rule_domain: str
    region: str
    rule_key: str
    template: str = ""
    attach_pdf: bool = False


@app.post("/api/radmin/template")
def radmin_template_save(t: RadminTpl):
    """维护 report_rule_template：某 (域,region,规则键) 用哪个模板 + 是否附 PDF（UPSERT）。"""
    if t.rule_domain not in _RULE_DOMAINS or not t.region or not t.rule_key.strip():
        raise HTTPException(400, "域/region/规则键必填")
    now = _now_s()
    try:
        rows = execute_params(
            "SELECT id FROM report_rule_template WHERE rule_domain=%s AND region=%s AND rule_key=%s LIMIT 1",
            (t.rule_domain, t.region, t.rule_key.strip()))
        if rows:
            execute_params(
                "UPDATE report_rule_template SET template=%s, attach_pdf=%s, status=1, modifier='web', modification_time=%s WHERE id=%s",
                (t.template.strip(), 1 if t.attach_pdf else 0, now, rows[0]["id"]))
        else:
            execute_params(
                "INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, create_by, create_time) "
                "VALUES (%s,%s,%s,%s,%s,1,'web',%s)",
                (t.rule_domain, t.region, t.rule_key.strip(), t.template.strip(), 1 if t.attach_pdf else 0, now))
    except Exception as e:
        raise HTTPException(500, f"保存失败: {e}")
    return {"ok": True, "message": "模板映射已保存"}


class RadminMap(BaseModel):
    id: int = 0
    rule_domain: str = "close"
    region: str
    match_key: str
    rule_key: str


@app.post("/api/radmin/map")
def radmin_map_save(m: RadminMap):
    """维护 report_rule_map：结项 组合→结项类型（新增/改）。"""
    if not m.region or not m.match_key.strip() or not m.rule_key.strip():
        raise HTTPException(400, "region/组合/规则键必填")
    now = _now_s()
    match_key = m.match_key.strip()
    rule_key = m.rule_key.strip()
    try:
        if m.id:
            execute_params("UPDATE report_rule_map SET match_key=%s, rule_key=%s, status=1, modifier='web', modification_time=%s WHERE id=%s",
                           (match_key, rule_key, now, m.id))
        else:
            existing = execute_params(
                "SELECT id, rule_key, status FROM report_rule_map "
                "WHERE rule_domain=%s AND region=%s AND match_key=%s LIMIT 1",
                (m.rule_domain, m.region, match_key)) or []
            if existing:
                old = existing[0]
                if old["status"]:
                    if old["rule_key"] != rule_key:
                        raise HTTPException(409, f"组合「{match_key}」已关联规则「{old['rule_key']}」，请先删除原映射")
                    return {"ok": True, "message": "组合映射已存在"}
                execute_params(
                    "UPDATE report_rule_map SET rule_key=%s, status=1, modifier='web', modification_time=%s WHERE id=%s",
                    (rule_key, now, old["id"]))
            else:
                execute_params("INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, create_by, create_time) "
                               "VALUES (%s,%s,%s,%s,1,'web',%s)",
                               (m.rule_domain, m.region, match_key, rule_key, now))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"保存失败（组合可能已存在）: {e}")
    return {"ok": True, "message": "组合映射已保存"}


@app.post("/api/radmin/map/{mid}/delete")
def radmin_map_delete(mid: int):
    try:
        execute_params("UPDATE report_rule_map SET status=0, modifier='web', modification_time=%s WHERE id=%s",
                       (_now_s(), mid))
    except Exception as e:
        raise HTTPException(500, f"删除失败: {e}")
    return {"ok": True, "message": "已删除"}


class RadminContent(BaseModel):
    name: str
    content: str


@app.post("/api/radmin/content")
def radmin_content_save(c: RadminContent):
    """编辑模板正文 report_template.content（UPSERT），旧正文写 report_template_history（best-effort）。"""
    name = (c.name or "").strip()
    if not name:
        raise HTTPException(400, "模板名必填")
    now = _now_s()
    try:
        rows = execute_params("SELECT id, content FROM report_template WHERE name=%s LIMIT 1", (name,))
        if rows:
            # 旧正文入历史表（表不存在则忽略）
            try:
                execute_params("INSERT INTO report_template_history (name, content, modifier, modification_time) VALUES (%s,%s,'web',%s)",
                               (name, rows[0].get("content") or "", now))
            except Exception:
                pass
            execute_params("UPDATE report_template SET content=%s, status=1, modifier='web', modification_time=%s WHERE id=%s",
                           (c.content, now, rows[0]["id"]))
        else:
            execute_params("INSERT INTO report_template (name, content, format, status, create_by, create_time) "
                           "VALUES (%s,%s,'md',1,'web',%s)", (name, c.content, now))
    except Exception as e:
        raise HTTPException(500, f"保存失败: {e}")
    return {"ok": True, "message": "模板正文已保存"}


# ─── 结项邮件抄送名单（供结项 web 表单页用；规则表优先、JSON 回退，仅 skip 产 cc）───
import close_cc  # noqa: E402


@app.get("/api/close-cc")
def api_close_cc(project: str = "", task1: str = "", task2: str = "", region: str = ""):
    """单次查：案号 + 结项类型一/二 → 结项邮件抄送名单。
    地区码优先从案号提取；region 仅作为缺失或不规范案号时的兜底参数。
    返回 {region, combination, closeType, action, cc:[邮箱...]}；查不到/非skip → cc 为空。"""
    try:
        return close_cc.resolve_cc(close_cc.load_rules(), project, task1, task2, region=region or None)
    except Exception as e:
        raise HTTPException(500, f"查抄送名单失败: {e}")


@app.get("/api/close-cc-rules")
def api_close_cc_rules():
    """整份派生抄送表 {region:{combination:{客户码/5开头/其他:[cc]}}}（表单页可一次拉全量本地解析）。"""
    try:
        return close_cc.build_cc_map(close_cc.load_rules())
    except Exception as e:
        raise HTTPException(500, f"读抄送表失败: {e}")


# ─── 保存字段 ────────────────────────────────────────────

class SaveReq(BaseModel):
    fields: dict
    attach_pdf: bool | None = None


@app.post("/api/tasks/{task_id}/save")
def save_task(task_id: str, req: SaveReq):
    if req.attach_pdf is not None:
        affected = execute_params(
            "UPDATE report_tasks SET fields_json = %s, attach_pdf = %s WHERE id = %s",
            (json.dumps(req.fields, ensure_ascii=False), 1 if req.attach_pdf else 0, task_id),
        )
    else:
        affected = execute_params(
            "UPDATE report_tasks SET fields_json = %s WHERE id = %s",
            (json.dumps(req.fields, ensure_ascii=False), task_id),
        )
    if not affected:
        raise HTTPException(404, f"task {task_id} not found")
    return {"ok": True, "task_id": task_id}


# ─── 确认发送 ────────────────────────────────────────────

OUTPUT_DIR = ROOT / "output"  # 生成物按 output/{代理所案号}/ 归类


def _guanyu_type(template, fields):
    """取模板「关于：」行破折号(–/—)前的前缀作主题类型段（占位用 fields 填好）。
    如 CN→'国家知识产权局审查意见'、US→'美国专利商标局审查意见'、EP EESR→'欧洲专利申请扩展检索报告'。
    取不到（无模板/无关于行）返回 None，调用方回退旧逻辑。"""
    if not template:
        return None
    text = _template_text(template)
    if text is None:
        return None
    m = re.search(r'关于[：:]\s*(.+)', text)
    if not m:
        return None
    line = m.group(1).strip().strip('*').strip()
    line = re.sub(r'\{\{\s*(.+?)\s*\}\}', lambda x: str(fields.get(x.group(1), "")), line)
    line = re.split(r'[–—]', line)[0].strip()   # 截到第一个破折号前
    return line or None


def _safe_filename(fields, template=None):
    """按 example/ 的命名拼汇报信文件名（去掉文件名非法字符）。
    类型段优先用模板「关于：」前缀，取不到则回退 通知类型+转达。"""
    issue = datetime.now().strftime("%Y-%m-%d")   # 邮件发送日（原为发文日期，已改）
    ntype = _guanyu_type(template, fields)
    if not ntype:
        ntype = fields.get("通知类型") or "汇报信"
        if not ntype.endswith("转达"):
            ntype += "转达"
    cref = fields.get("客户案号") or "请提供"
    oref = fields.get("代理所案号") or ""
    name = f"{issue}-{ntype}（委托方案号：{cref}；代理所案号：{oref}）"
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", name).strip()


def _build_mime(subject, html_body, pdf_bytes, pdf_filename, extra_attachments=None,
                from_addr="", to_addrs=None, cc_addrs=None):
    """构建 MIMEMultipart 邮件对象（HTML 正文 + 汇报信 PDF + 官文/上传附件）。
    返回 MIMEMultipart——SMTP 发送时直接 .as_string()，写 .eml 文件时 .as_bytes()。
    extra_attachments: 相对 OUTPUT_DIR 的路径列表，如 ['20651-0129CM00/source/通知书.pdf']"""
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = from_addr or ""
    msg["To"] = ", ".join(to_addrs) if to_addrs else ""
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html_body or "", "html", "utf-8"))
    msg.attach(alt)
    # 汇报信 PDF（html2pdf 生成的）
    if pdf_bytes:
        part = MIMEApplication(pdf_bytes, _subtype="pdf")
        part.add_header("Content-Disposition", "attachment", filename=pdf_filename)
        msg.attach(part)
    # 官文和手动上传的附件：按文件名设置 MIME 类型，压缩包不能标成 PDF。
    for rel in (extra_attachments or []):
        try:
            full = OUTPUT_DIR / rel
            if not full.is_file():
                print(f"[eml] 官文附件不存在，跳过: {rel}", file=sys.stderr)
                continue
            content = full.read_bytes()
            mime_type = mimetypes.guess_type(full.name)[0] or "application/octet-stream"
            maintype, subtype = mime_type.split("/", 1)
            part = MIMEBase(maintype, subtype)
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=full.name)
            msg.attach(part)
        except Exception as e:
            print(f"[eml] 附加附件失败 {rel}: {e}", file=sys.stderr)
    return msg


# ─── SMTP 发送 ───────────────────────────────────────────

def _load_email_config():
    """读 email_config.json。"""
    if not EMAIL_CONFIG_PATH.is_file():
        raise FileNotFoundError(f"email_config.json not found at {EMAIL_CONFIG_PATH}")
    return json.loads(EMAIL_CONFIG_PATH.read_text(encoding="utf-8"))


# ─── 发送人身份（七星天 / 众慧）─────────────────────────────
# 代码内置身份表；实际 SMTP 凭据从 email_config.json 的 senders.{key} 取（gitignore）。
SENDER_PROFILES = {
    "qxt":  {"label": "七星天", "from": "report@metis-ip.com"},
    "zhyc": {"label": "众慧",   "from": "report_zhyc@zhycip.com"},
}


def _default_sender_key(project):
    """代理所案号含 -H → 众慧(zhyc)，否则七星天(qxt)。"""
    return "zhyc" if "-H" in (project or "").upper() else "qxt"


def _sender_configured(scfg):
    """senders.{key} 是否已填好可用凭据（以 smtp_host 是否填写为准）。"""
    host = (scfg or {}).get("smtp_host", "")
    return bool(host) and not str(host).startswith("请填写")


def _resolve_sender(cfg, key):
    """按 key 解析发送账号。返回 (send_cfg, from_addr)。
    未配凭据时 send_cfg 为 None，调用方据此报错。"""
    prof = SENDER_PROFILES.get(key) or SENDER_PROFILES["qxt"]
    from_addr = prof["from"]
    scfg = (cfg.get("senders") or {}).get(key) or {}
    if not _sender_configured(scfg):
        return None, from_addr
    scfg = dict(scfg)
    scfg.setdefault("user", from_addr)   # From 与登录账号一致
    return scfg, from_addr


def _sender_options(cfg):
    """给前端下拉：每个发送人 key/label/from/configured。"""
    senders = cfg.get("senders") or {}
    return [
        {"key": key, "label": prof["label"], "from": prof["from"],
         "configured": _sender_configured(senders.get(key) or {})}
        for key, prof in SENDER_PROFILES.items()
    ]


def _get_smtp_oauth2_token(account_cfg):
    """获取 SMTP 用的 OAuth2 token。"""
    oauth = account_cfg.get("oauth2", {})
    if not oauth.get("enabled"):
        return None
    try:
        resp = requests.post(oauth["token_url"], data={
            "client_id": oauth["client_id"],
            "client_secret": oauth["client_secret"],
            "resource": oauth["resource"],
            "username": account_cfg["user"],
            "password": account_cfg["password"],
            "grant_type": "password",
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        data = resp.json()
        if "access_token" in data:
            return data["access_token"]
        print(f"SMTP OAuth2 获取 token 失败: {data.get('error_description', data)}", file=sys.stderr)
    except Exception as e:
        print(f"SMTP OAuth2 请求失败: {e}", file=sys.stderr)
    return None


def _normalize_mailboxes(values):
    """把页面输入的「姓名 <邮箱>」规范为邮件头地址及纯邮箱信封地址。"""
    headers, envelopes = [], []
    for value in values or []:
        raw = str(value or "").strip()
        if not raw:
            continue
        parsed = getaddresses([raw])
        if len(parsed) != 1:
            raise ValueError(f"收件地址格式无效: {raw}")
        name, addr = parsed[0]
        addr = addr.strip()
        if not _EMAIL_RE.fullmatch(addr):
            raise ValueError(f"收件地址格式无效: {raw}")
        headers.append(formataddr((name.strip(), addr)) if name.strip() else addr)
        envelopes.append(addr)
    return headers, envelopes


def _send_smtp(msg, account_cfg, recipients, cc_addrs=None):
    """通过 SMTP 发送 MIMEMultipart 邮件。OAuth2 优先，失败降级密码。失败抛异常。"""
    to_headers, to_envelopes = _normalize_mailboxes(recipients)
    cc_headers, cc_envelopes = _normalize_mailboxes(cc_addrs)
    if not to_envelopes:
        raise ValueError("请填写有效收件人邮箱")
    smtp = smtplib.SMTP(account_cfg["smtp_host"], account_cfg["smtp_port"], timeout=30)
    try:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        token = _get_smtp_oauth2_token(account_cfg)
        if token:
            auth_string = f"user={account_cfg['user']}\x01auth=Bearer {token}\x01\x01"
            try:
                smtp.docmd("AUTH", "XOAUTH2 " + base64.b64encode(auth_string.encode()).decode())
            except smtplib.SMTPAuthenticationError:
                print("[SMTP] OAuth2 认证失败，降级到密码认证", file=sys.stderr)
                smtp.login(account_cfg["user"], account_cfg["password"])
        else:
            smtp.login(account_cfg["user"], account_cfg["password"])

        # MIMEMultipart 的 __setitem__ 是 append，必须先 del 再设
        if msg["From"]: del msg["From"]
        if msg["To"]:   del msg["To"]
        if msg["Cc"]:   del msg["Cc"]
        msg["From"] = account_cfg["user"]
        msg["To"] = ", ".join(to_headers)
        if cc_headers:
            msg["Cc"] = ", ".join(cc_headers)
        smtp.sendmail(account_cfg["user"], to_envelopes + cc_envelopes, msg.as_string())
    finally:
        try:
            smtp.quit()
        except Exception:
            pass


class ConfirmReq(BaseModel):
    reviewer: str = ""
    fields: dict | None = None       # 可选：和 save 合并提交
    attach_pdf: bool | None = None   # 可选：审核人覆盖默认 attach_pdf
    html_body: str | None = None     # 邮件正文 HTML（前端渲染好的干净版）
    pdf_base64: str | None = None    # 浏览器生成的 PDF（base64），仅 attach_pdf=1 时有
    mail_from: str | None = None     # 发送人 key（qxt/zhyc），空则按代理所案号 -H 规则
    mail_to: list[str] | None = None # 收件人（客户邮箱），弹窗手填
    mail_cc: list[str] | None = None # 抄送
    subject: str | None = None       # 主题（弹窗可自定义编辑，空则用默认规则）
    source_attachments: list[str] | None = None  # 勾选要附的官文(相对路径)；None=全带


class PreviewSendReq(BaseModel):
    fields: dict
    attach_pdf: bool = True


@app.post("/api/tasks/{task_id}/preview-send")
def preview_send(task_id: str, req: PreviewSendReq):
    """发送前的预览：返回 from/recipients/subject/附件清单，供 modal 显示。"""
    rows = execute_params("SELECT template, source_attachments FROM report_tasks WHERE id = %s", (task_id,))
    template = rows[0].get("template") if rows else None
    base = _safe_filename(req.fields, template) or task_id
    subject = f"Privileged & Confidential-{base}"

    # 官文附件清单（PDF、压缩包等）
    source_attachments = []
    if rows and rows[0].get("source_attachments"):
        try:
            source_attachments = json.loads(rows[0]["source_attachments"])
        except Exception:
            pass

    # 发送人：按代理所案号 -H 规则算默认，前端可在弹窗改
    project = req.fields.get("代理所案号", "")
    try:
        cfg = _load_email_config()
        senders = _sender_options(cfg)
        default_sender = _default_sender_key(project)
    except Exception as e:
        raise HTTPException(500, f"读 email_config.json 失败: {e}")

    # 收件人/抄送：按案号从 report_recipient 查（族号前10优先→客户号前5回退，IPEasy 兜底）
    recipients, cc = [], []
    try:
        from enrich_report import query_case_recipients
        _fmt = lambda c: (f'{c["name"].strip()} <{c["email"]}>' if (c.get("name") or "").strip() else c["email"])
        rc = query_case_recipients(project)   # {"to":[...], "cc":[...]}
        recipients = [_fmt(c) for c in rc.get("to", [])]
        cc = [_fmt(c) for c in rc.get("cc", [])]
    except Exception as e:
        print(f"[preview-send] 查收件人失败 {project}: {e}", file=sys.stderr)

    return {
        "senders": senders,               # [{key,label,from,configured}]
        "default_sender": default_sender, # 按 -H 预选
        "recipients": recipients,         # 按案号自动带出(收件人)，弹窗可改
        "cc": cc,                          # 抄送(report_recipient 的 cc)，弹窗可改
        "subject": subject,
        "report_pdf_filename": (base + ".pdf") if req.attach_pdf else None,
        "source_attachments": [{"path": rel, "filename": rel.rsplit("/", 1)[-1]} for rel in source_attachments],
        "manual_attachments": [{"path": a["path"], "filename": a["name"]} for a in _report_manual_attachments(task_id)],
    }


@app.post("/api/tasks/{task_id}/confirm")
def confirm_task(task_id: str, req: ConfirmReq):
    # 1) 先保存审核人改过的字段/勾选（无论后续是否发送成功都要保存），但不改 status
    sets = []
    params = []
    if req.fields is not None:
        sets.append("fields_json = %s")
        params.append(json.dumps(req.fields, ensure_ascii=False))
    if req.attach_pdf is not None:
        sets.append("attach_pdf = %s")
        params.append(1 if req.attach_pdf else 0)
    if sets:
        params.append(task_id)
        execute_params(f"UPDATE report_tasks SET {', '.join(sets)} WHERE id = %s", tuple(params))

    # 2) 生成产出物（.eml + 可选 PDF），按 output/{代理所案号}/ 归类
    fields = req.fields or {}
    sa_rows = execute_params("SELECT template, source_attachments FROM report_tasks WHERE id = %s", (task_id,))
    template = sa_rows[0].get("template") if sa_rows else None
    base = _safe_filename(fields, template) or task_id
    project = fields.get("代理所案号") or task_id
    case_dir = OUTPUT_DIR / re.sub(r'[\\/:*?"<>|\r\n]', "_", project).strip()
    out = {"task_id": task_id}

    # 查官文附件路径
    source_attachments = []
    if sa_rows and sa_rows[0].get("source_attachments"):
        try:
            source_attachments = json.loads(sa_rows[0]["source_attachments"])
        except Exception:
            pass
    # 官文附件 + 手动上传附件；按弹窗勾选过滤（未传=全带；只保留已登记路径）
    manual_paths = [a["path"] for a in _report_manual_attachments(task_id)]
    all_atts = source_attachments + manual_paths
    if req.source_attachments is not None:
        sel = set(req.source_attachments)
        source_attachments = [p for p in all_atts if p in sel]
    else:
        source_attachments = all_atts

    pdf_bytes = None
    pdf_filename = None
    if req.pdf_base64:
        try:
            pdf_bytes = base64.b64decode(req.pdf_base64)
            pdf_filename = base + ".pdf"
            case_dir.mkdir(parents=True, exist_ok=True)
            (case_dir / pdf_filename).write_bytes(pdf_bytes)
            out["pdf"] = f"output/{project}/{pdf_filename}"
        except Exception as e:
            print(f"[confirm] PDF 保存失败 {task_id}: {e}", file=sys.stderr)

    # 3) 构 MIME，写 .eml 备份（主题：弹窗自定义优先，否则默认规则）
    subject = (req.subject or "").strip() or f"Privileged & Confidential-{base}"
    mime_msg = None
    if req.html_body is not None:
        try:
            mime_msg = _build_mime(subject, req.html_body, pdf_bytes, pdf_filename,
                                   extra_attachments=source_attachments)
            case_dir.mkdir(parents=True, exist_ok=True)
            (case_dir / (base + ".eml")).write_bytes(mime_msg.as_bytes())
            out["eml"] = f"output/{project}/{base}.eml"
        except Exception as e:
            print(f"[confirm] .eml 生成失败 {task_id}: {e}", file=sys.stderr)

    # 4) SMTP 发送：成功才改 status='done'；失败保留 pending 等重试
    if mime_msg is None:
        out["ok"] = False
        out["status"] = "pending"
        out["error"] = "邮件正文为空，无法发送"
        return out

    try:
        cfg = _load_email_config()

        # 发送人：弹窗选的优先，否则按代理所案号 -H 规则
        sender_key = req.mail_from or _default_sender_key(project)
        send_cfg, from_addr = _resolve_sender(cfg, sender_key)

        # 收件人/抄送：弹窗手填（去空白、去空项）
        recipients = [a.strip() for a in (req.mail_to or []) if a and a.strip()]
        cc_addrs = [a.strip() for a in (req.mail_cc or []) if a and a.strip()]

        if not recipients:
            raise RuntimeError("请填写收件人")
        if not send_cfg:
            label = SENDER_PROFILES.get(sender_key, {}).get("label", sender_key)
            raise RuntimeError(
                f"发送人「{label} {from_addr}」未配置 SMTP 凭据"
                f"（email_config.json → senders.{sender_key}），凭据到位后即可发送")

        _send_smtp(mime_msg, send_cfg, recipients, cc_addrs)

        # 发送成功才更新 status
        execute_params(
            "UPDATE report_tasks SET status = 'done', reviewer = %s WHERE id = %s",
            (req.reviewer or None, task_id),
        )
        out["ok"] = True
        out["status"] = "done"
        out["sent_to"] = recipients
        out["sent_from"] = from_addr
        print(f"[confirm] 已发送 task={task_id} → {recipients}", file=sys.stderr)
    except Exception as e:
        # 发送失败：status 保留 pending；PDF/.eml 已存在 output/ 作为备份，可重试
        out["ok"] = False
        out["status"] = "pending"
        out["error"] = f"SMTP 发送失败: {e}"
        print(f"[confirm] SMTP 发送失败 task={task_id}: {e}", file=sys.stderr)

    return out


# ─── 跳过 ────────────────────────────────────────────────

@app.post("/api/tasks/{task_id}/skip")
def skip_task(task_id: str):
    execute_params(
        "UPDATE report_tasks SET status = 'skipped' WHERE id = %s",
        (task_id,),
    )
    return {"ok": True, "task_id": task_id, "status": "skipped"}


# ─── 手动上传附件（随汇报信一起发给客户）────────────────────

def _report_manual_dir(task_id: str) -> Path:
    """审核人手动上传的汇报信附件目录（output/_manual/{task_id}/）。"""
    return OUTPUT_DIR / "_manual" / re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", task_id)


def _report_manual_attachments(task_id: str):
    """手动上传附件的相对 OUTPUT_DIR 路径列表 [{name,path}]（供弹窗展示与 _build_mime）。"""
    d = _report_manual_dir(task_id)
    out = []
    if d.is_dir():
        tid = d.name
        for p in sorted(d.iterdir()):
            if p.is_file():
                out.append({"name": p.name, "path": f"_manual/{tid}/{p.name}"})
    return out


@app.post("/api/tasks/{task_id}/upload-attachment")
def upload_report_attachment(task_id: str, file: UploadFile = File(...)):
    """审核人手动上传附件（存 output/_manual/{task_id}/，发汇报信时一并附上）。"""
    dest_dir = _report_manual_dir(task_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", file.filename or "upload.bin").strip() or "upload.bin"
    (dest_dir / name).write_bytes(file.file.read())
    return {"ok": True, "name": name}


@app.get("/api/tasks/{task_id}/attachments")
def list_report_attachments(task_id: str):
    """列手动上传的附件。"""
    return {"attachments": _report_manual_attachments(task_id)}


@app.delete("/api/tasks/{task_id}/attachment/{name}")
def delete_report_attachment(task_id: str, name: str):
    """删除手动上传的附件。"""
    safe = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", name)
    p = _report_manual_dir(task_id) / safe
    if p.is_file():
        p.unlink()
    return {"ok": True, "name": safe}


if __name__ == "__main__":
    print(f"启动汇报信审核服务: http://localhost:8501", file=sys.stderr)
    print(f"  - 模板目录: {TEMPLATES_DIR}", file=sys.stderr)
    print(f"  - 审核页:   {PROTOTYPE_HTML}", file=sys.stderr)
    uvicorn.run(app, host="0.0.0.0", port=8501)
