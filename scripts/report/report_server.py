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

US 递交在线审核（/submission 路由组，表 submission_tasks）:
  GET  /submission/review/{task_id}          审核页（web/submission.html）
  GET  /api/submission/tasks                 任务列表 ?type=&status=
  GET  /api/submission/tasks/{task_id}       fields_json + missing_json（含 subject_matter 推断）
  POST /api/submission/tasks/{task_id}/save  UPDATE fields_json
  POST /api/submission/tasks/{task_id}/preview  生成文档+PDF预览 ?target=confirmation|assignment|declaration
  POST /api/submission/tasks/{task_id}/preview-send  硬校验+生成三件成品+返回发送清单（modal用）
  POST /api/submission/tasks/{task_id}/confirm  发送成品邮件 → done + 插 signature_followup
  POST /api/submission/tasks/{task_id}/skip  UPDATE status='skipped'
  POST /api/submission/tasks/{task_id}/reopen  done→pending 退回重编（客户已签须 force）

环节4 准备递交文件（task_type='filing_preparation'）相关：
  POST /api/submission/filing/create         手动转入（按案号从 filing_confirmation 建 filing_preparation）
  GET  /api/submission/signatures            待回签列表（signature_followup pending，附 transferred 标记）
  POST /api/submission/signatures/{id}/mark-signed  「已收到签署」→ 置 done 并立即转入递交准备
  POST /api/submission/filing/auto-transfer  cron：扫已回签且未转入的案件批量建 filing_preparation
"""
import json
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
from email.utils import getaddresses

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


WEB_DIR = ROOT / "web"
PROTOTYPE_HTML = WEB_DIR / "prototype.html"
TEMPLATES_PREVIEW_HTML = WEB_DIR / "templates_preview.html"
EMAIL_CONFIG_PATH = SCRIPT_DIR / "email_config.json"
QA_SEED_STATE_PATH = SCRIPT_DIR / "qa_seed_state.json"   # QA 播种全局开关（默认开）

sys.path.insert(0, str(SCRIPT_DIR))
from db_query import execute_params  # noqa: E402
from submission.common import infer_subject_matter, normalize_parents, validate_for_confirm, parse_address_en  # noqa: E402
from submission.email_modules import build_email_modules  # noqa: E402
from submission.confirmation_sheet import generate_confirmation_sheet, list_confirmation_rows  # noqa: E402
from submission.assignment_generator import generate_assignments  # noqa: E402
from submission.declaration_generator import generate_declarations  # noqa: E402
from submission.preview import docx_to_pdf, office_convert  # noqa: E402
# 环节4（递交文件）生成器 —— 与环节2 互不影响
from submission.fields_mapping import fields_to_case_info, load_agent_info  # noqa: E402
from submission.poa_generator import generate_poa, generate_poas  # noqa: E402
from submission.transmittal_generator import generate_transmittal  # noqa: E402
from submission.ads_generator import generate_ads, generate_ads_preview, generate_ads_flat  # noqa: E402
from submission.agent_email import build_agent_email  # noqa: E402
from submission import docusign_client as _docusign  # noqa: E402（仅 requests 依赖，安全 import）

SUBMISSION_HTML = WEB_DIR / "submission.html"
FILING_HTML = WEB_DIR / "filing.html"


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

# US 递交预览/成品输出目录（挂载在 /output 下，PDF 可直接 URL 访问）
SUBMISSION_OUTPUT_DIR = _OUTPUT_DIR_FOR_MOUNT / "submission"

# 原始文档预览目录：审核服务（Windows）读 P:\confirmation-intake\<案号>\（P: 已映射到原始材料盘）。
# 写死 P:\confirmation-intake\；挂载容错——非 Windows/盘未映射时跳过挂载、原始页暂不可用，服务不崩。
SOURCE_DOC_DIR = Path("P:\\confirmation-intake")
try:
    SOURCE_DOC_DIR.mkdir(parents=True, exist_ok=True)
except Exception as _e:  # noqa: BLE001
    print(f"[source-docs] 目录不可用 {SOURCE_DOC_DIR}: {_e}", file=sys.stderr)
if SOURCE_DOC_DIR.exists():
    app.mount("/source-docs", StaticFiles(directory=str(SOURCE_DOC_DIR)), name="source-docs")
else:
    print(f"[source-docs] {SOURCE_DOC_DIR} 不存在，原始页预览暂不可用（挂载跳过）", file=sys.stderr)


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
        SELECT t.id, t.status, t.fields_json, t.reviewer,
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
        items.append({
            "id": r["id"],
            "status": r["status"],
            "project": r.get("p_project") or fj.get("代理所案号", ""),
            "ntype":   fj.get("通知类型", ""),
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
        SELECT t.id, t.template, t.attach_pdf, t.fields_json, t.source_attachments, t.status, t.reviewer,
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
            enriched = enrich_cn_fields(project)
            customer_demands = query_customer_demands(project)
            interface_contacts = query_case_interface(project)
        except Exception as e:
            print(f"[warn] task {task_id} enrich 失败: {e}", file=sys.stderr)

    # 合并优先级（低→高）：projects 默认 < enrich 主数据 < fields_json（审核人改过的最优先）
    # 注：fields_json 里值为 ""/None 的是占位，不应覆盖 enrich 查到的真实值
    effective_user = {k: v for k, v in user_fields.items() if v not in ("", None)}
    merged = {**p_defaults, **enriched, **effective_user}

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
    """返回 templates/md/{name} 原文。"""
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(400, "invalid template name")
    p = _resolve_template(name)
    if not p:
        raise HTTPException(404, f"template {name} not found")
    return PlainTextResponse(p.read_text(encoding="utf-8"), media_type="text/plain; charset=utf-8")


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
    p = _resolve_template(template)
    if not p:
        return None
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
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
    """构建 MIMEMultipart 邮件对象（HTML 正文 + 汇报信 PDF + 官文 PDF 附件）。
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
    # 官文 PDF 附件
    for rel in (extra_attachments or []):
        try:
            full = OUTPUT_DIR / rel
            if not full.is_file():
                print(f"[eml] 官文附件不存在，跳过: {rel}", file=sys.stderr)
                continue
            content = full.read_bytes()
            part = MIMEApplication(content, _subtype="pdf")
            part.add_header("Content-Disposition", "attachment", filename=full.name)
            msg.attach(part)
        except Exception as e:
            print(f"[eml] 附加官文 PDF 失败 {rel}: {e}", file=sys.stderr)
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


def _send_smtp(msg, account_cfg, recipients, cc_addrs=None):
    """通过 SMTP 发送 MIMEMultipart 邮件。OAuth2 优先，失败降级密码。失败抛异常。"""
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
        msg["To"] = ", ".join(recipients)            # 可含「姓名 <邮箱>」
        if cc_addrs:
            msg["Cc"] = ", ".join(cc_addrs)
        # 信封收件人只要纯邮箱：从「姓名 <邮箱>」解析出地址
        all_rcpts = [addr for _, addr in getaddresses(recipients + (cc_addrs or [])) if addr]
        smtp.sendmail(account_cfg["user"], all_rcpts, msg.as_string())
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

    # 官文 PDF 清单
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

    # 收件人：按案号从 IPEasy 查客户联系人（在职、有邮箱，全取），格式化为「姓名 <邮箱>」
    recipients = []
    try:
        from enrich_report import query_case_recipients
        recipients = [
            (f'{c["name"]} <{c["email"]}>' if c.get("name") else c["email"])
            for c in query_case_recipients(project)
        ]
    except Exception as e:
        print(f"[preview-send] 查收件人失败 {project}: {e}", file=sys.stderr)

    return {
        "senders": senders,               # [{key,label,from,configured}]
        "default_sender": default_sender, # 按 -H 预选
        "recipients": recipients,         # 按案号自动带出，弹窗可改
        "cc": [],                         # 抄送默认空，弹窗手填
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

    # 查官文 PDF 附件路径
    source_attachments = []
    if sa_rows and sa_rows[0].get("source_attachments"):
        try:
            source_attachments = json.loads(sa_rows[0]["source_attachments"])
        except Exception:
            pass
    # 官文 PDF + 手动上传附件；按弹窗勾选过滤（未传=全带；只保留确有的，防越权附任意路径）
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


# ═══ US 递交在线审核（/submission 路由组，表 submission_tasks）═══
# 设计见 us_submission/在线审核与文件生成方案.md；任务由 VPS skill 写入（pending），
# 此处提供审核页数据层。preview/confirm 在后续子任务实现。


def _load_submission_task(task_id: str) -> dict:
    rows = execute_params(
        "SELECT id, task_type, case_volume, fields_json, missing_json, source_mail, "
        "contact_email, filer_email, status, created_at, updated_at, confirmed_at "
        "FROM submission_tasks WHERE id = %s",
        (task_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    return rows[0]


@app.get("/submission/review/{task_id}")
def submission_review_page(task_id: str):
    if not SUBMISSION_HTML.exists():
        return PlainTextResponse(
            f"审核页前端尚未部署（web/submission.html 缺失）。任务ID: {task_id}\n"
            f"可先用 GET /api/submission/tasks/{task_id} 查看数据。",
            status_code=503,
        )
    return FileResponse(str(SUBMISSION_HTML))


@app.get("/api/submission/tasks")
def list_submission_tasks(type: str = "filing_confirmation", status: str = "pending,skipped,done"):
    statuses = [s.strip() for s in status.split(",") if s.strip()]
    placeholders = ",".join(["%s"] * len(statuses))
    rows = execute_params(
        f"SELECT id, task_type, case_volume, contact_email, status, created_at, updated_at "
        f"FROM submission_tasks WHERE task_type = %s AND status IN ({placeholders}) "
        f"ORDER BY created_at DESC",
        tuple([type] + statuses),
    )
    for row in rows:
        for key in ("created_at", "updated_at"):
            if row.get(key) is not None:
                row[key] = str(row[key])
    return {"tasks": rows}


@app.get("/api/submission/tasks/{task_id}")
def get_submission_task(task_id: str):
    row = _load_submission_task(task_id)
    try:
        fields = json.loads(row["fields_json"]) if row["fields_json"] else {}
    except Exception:
        raise HTTPException(status_code=500, detail="fields_json 不是合法 JSON")
    try:
        missing = json.loads(row["missing_json"]) if row["missing_json"] else []
    except Exception:
        missing = []

    # QA 埋点：首次打开确认函页时播种（AI 造 0~3 处错、就地改 fields 为 B、B 落库+种子入表）。best-effort
    _qa_seed_on_open(task_id, row, fields)

    # server 侧推断 subject_matter（来源3，审核页可改；save 后以 fields_json 为准）
    fields["subject_matter"] = infer_subject_matter(fields)
    normalize_parents(fields)  # 兼容存量任务的小写母案键

    return {
        "id": row["id"],
        "task_type": row["task_type"],
        "case_volume": row["case_volume"],
        "fields_json": fields,
        "missing_json": missing,
        "source_mail": row["source_mail"],
        "contact_email": row["contact_email"],
        "filer_email": row.get("filer_email") or "",   # 递交人邮箱（环节5/6 用；确认页可手填）
        "status": row["status"],
        "created_at": str(row["created_at"]) if row["created_at"] else None,
        "updated_at": str(row["updated_at"]) if row["updated_at"] else None,
        "confirmed_at": str(row["confirmed_at"]) if row["confirmed_at"] else None,
    }


# 原始文档预览：可直接内联的扩展名 / Markdown / CSV / 需 LibreOffice 转 PDF 的 Office 文档
_INLINE_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".txt", ".html", ".htm"}
_MD_EXT = {".md", ".markdown"}
_CSV_EXT = {".csv", ".tsv"}
_WORD_EXT = {".doc", ".docx", ".rtf", ".odt"}   # LibreOffice 转 PDF 内联预览
_SHEET_EXT = {".xlsx", ".xls", ".ods"}          # LibreOffice 转 HTML（保留表格，效果优于 PDF）
# LibreOffice 转换产物的缓存目录（在 /output 下，可直接 URL 访问）
_SOURCE_PREVIEW_DIR = SUBMISSION_OUTPUT_DIR / "source_preview"


def _source_doc_preview(case_volume: str, f: Path):
    """返回 (preview_url, kind)：
      kind="inline"   → preview_url 直接嵌 iframe（PDF/图片/txt/html；Word→PDF、Excel→HTML）
      kind="markdown" → preview_url 指向原始 .md 文本，前端用 marked 渲染
      kind="csv"      → preview_url 指向原始 csv/tsv 文本，前端解析成表格
      kind="none"     → 不可预览，preview_url=None（前端给下载链接）"""
    ext = f.suffix.lower()
    if ext in _MD_EXT:
        return f"/source-docs/{quote(case_volume)}/{quote(f.name)}", "markdown"
    if ext in _CSV_EXT:
        return f"/source-docs/{quote(case_volume)}/{quote(f.name)}", "csv"
    if ext in _INLINE_EXT:
        return f"/source-docs/{quote(case_volume)}/{quote(f.name)}", "inline"
    if ext in _WORD_EXT or ext in _SHEET_EXT:
        # 表格转 HTML（保留多 sheet/表格结构），其余 Office 文档转 PDF
        to_fmt, out_ext = ("html", ".html") if ext in _SHEET_EXT else ("pdf", ".pdf")
        try:
            cache_dir = _SOURCE_PREVIEW_DIR / case_volume
            out = cache_dir / (f.stem + out_ext)
            if not out.exists() or out.stat().st_mtime < f.stat().st_mtime:
                if ext in _SHEET_EXT:
                    office_convert(f, "html", out_dir=cache_dir)
                else:
                    docx_to_pdf(f, out_dir=cache_dir)
            rel = out.relative_to(_OUTPUT_DIR_FOR_MOUNT)
            return "/output/" + "/".join(quote(p) for p in rel.parts), "inline"
        except Exception as e:
            print(f"[source-doc] Office→{to_fmt} 预览失败 {f.name}: {e}", file=sys.stderr)
            return None, "none"
    return None, "none"


# 参考文件里不展示的流水线内部文件（邮件正文/元数据/抽取结果等）
_SOURCE_DOC_HIDDEN = {"body.txt", "email_meta.json", "extracted_fields.json", "result.json"}


@app.get("/api/submission/tasks/{task_id}/source-docs")
def get_submission_source_docs(task_id: str):
    """原始文档列表：系统最初提取数据写入 IPEasy 的源文件（NAS），供审核人对照核对著录项目。
    测试期从 SOURCE_DOC_DIR/<case_volume>/ 读取；NAS 挂载后改环境变量 SOURCE_DOC_DIR 即可。
    每个文件返回 url（原件下载）+ preview_url（可内联预览的 URL，Word 已转 PDF；不可预览为 null）。"""
    row = _load_submission_task(task_id)
    case_volume = (row.get("case_volume") or "").strip()
    docs = []
    if case_volume:
        case_dir = SOURCE_DOC_DIR / case_volume
        if case_dir.is_dir():
            for f in sorted(case_dir.iterdir()):
                if f.is_file() and not f.name.startswith(".") and f.name.lower() not in _SOURCE_DOC_HIDDEN:
                    preview_url, kind = _source_doc_preview(case_volume, f)
                    docs.append({
                        "filename": f.name,
                        "url": f"/source-docs/{quote(case_volume)}/{quote(f.name)}",
                        "preview_url": preview_url,
                        "kind": kind,
                    })
    return {"case_volume": case_volume, "docs": docs}


def _safe_source_doc(case_volume: str, name: str) -> Path:
    """校验参考文件名（禁路径穿越/空/. ..），返回 SOURCE_DOC_DIR/<案号>/<name>。"""
    base = (name or "").strip()
    if not case_volume or not base or base != Path(base).name or base in (".", ".."):
        raise HTTPException(400, f"非法文件名：{name!r}")
    return SOURCE_DOC_DIR / case_volume / base


@app.post("/api/submission/tasks/{task_id}/source-doc/upload")
def upload_submission_source_doc(task_id: str, file: UploadFile = File(...)):
    """上传参考文件到 P:\\confirmation-intake\\<案号>\\（同名覆盖）。
    供审核人在确认函页删掉邮箱读来的错误参考文件后、上传正确的。"""
    row = _load_submission_task(task_id)
    dest = _safe_source_doc((row.get("case_volume") or "").strip(), Path(file.filename or "").name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(file.file.read())
    return {"ok": True, "name": dest.name}


@app.post("/api/submission/tasks/{task_id}/source-doc/delete")
def delete_submission_source_doc(task_id: str, name: str):
    """删除该案某个参考文件（P:\\confirmation-intake\\<案号>\\<name>）。
    用 POST（而非 DELETE 方法），避免部分代理/服务器拦 DELETE 导致前端 fetch 被拒。"""
    row = _load_submission_task(task_id)
    p = _safe_source_doc((row.get("case_volume") or "").strip(), name)
    if p.is_file():
        p.unlink()
    return {"ok": True, "name": p.name}


class SubmissionSaveReq(BaseModel):
    fields_json: dict
    contact_email: str = ""
    filer_email: str = None       # 递交人邮箱；None=不改，""=清空，值=更新


def _uppercase_applicant_names(fields: dict) -> None:
    """申请人英文名统一转大写（就地改 fields，落库即大写）。"""
    for a in (fields.get("applicants") or []):
        if isinstance(a, dict) and a.get("applicant_name_en"):
            a["applicant_name_en"] = str(a["applicant_name_en"]).upper()


@app.post("/api/submission/tasks/{task_id}/save")
def save_submission_task(task_id: str, req: SubmissionSaveReq):
    row = _load_submission_task(task_id)
    if row["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"任务状态为 {row['status']}，不可编辑")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _uppercase_applicant_names(req.fields_json)   # 申请人英文名落库即大写
    contact_email = req.contact_email.strip() or row["contact_email"]
    # filer_email：None=保留原值，否则更新（含清空）
    filer_email = row.get("filer_email") if req.filer_email is None else req.filer_email.strip()
    execute_params(
        "UPDATE submission_tasks SET fields_json = %s, contact_email = %s, filer_email = %s, "
        "updated_at = %s WHERE id = %s",
        (json.dumps(req.fields_json, ensure_ascii=False), contact_email, filer_email, now, task_id),
    )
    return {"ok": True, "task_id": task_id, "updated_at": now}


class ParseAddressReq(BaseModel):
    raw: str = ""


@app.post("/api/submission/parse-address")
def parse_address(req: ParseAddressReq):
    """把一整串英文地址启发式拆成结构化字段（供转让方公司地址「粘贴完整地址→识别填充」；结果需人工复核）。"""
    return parse_address_en(req.raw or "")


class SubmissionPreviewReq(BaseModel):
    # 可选传入页面当前编辑值（不落库，预览所见即所改）；缺省用库中 fields_json
    fields_json: dict = None
    target: str = "confirmation"  # confirmation / assignment / declaration


@app.post("/api/submission/tasks/{task_id}/preview")
def preview_submission_task(task_id: str, req: SubmissionPreviewReq):
    row = _load_submission_task(task_id)
    if req.fields_json is not None:
        fields = req.fields_json
    else:
        try:
            fields = json.loads(row["fields_json"]) if row["fields_json"] else {}
        except Exception:
            raise HTTPException(status_code=500, detail="fields_json 不是合法 JSON")
    fields["subject_matter"] = infer_subject_matter(fields)
    normalize_parents(fields)

    preview_dir = SUBMISSION_OUTPUT_DIR / task_id / "preview"
    files, missing_fields, missing_optional, warnings, rows = [], [], [], [], []

    def _url(path) -> str:
        return "/output/" + str(Path(path).relative_to(_OUTPUT_DIR_FOR_MOUNT))

    try:
        if req.target == "confirmation":
            result = generate_confirmation_sheet(fields, preview_dir)
            missing_fields = result["missing_fields"]
            missing_optional = result["missing_optional_fields"]
            rows = result.get("rows", [])   # 各行 key/标签/值，供审核页「标黄设置」勾选
            pdf_path = docx_to_pdf(result["file_path"], preview_dir)
            files.append({"name": result["file_name"], "pdf_url": _url(pdf_path),
                          "docx_url": _url(result["file_path"])})
        elif req.target == "assignment":
            for item in generate_assignments(fields, preview_dir):
                warnings.extend(item.get("warnings") or [])
                pdf_path = docx_to_pdf(item["file_path"], preview_dir)
                files.append({"name": item["file_name"], "pdf_url": _url(pdf_path),
                              "docx_url": _url(item["file_path"])})
        elif req.target == "declaration":
            for item in generate_declarations(fields, preview_dir):
                files.append({"name": item["file_name"], "pdf_url": _url(item["file_path"]),
                              "docx_url": None})
        else:
            raise HTTPException(status_code=400, detail=f"未知 target: {req.target}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"预览生成失败：{exc}")

    return {
        "target": req.target,
        "files": files,
        "missing_fields": missing_fields,
        "missing_optional_fields": missing_optional,
        "warnings": warnings,
        "rows": rows,   # confirmation 时非空：[{key,label,value}]，供「标黄设置」面板
    }


@app.post("/api/submission/tasks/{task_id}/confirmation-rows")
def confirmation_rows(task_id: str, req: SubmissionPreviewReq):
    """确认函各行清单（只算不产 PDF），供审核页「标黄设置」勾选。
    用页面当前编辑值（req.fields_json）优先，否则库中 fields_json。
    :return: {rows:[{key,label,value}], highlights:[...当前已勾选]}"""
    row = _load_submission_task(task_id)
    if req.fields_json is not None:
        fields = req.fields_json
    else:
        try:
            fields = json.loads(row["fields_json"]) if row["fields_json"] else {}
        except Exception:
            raise HTTPException(status_code=500, detail="fields_json 不是合法 JSON")
    fields["subject_matter"] = infer_subject_matter(fields)
    normalize_parents(fields)
    try:
        rows = list_confirmation_rows(fields)
    except Exception as exc:   # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"行清单生成失败：{exc}")
    return {"rows": rows, "highlights": fields.get("confirmation_highlights") or []}


def _confirmation_override(task_id: str, gen_mtime: float = 0.0):
    """确认函替换件：manual/ 里名字含「Application Information Sheet」的上传件(与发送口径一致)。
    仅当替换件**比 gen_mtime(最近一次按数据生成的预览)更新**时才采用——一旦点过「刷新预览」，
    生成版时间戳更晚，则不再显示替换件(即使重开页面，因比的是磁盘 mtime)。
    是 PDF 直接用；是 docx 则转 PDF 缓存到 preview/_ov/（不污染顶层扫描、也不进发送集）。
    :return: (pdf_path, docx_path) 或 (None, None)。"""
    manual_dir = _submission_manual_dir(task_id)
    if not manual_dir.is_dir():
        return None, None
    tk = "application information sheet"
    cands = [p for p in manual_dir.glob("*")
             if p.is_file() and tk in p.name.lower() and p.suffix.lower() in (".pdf", ".docx")]
    if not cands:
        return None, None
    cands.sort(key=lambda p: (p.suffix.lower() != ".pdf", -p.stat().st_mtime))  # pdf 优先，再取新
    src = cands[0]
    if src.stat().st_mtime <= gen_mtime:
        return None, None   # 生成版比替换件新(已点过刷新预览) → 不用替换件，回落生成版
    if src.suffix.lower() == ".pdf":
        docx = next((p for p in cands if p.suffix.lower() == ".docx"), None)
        return src, docx
    ov_dir = SUBMISSION_OUTPUT_DIR / task_id / "preview" / "_ov"
    ov_dir.mkdir(parents=True, exist_ok=True)
    out_pdf = ov_dir / (src.stem + ".pdf")
    if (not out_pdf.exists()) or out_pdf.stat().st_mtime < src.stat().st_mtime:
        docx_to_pdf(str(src), ov_dir)   # 上传的是 docx → 转 PDF 供预览
    return (out_pdf if out_pdf.exists() else None), src


@app.get("/api/submission/tasks/{task_id}/preview-existing")
def preview_existing_submission(task_id: str, target: str = "confirmation"):
    """展示已存在成品(不重生成)。确认函优先展示 manual/ 里的替换件(与发送一致)，
    无替换件再看 preview/；供页面打开时「有则直接展示、无则再 POST /preview 生成」。"""
    _load_submission_task(task_id)
    preview_dir = SUBMISSION_OUTPUT_DIR / task_id / "preview"
    token = {"confirmation": "Application Information Sheet",
             "assignment": "Assignment", "declaration": "Declaration"}.get(target, target)
    files = []
    # 确认函：替换件比"最近一次生成的预览"更新才优先展示（点过刷新预览后 → 显示生成版）
    if target == "confirmation":
        _gen_mtime = 0.0
        if preview_dir.is_dir():
            _ms = [p.stat().st_mtime for p in preview_dir.glob("*.pdf") if token.lower() in p.name.lower()]
            _gen_mtime = max(_ms) if _ms else 0.0
        ov_pdf, ov_docx = _confirmation_override(task_id, _gen_mtime)
        if ov_pdf:
            return {"target": target, "override": True,
                    "files": [{"name": ov_pdf.stem, "pdf_url": _output_url(ov_pdf),
                               "docx_url": _output_url(ov_docx) if ov_docx else None}]}
    if preview_dir.is_dir():
        cand = [p for p in preview_dir.glob("*.pdf") if token.lower() in p.name.lower()]
        # 去重（Windows 占用时 _free_output_path 追加的 -时间戳 锁后缀 / 不同日期前缀），每组取最新
        best = {}
        for p in cand:
            base = re.sub(r"-\d{6,}$", "", p.stem)
            if base not in best or p.stat().st_mtime > best[base].stat().st_mtime:
                best[base] = p
        picks = sorted(best.values(), key=lambda p: p.stat().st_mtime, reverse=True)
        # 确认函/Declaration 天然单份 → 只取最新一份（Assignment 可多份=多段转让）
        if target in ("confirmation", "declaration"):
            picks = picks[:1]
        for p in picks:
            docx = p.with_suffix(".docx")
            files.append({"name": p.stem, "pdf_url": _output_url(p),
                          "docx_url": _output_url(docx) if docx.exists() else None})
    return {"target": target, "files": files}


@app.get("/api/submission/tasks/{task_id}/final-doc")
def submission_final_doc(task_id: str, target: str):
    """已发版预览：发美代理后文件已锁定，返回 final/(发送时生成) 中匹配 target 的【已发送】
    文件 URL，不按当前编辑重生成。ADS 为动态 XFA 表单浏览器不内联 → inline=False（下载打开）。"""
    _load_submission_task(task_id)
    token = {"ads": "ADS", "poa": "POA", "transmittal": "Transmittal",
             "assignment": "Assignment", "declaration": "Declaration"}.get(target, target)
    hit = next((a for a in _submission_attachment_set(task_id)
                if token.lower() in a["filename"].lower()), None)
    if not hit:
        return {"available": False, "note": f"final/ 无匹配「{token}」的已发文件"}
    url = "/output/" + str(Path(hit["path"]).relative_to(_OUTPUT_DIR_FOR_MOUNT))
    inline = Path(hit["filename"]).suffix.lower() == ".pdf" and token != "ADS"
    return {"available": True, "name": hit["filename"], "url": url, "inline": inline}


def _submission_final_dir(task_id: str) -> Path:
    return SUBMISSION_OUTPUT_DIR / task_id / "final"


def _submission_manual_dir(task_id: str) -> Path:
    """操作员手动上传的附件目录（改后重传/额外附件）。

    与 final/ 分开存：preview-send 每次 rmtree 重建 final/，manual/ 不受影响，否则
    一点发送预览上传件就没了。发送时两边合并、manual 同名覆盖 final。"""
    return SUBMISSION_OUTPUT_DIR / task_id / "manual"


def _submission_attachment_set(task_id: str) -> list:
    """合并 final/(生成) 与 manual/(手动上传)，返回有序去重列表。

    manual 同名覆盖 final（操作员改后用原名重传即顶替生成版），保持生成件原有顺序；
    manual 独有的文件追加在后。每项：{"filename", "source", "path"}，
    source ∈ generated | manual-override | manual。"""
    items = {}  # filename -> dict（dict 保序：覆盖时位置不变）
    final_dir = _submission_final_dir(task_id)
    if final_dir.exists():
        for p in sorted(final_dir.glob("*")):
            if p.is_file():
                items[p.name] = {"filename": p.name, "source": "generated", "path": p}
    manual_dir = _submission_manual_dir(task_id)
    if manual_dir.exists():
        for p in sorted(manual_dir.glob("*")):
            if p.is_file():
                items[p.name] = {"filename": p.name, "path": p,
                                 "source": "manual-override" if p.name in items else "manual"}
    return list(items.values())


def _submission_send_config():
    """US 递交发送配置：email_config.json 的 submission 节（缺省回退 pa 账号、无抄送）。"""
    cfg = _load_email_config()
    sub = cfg.get("submission", {})
    account_key = sub.get("account", "pa")
    account_cfg = cfg.get("accounts", {}).get(account_key) or {}
    if not account_cfg:
        raise HTTPException(500, f"email_config.json 缺少 accounts.{account_key} 配置")
    return account_cfg, sub.get("cc", [])


def _filing_firm_key(agent_firm):
    """代理所名归一到发件人账号 key（Metis/Poseidon/Porus）：子串不敏感匹配，找不到返回 ''。"""
    f = (agent_firm or "").strip().lower()
    for key in ("metis", "poseidon", "porus"):
        if key in f:
            return key.capitalize()   # metis→Metis / poseidon→Poseidon / porus→Porus
    return ""


def _filing_send_config(agent_firm):
    """发美代理发信账号：按代理所 agent_firm 选 submission.firm_send_accounts 里的账号
    （Metis→patent_filling@metis-ip.com 等）；识别不出/未配 → firm_send_default，
    再兜底回退 _submission_send_config()（pa）。返回 (account_cfg, cc)。"""
    cfg = _load_email_config()
    sub = cfg.get("submission", {})
    fmap = sub.get("firm_send_accounts") or {}
    acct_key = fmap.get(_filing_firm_key(agent_firm)) or sub.get("firm_send_default")
    account_cfg = cfg.get("accounts", {}).get(acct_key) if acct_key else None
    if account_cfg:
        return account_cfg, sub.get("cc", [])
    return _submission_send_config()


class EmailModulesReq(BaseModel):
    fields_json: dict = None       # 页面当前编辑值；缺省用库中值
    params: dict = {}              # 超权费/超页费输入：claims_total / pages_total / pages_excess


@app.post("/api/submission/tasks/{task_id}/email-modules")
def email_modules_submission(task_id: str, req: EmailModulesReq):
    """确认邮件正文模块清单（审核页全部展示，审阅人勾选适用项后拼装正文）。"""
    row = _load_submission_task(task_id)
    if req.fields_json is not None:
        fields = req.fields_json
    else:
        fields = json.loads(row["fields_json"]) if row["fields_json"] else {}
    normalize_parents(fields)
    return {"modules": build_email_modules(fields, req.params or {})}


class SubmissionPreviewSendReq(BaseModel):
    fields_json: dict = None  # 页面当前编辑值；缺省用库中值


@app.post("/api/submission/tasks/{task_id}/preview-send")
def preview_send_submission(task_id: str, req: SubmissionPreviewSendReq):
    """confirm 前置：硬校验 → 生成三件成品到 final/ → 返回发送清单供 modal 确认。"""
    row = _load_submission_task(task_id)
    if row["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"任务状态为 {row['status']}，不可发送")
    if req.fields_json is not None:
        fields = req.fields_json
    else:
        fields = json.loads(row["fields_json"]) if row["fields_json"] else {}
    fields["subject_matter"] = infer_subject_matter(fields)
    normalize_parents(fields)

    # 1) 硬校验（申请类型/转让安排/四件套/发明人/申请人）
    problems = validate_for_confirm(fields)
    if problems:
        raise HTTPException(status_code=422, detail={"problems": problems})

    # 2) 生成三件成品（每次重建 final/，保证与当前字段一致）
    final_dir = _submission_final_dir(task_id)
    if final_dir.exists():
        shutil.rmtree(final_dir)
    final_dir.mkdir(parents=True, exist_ok=True)

    warnings = []
    try:
        sheet = generate_confirmation_sheet(fields, final_dir)
        if sheet["missing_fields"]:
            shutil.rmtree(final_dir, ignore_errors=True)
            raise HTTPException(status_code=422, detail={
                "problems": [f"确认函必填缺失：{m.get('field_name') or m.get('field')}" for m in sheet["missing_fields"]],
            })
        assignment_results = generate_assignments(fields, final_dir)
        for item in assignment_results:
            warnings.extend(item.get("warnings") or [])
        declaration_results = generate_declarations(fields, final_dir)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"成品生成失败：{exc}")

    account_cfg, cc_addrs = _submission_send_config()
    case_volume = row["case_volume"]
    # 合并生成件 + 手动上传件（manual 同名覆盖 final），供 modal 勾选/下载/替换
    attachments = [{"filename": it["filename"], "source": it["source"], "url": _output_url(it["path"])}
                   for it in _submission_attachment_set(task_id)]

    return {
        "from": account_cfg.get("user", ""),
        "recipients": [row["contact_email"]] if row["contact_email"] else [],
        "cc": cc_addrs,
        "subject": f"【US递交】{case_volume} 确认函及签署文件",
        "body_html": (
            f"<p>您好，</p>"
            f"<p>案号 <b>{case_volume}</b> 的确认函、Assignment 及 Declaration 已生成，"
            f"请查收附件并安排签署。</p>"
            f"<p>本邮件由系统自动发送。</p>"
        ),
        "attachments": attachments,
        "missing_optional_fields": sheet["missing_optional_fields"],
        "warnings": warnings,
    }


@app.get("/api/submission/tasks/{task_id}/attachments")
def list_submission_attachments(task_id: str):
    """当前合并附件清单（生成件 + 手动上传件，manual 同名覆盖）。上传/删除后刷新用。"""
    _load_submission_task(task_id)
    return {"attachments": [
        {"filename": it["filename"], "source": it["source"], "url": _output_url(it["path"])}
        for it in _submission_attachment_set(task_id)]}


@app.post("/api/submission/tasks/{task_id}/upload-attachment")
def upload_submission_attachment(task_id: str, file: UploadFile = File(...)):
    """上传附件到 manual/（改后重传同名件即覆盖生成版；新文件名则作为额外附件）。"""
    _load_submission_task(task_id)
    dest_dir = _submission_manual_dir(task_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", file.filename or "upload.bin").strip() or "upload.bin"
    dest = dest_dir / name
    dest.write_bytes(file.file.read())
    return {"ok": True, "name": name, "url": _output_url(dest)}


@app.delete("/api/submission/tasks/{task_id}/attachment/{name}")
def delete_submission_attachment(task_id: str, name: str):
    """删除手动上传的附件（仅 manual/；生成件由"勾掉不发"控制，不在此删）。"""
    safe = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", name)
    p = _submission_manual_dir(task_id) / safe
    if p.is_file():
        p.unlink()
    return {"ok": True, "name": safe}


class SubmissionConfirmReq(BaseModel):
    fields_json: dict = None      # 可选：与 confirm 一并保存
    recipients: list = []         # modal 确认后的收件人（必填）
    cc: list = []
    subject: str = ""
    body_html: str = ""
    attachments: list = None      # 勾选要发送的附件文件名；缺省=合并集全发（manual 覆盖 final）
    qa: dict = None               # 操作留痕：{opened_at, duration_sec, changed:[{path,old,new}]}（前端采集）


# ─── QA 埋点（seeded error）：播种 / 判定（种子存 submission_qa_seeds，value_a 绝不返前端）───
def _qa_seed_label(path):
    try:
        from submission.qa_seed import POOL
        for it in POOL:
            if it["path"] == path:
                return it["label"]
    except Exception:
        pass
    return path


def _qa_seed_enabled() -> bool:
    """QA 播种全局开关：手动改 qa_seed_state.json 的 "enabled"（true 开 / false 关）。
    文件不存在或读取异常 → 默认开。"""
    try:
        return bool(json.loads(QA_SEED_STATE_PATH.read_text(encoding="utf-8")).get("enabled", True))
    except FileNotFoundError:
        return True
    except Exception:
        return True


def _qa_seed_on_open(task_id, row, fields):
    """env2 确认函页首次打开：pending 且未播过 → AI 造 0~3 错、就地改 fields 为 B、
    B 落库 fields_json + 种子插 submission_qa_seeds(A 只进表)。best-effort，失败不影响页面。
    受全局开关 _qa_seed_enabled() 控制，关则完全跳过播种。"""
    try:
        if not _qa_seed_enabled():
            return
        if row.get("task_type") != "filing_confirmation" or row.get("status") != "pending":
            return
        seen = execute_params("SELECT COUNT(*) AS n FROM submission_qa_seeds WHERE task_id=%s", (task_id,))
        if seen and int(seen[0].get("n") or 0) > 0:
            return   # 已播过，不重复
        from submission.qa_seed import ai_make_seeds
        seeds = ai_make_seeds(fields)   # 就地把 fields 改成 B
        if not seeds:
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for s in seeds:
            execute_params(
                "INSERT INTO submission_qa_seeds "
                "(id, case_volume, task_id, stage, field_path, value_a, value_b, resolved, seeded_at) "
                "VALUES (%s,%s,%s,'confirmation',%s,%s,%s,0,%s)",
                (str(uuid.uuid4()), row["case_volume"], task_id, s["path"], s["value_a"], s["value_b"], now))
        execute_params("UPDATE submission_tasks SET fields_json=%s, updated_at=%s WHERE id=%s",
                       (json.dumps(fields, ensure_ascii=False), now, task_id))
    except Exception as e:  # noqa: BLE001
        print(f"[qa_seed] 播种失败(忽略): {e}", file=sys.stderr)


def _qa_judge_seeds(case_volume, fields):
    """出口判定：读该案未 resolved 种子，逐个判当前值。
    仍==B→漏检(收进 blocked 标签)；已改→捕获(标 resolved)。返回 (blocked_labels, results)。"""
    try:
        seeds = execute_params(
            "SELECT id, field_path, value_b FROM submission_qa_seeds WHERE case_volume=%s AND resolved=0",
            (case_volume,)) or []
        if not seeds:
            return [], []
        from submission.qa_seed import get_by_path
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        blocked, results = [], []
        for s in seeds:
            cur = get_by_path(fields, s["field_path"])
            if cur is not None and str(cur) == str(s["value_b"]):
                blocked.append(_qa_seed_label(s["field_path"]))
                results.append({"field": s["field_path"], "outcome": "missed"})
            else:
                execute_params("UPDATE submission_qa_seeds SET resolved=1, resolved_at=%s WHERE id=%s",
                               (now, s["id"]))
                results.append({"field": s["field_path"], "outcome": "caught"})
        return blocked, results
    except Exception as e:  # noqa: BLE001
        print(f"[qa_seed] 判定失败(忽略，不拦截): {e}", file=sys.stderr)
        return [], []


@app.post("/api/submission/tasks/{task_id}/confirm")
def confirm_submission_task(task_id: str, req: SubmissionConfirmReq):
    """发送成品邮件（复用 preview-send 生成的 final/ 文件）→ done + 插 signature_followup。"""
    row = _load_submission_task(task_id)
    if row["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"任务状态为 {row['status']}，不可确认")
    recipients = [r.strip() for r in req.recipients if r and r.strip()]
    if not recipients:
        raise HTTPException(status_code=400, detail="收件人不能为空")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1) 先保存字段（无论发送成功与否）
    if req.fields_json is not None:
        _uppercase_applicant_names(req.fields_json)   # 申请人英文名落库即大写
        execute_params(
            "UPDATE submission_tasks SET fields_json = %s, updated_at = %s WHERE id = %s",
            (json.dumps(req.fields_json, ensure_ascii=False), now, task_id),
        )

    # 1.5) QA 埋点出口判定（发送前）：仍==B 的种子→漏检+拦截(不发送、逼改)；已改→捕获+标 resolved
    _qa_cur = req.fields_json if req.fields_json is not None else (json.loads(row["fields_json"]) if row["fields_json"] else {})
    _qa_blocked, _qa_results = _qa_judge_seeds(row["case_volume"], _qa_cur)
    if _qa_blocked:
        try:
            from submission.qa_log import append as _qa_append
            _qa_append({"stage": "confirmation", "case": row["case_volume"],
                        "reviewer": row.get("contact_email"), "event": "blocked", "seeds": _qa_results})
        except Exception:
            pass
        raise HTTPException(status_code=409,
                            detail="以下字段疑似未核对（与初始值一致）：【" + "、".join(_qa_blocked) +
                                   "】。请对照原始资料核对、修正后再发送。")

    # 2) 取附件：合并 final/(生成) + manual/(手动上传)，manual 同名覆盖；
    #    req.attachments 给定则只发勾选的，缺省全发。
    all_items = {it["filename"]: it["path"] for it in _submission_attachment_set(task_id)}
    if not all_items:
        raise HTTPException(status_code=400, detail="成品文件不存在，请先点击发送预览（preview-send）")
    if req.attachments is not None:
        files = [all_items[n] for n in req.attachments if n in all_items]
        if not files:
            raise HTTPException(status_code=400, detail="未选择任何附件")
    else:
        files = list(all_items.values())

    # 3) 组装邮件并实发
    case_volume = row["case_volume"]
    subject = req.subject or f"【US递交】{case_volume} 确认函及签署文件"
    body_html = req.body_html or f"<p>案号 {case_volume} 的签署文件见附件。</p>"
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    for path in files:
        part = MIMEApplication(path.read_bytes())
        part.add_header("Content-Disposition", "attachment", filename=("utf-8", "", path.name))
        msg.attach(part)

    account_cfg, _default_cc = _submission_send_config()
    try:
        _send_smtp(msg, account_cfg, recipients, req.cc or None)
    except Exception as exc:
        # 发送失败：保留 pending，成品已在 final/ 可人工补发
        raise HTTPException(status_code=502, detail=f"邮件发送失败（任务保留 pending，成品已存 final/）：{exc}")

    # 4) 落库：done + 插 signature_followup 待检查记录（供跟进客户回邮 skill 消费）
    execute_params(
        "UPDATE submission_tasks SET status = 'done', confirmed_at = %s, updated_at = %s WHERE id = %s",
        (now, now, task_id),
    )
    followup_fields = json.dumps({
        "source_task_id": task_id,
        "files": [p.name for p in files],
        "sent_to": recipients,
        "sent_cc": req.cc,
        "sent_at": now,
    }, ensure_ascii=False)
    # cc_email：本次确认函发送所用抄送（缺省回退配置默认抄送）→ 存入 followup，
    # 供环节3 超时催办：客户满 2 自然日未回签时，往该地址发催办邮件。
    cc_list = [c.strip() for c in (req.cc or _default_cc or []) if c and c.strip()]
    cc_email = ",".join(cc_list)
    existing = execute_params(
        "SELECT id FROM submission_tasks WHERE task_type = 'signature_followup' AND case_volume = %s",
        (case_volume,),
    )
    if existing:
        execute_params(
            "UPDATE submission_tasks SET fields_json = %s, cc_email = %s, status = 'pending', updated_at = %s WHERE id = %s",
            (followup_fields, cc_email, now, existing[0]["id"]),
        )
        followup_id = existing[0]["id"]
    else:
        followup_id = str(uuid.uuid4())
        execute_params(
            "INSERT INTO submission_tasks "
            "(id, task_type, case_volume, fields_json, contact_email, cc_email, status, created_at) "
            "VALUES (%s, 'signature_followup', %s, %s, %s, %s, 'pending', %s)",
            (followup_id, case_volume, followup_fields, row["contact_email"], cc_email, now),
        )

    # 5) 退回重编后重发的场景：若同案环节4（filing_preparation）已存在且 pending，
    #    用本次确认的改正后数据【原地刷新】其 fields_json（审阅人链接不变、数据更新）。
    #    环节4 若已 done（递交件已发美代理）在 reopen 阶段就被硬拦，不会走到这里。
    refreshed_prep = []
    prep_rows = execute_params(
        "SELECT id FROM submission_tasks "
        "WHERE task_type = 'filing_preparation' AND case_volume = %s AND status = 'pending'",
        (case_volume,),
    )
    if prep_rows:
        cur = execute_params("SELECT fields_json FROM submission_tasks WHERE id = %s", (task_id,))
        new_fields = cur[0]["fields_json"] if cur else None
        for p in prep_rows:
            execute_params(
                "UPDATE submission_tasks SET fields_json = %s, updated_at = %s WHERE id = %s",
                (new_fields, now, p["id"]),
            )
            refreshed_prep.append(p["id"])

    # QA 操作留痕（修改痕迹+时长+埋点结果）：best-effort，不影响发送
    try:
        from submission.qa_log import append as _qa_append, build_op_record as _qa_build
        _qa_append(_qa_build("confirmation", case_volume, row.get("contact_email"), req.qa,
                             seeds=(_qa_results or None)))
    except Exception:
        pass

    return {
        "ok": True,
        "task_id": task_id,
        "status": "done",
        "sent_to": recipients,
        "files": [p.name for p in files],
        "followup_task_id": followup_id,
        "refreshed_filing_prep": refreshed_prep,
    }


@app.post("/api/submission/tasks/{task_id}/skip")
def skip_submission_task(task_id: str):
    _load_submission_task(task_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_params(
        "UPDATE submission_tasks SET status = 'skipped', updated_at = %s WHERE id = %s",
        (now, task_id),
    )
    return {"ok": True, "task_id": task_id, "status": "skipped"}


class SubmissionReopenReq(BaseModel):
    # 客户已签（派生 signature_followup 已 received/done）时须显式 force=True 才放行
    force: bool = False


@app.post("/api/submission/tasks/{task_id}/reopen")
def reopen_submission_task(task_id: str, req: SubmissionReopenReq):
    """退回重编：done 的 filing_confirmation → pending，重新可编辑/预览/重发。

    护栏：
    - 同案环节4 filing_preparation 已 done（递交件已发美代理，环节5 已完成）→ 硬禁止退回，
      走人工处置（force 也不放行）。
    - 同案 filing_preparation 仍 pending → 允许退回；重发确认函时（confirm）会用改正后的
      新数据原地刷新该 filing_preparation 的 fields_json（审阅人链接不变）。
    - 同案 signature_followup 已收到签署（received/done）→ 旧签署件基于旧数据，退回会使其失效，
      须 force=True，并把该 followup 重置回 pending（客户须重签）。
    """
    row = _load_submission_task(task_id)
    if row["task_type"] != "filing_confirmation":
        raise HTTPException(status_code=400, detail=f"仅 filing_confirmation 可退回重编，当前 {row['task_type']}")
    if row["status"] != "done":
        raise HTTPException(status_code=400, detail=f"任务状态为 {row['status']}，仅 done 可退回重编")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 环节4 已 done（递交件已发美代理）→ 硬禁止，无法用 force 覆盖，须人工处置
    filing_prep = execute_params(
        "SELECT id, status FROM submission_tasks "
        "WHERE task_type = 'filing_preparation' AND case_volume = %s",
        (row["case_volume"],),
    )
    if any(f["status"] == "done" for f in filing_prep):
        raise HTTPException(
            status_code=409,
            detail="该案递交件已发美代理（环节4/5 已完成），不能退回重编，请人工处理。",
        )

    followup = execute_params(
        "SELECT id, status FROM submission_tasks "
        "WHERE task_type = 'signature_followup' AND case_volume = %s",
        (row["case_volume"],),
    )
    signed_followup = [f for f in followup if f["status"] in ("received", "done")]
    if signed_followup and not req.force:
        raise HTTPException(
            status_code=409,
            detail=(f"客户已签署（signature_followup 状态 {signed_followup[0]['status']}），"
                    "退回将使已签件失效、客户须重签；如确需退回请以 force=true 重试。"),
        )

    # 1) 确认函任务退回 pending，清 confirmed_at
    execute_params(
        "UPDATE submission_tasks SET status = 'pending', confirmed_at = NULL, updated_at = %s WHERE id = %s",
        (now, task_id),
    )
    # 2) 已签的 followup 重置回 pending（客户须重签）；pending 的保持不动，等重发时 confirm 自动刷新
    reset_followups = []
    if req.force:
        for f in signed_followup:
            execute_params(
                "UPDATE submission_tasks SET status = 'pending', updated_at = %s WHERE id = %s",
                (now, f["id"]),
            )
            reset_followups.append(f["id"])

    return {
        "ok": True,
        "task_id": task_id,
        "status": "pending",
        "reset_followups": reset_followups,
        # pending 的环节4 任务：重发确认函时会用新数据原地刷新其 fields_json
        "filing_prep_pending": [f["id"] for f in filing_prep if f["status"] == "pending"],
    }


# ═══════════════════════════════════════════════════════════════════
# 环节4：准备递交文件（task_type='filing_preparation'）—— 审阅人审 POA/Transmittal/ADS
# 全部新增 /api/submission/filing/* 路由，与环节2 的 /api/submission/tasks/* 互不影响。
# ═══════════════════════════════════════════════════════════════════

def _output_url(path) -> str:
    """绝对路径 → /output 挂载下的相对 URL。"""
    return "/output/" + str(Path(path).relative_to(_OUTPUT_DIR_FOR_MOUNT))


def _filing_final_docs_dir(task_id: str) -> Path:
    """人工上传的定稿文件目录（说明书/权要/附图终版）。"""
    return SUBMISSION_OUTPUT_DIR / task_id / "final-docs"


def _filing_poa_scan_dir(task_id: str) -> Path:
    """POA 第二页扫描件目录（人工上传，单张 PDF，重传覆盖）。"""
    return SUBMISSION_OUTPUT_DIR / task_id / "poa-scan"


def _filing_poa_scan_paths(task_id: str) -> dict:
    """按申请人下标取 POA 扫描件：poa-scan/{i}.pdf → {i: Path}。
    兼容旧的单张(非 {i}.pdf 命名)：无任何 {i}.pdf 时把目录里第一张 pdf 当作 index 0。"""
    d = _filing_poa_scan_dir(task_id)
    out = {}
    if not d.is_dir():
        return out
    for p in d.glob("*.pdf"):
        if p.is_file() and p.stem.isdigit():
            out[int(p.stem)] = p
    if not out:   # 旧单张兼容
        pdfs = sorted(p for p in d.glob("*.pdf") if p.is_file())
        if pdfs:
            out[0] = pdfs[0]
    return out


def _filing_poa_scan_path(task_id: str):
    """兼容旧调用：返回 index 0 的扫描件（无则 None）。"""
    return _filing_poa_scan_paths(task_id).get(0)


def _find_confirmation_original(conf_task_id: str):
    """在同案 filing_confirmation 任务的 manual/(优先，同名覆盖) / final/ 里找确认函原件。
    确认函文件名含 'Application Information Sheet'（排除 Assignment/Declaration）。返回 Path 或 None。"""
    def pick(d: Path):
        if not d.exists():
            return None
        for p in sorted(d.glob("*")):
            if not p.is_file() or p.suffix.lower() not in (".docx", ".pdf"):
                continue
            nm = p.name.lower()
            if "application information sheet" in nm or "确认函" in p.name:
                return p
        return None
    return pick(_submission_manual_dir(conf_task_id)) or pick(_submission_final_dir(conf_task_id))


# 代理所固定 4 家（与旧确认函流程一致）；前端下拉用此列表，值即 agent_info.agent 的匹配串
FILING_AGENT_FIRMS = ["Lai Runzhi", "Poseidon Advanced IP LLC", "Metis IP LLC", "Porus IP LLC"]


def _resolve_agent_cus_code(case_volume: str, firm: str) -> str:
    """按代理所把客户码(案号前缀)重映射为 agent_info.cus_code（对齐旧 single_parse_confirm）。"""
    code = (case_volume or "").split("-")[0]
    f = (firm or "").lower()
    if "lai" in f or "runzhi" in f:
        return "all"
    if "poseidon" in f:
        return code if code in ("20618", "20608", "20664") else "other"
    if "metis" in f:
        return code if code in ("20615", "20618") else "other"
    if "porus" in f:
        return "all"
    return code


def query_agent_info(case_volume: str, firm: str, person: str) -> dict:
    """查 atw.agent_info 取签字代理人信息（代理所 + 客户码 + 代理人）。

    对齐旧 single_parse_confirm.py:1157：cus_code 按代理所重映射，代理人按 CNname 精确或
    othername 模糊。**参数化查询**（不拼字符串）。命中返回可注入 fields_to_case_info 的 dict；
    未命中返回 {"_matched": False, "_note": ...}。
    """
    cus_code = _resolve_agent_cus_code(case_volume, firm)
    rows = execute_params(
        "SELECT cus_code, reg_no, firstname, lastname, agent_cus_no, mail, CNname, typed_name, deposit "
        "FROM agent_info WHERE cus_code=%s AND agent LIKE %s AND (CNname=%s OR othername LIKE %s)",
        (cus_code, f"%{firm}%", person, f"%{person}%"))
    if not rows:
        return {"_matched": False,
                "_note": f"未在 agent_info 命中（代理所={firm} 客户码={cus_code} 代理人={person}）"}
    r = rows[0]
    first = (r.get("firstname") or "").strip()
    last = (r.get("lastname") or "").strip()
    mail = r.get("mail") or ""
    return {
        "_matched": True,
        "Name": f"{first} {last}".strip(),
        "First Name": first,
        "Last Name": last,
        "Registration Number": r.get("reg_no") or "",
        "title": r.get("typed_name") or "",
        "Customer Number": r.get("agent_cus_no") or "",
        "Deposit Account No": r.get("deposit") or "",
        "Email Address": [m.strip() for m in mail.split(",") if m.strip()],
    }


def _filing_case_info(row: dict, fields: dict):
    """fields_json → case_info。签字人/Customer Number/Deposit 优先用审核页「查库带出」并存进
    fields_json.filing_extra.agent_info 的快照；无则回退 agent_config（load_agent_info）。"""
    ai = (fields.get("filing_extra") or {}).get("agent_info") or load_agent_info(row["case_volume"])
    ci = fields_to_case_info(fields, ai)
    return ci, ai


def _filing_review_base() -> str:
    cfg = _load_email_config()
    return cfg.get("submission", {}).get("review_base_url", "http://10.10.70.88:8501")


def _send_filing_review_link(case_volume: str, link: str) -> bool:
    """转入后给审阅人发审阅链接（best-effort，收件人取 email_config.submission.review_notify）。"""
    try:
        cfg = _load_email_config()
        sub = cfg.get("submission", {})
        recipients = [r for r in (sub.get("review_notify") or []) if r]
        if not recipients:
            return False
        account_cfg, _cc = _submission_send_config()
        msg = MIMEMultipart()
        msg["Subject"] = f"【US递交-待审阅】{case_volume} 递交文件"
        msg.attach(MIMEText(
            f"<p>案号 <b>{case_volume}</b> 的递交文件已转入准备，请审阅 POA/Transmittal/ADS：</p>"
            f"<p><a href='{link}'>{link}</a></p><p>本邮件由系统自动发送。</p>",
            "html", "utf-8"))
        _send_smtp(msg, account_cfg, recipients, sub.get("cc") or None)
        return True
    except Exception as exc:
        print(f"[filing] 审阅链接发送失败: {exc}", file=sys.stderr)
        return False


@app.get("/submission/filing")
def filing_review_home():
    """落地页（不带 task_id）：列表 + 转入入口，供首次进入/没有链接时使用。"""
    if not FILING_HTML.exists():
        return PlainTextResponse("递交准备审核页前端尚未部署（web/filing.html 缺失）。", status_code=503)
    return FileResponse(str(FILING_HTML))


@app.get("/submission/filing/{task_id}")
def filing_review_page(task_id: str):
    if not FILING_HTML.exists():
        return PlainTextResponse(
            f"递交准备审核页前端尚未部署（web/filing.html 缺失）。任务ID: {task_id}\n"
            f"可先用 GET /api/submission/filing/{task_id} 查看数据。",
            status_code=503,
        )
    return FileResponse(str(FILING_HTML))


def _transfer_to_filing(case_volume: str) -> dict:
    """从同案 filing_confirmation 复制 fields_json，建 filing_preparation（幂等）。

    手动转入 / 「已收到签署」/ cron auto-transfer 三处共用。
    已存在则返回现有；无 filing_confirmation 任务抛 404。
    :return: {task_id, existed, review_link, notified}
    """
    existing = execute_params(
        "SELECT id FROM submission_tasks WHERE task_type='filing_preparation' AND case_volume=%s",
        (case_volume,))
    if existing:
        eid = existing[0]["id"]
        return {"task_id": eid, "existed": True,
                "review_link": f"{_filing_review_base()}/submission/filing/{eid}", "notified": False}
    src = execute_params(
        "SELECT fields_json, contact_email FROM submission_tasks "
        "WHERE task_type='filing_confirmation' AND case_volume=%s ORDER BY created_at DESC LIMIT 1",
        (case_volume,))
    if not src:
        raise HTTPException(404, f"未找到案号 {case_volume} 的 filing_confirmation 任务，无法转入")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_id = str(uuid.uuid4())
    execute_params(
        "INSERT INTO submission_tasks (id, task_type, case_volume, fields_json, contact_email, status, created_at) "
        "VALUES (%s, 'filing_preparation', %s, %s, %s, 'pending', %s)",
        (new_id, case_volume, src[0]["fields_json"], src[0].get("contact_email"), now))
    link = f"{_filing_review_base()}/submission/filing/{new_id}"
    notified = _send_filing_review_link(case_volume, link)
    return {"task_id": new_id, "existed": False, "review_link": link, "notified": notified}


@app.post("/api/submission/filing/create")
def create_filing_task(case_volume: str):
    """手动转入：从同案 filing_confirmation 建 filing_preparation（已存在则返回现有）。"""
    return _transfer_to_filing(case_volume)


# 递交页独有、重新拉取时要保留的键（确认函没有这些）：代理人/发明人地址、递交清单
_FILING_ONLY_KEYS = ("filing_extra", "transmittal_options")


@app.post("/api/submission/filing/{task_id}/resync")
def resync_filing_from_confirmation(task_id: str):
    """从同案确认函(filing_confirmation)重新拉取最新数据覆盖本递交任务的共享字段，
    保留递交页独有的 filing_extra(代理人/通信地址)/transmittal_options(递交清单)。
    仅 pending(未发美代理)时可用。解决转入后 env2 又改数据、env5 拿不到的问题。"""
    row = _load_submission_task(task_id)
    if row["task_type"] != "filing_preparation":
        raise HTTPException(400, "仅递交准备(filing_preparation)任务可重新拉取")
    if row["status"] != "pending":
        raise HTTPException(400, f"任务状态为 {row['status']}，已锁定，不可重新拉取")
    src = execute_params(
        "SELECT fields_json FROM submission_tasks "
        "WHERE task_type='filing_confirmation' AND case_volume=%s ORDER BY created_at DESC LIMIT 1",
        (row["case_volume"],))
    if not src or not src[0].get("fields_json"):
        raise HTTPException(404, f"未找到案号 {row['case_volume']} 的确认函数据，无法拉取")
    conf = json.loads(src[0]["fields_json"])
    cur = json.loads(row["fields_json"]) if row["fields_json"] else {}
    merged = dict(conf)                       # 确认函最新数据为基底
    for k in _FILING_ONLY_KEYS:               # 保留递交页独有键
        if k in cur:
            merged[k] = cur[k]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_params("UPDATE submission_tasks SET fields_json=%s, updated_at=%s WHERE id=%s",
                   (json.dumps(merged, ensure_ascii=False), now, task_id))
    return {"ok": True, "task_id": task_id}


@app.get("/api/submission/signatures")
def list_signature_followups(status: str = "pending"):
    """待回签列表（signature_followup）。附 transferred=该案是否已建 filing_preparation。"""
    statuses = [s.strip() for s in status.split(",") if s.strip()]
    placeholders = ",".join(["%s"] * len(statuses))
    rows = execute_params(
        f"SELECT id, case_volume, contact_email, status, fields_json, created_at, updated_at "
        f"FROM submission_tasks WHERE task_type='signature_followup' AND status IN ({placeholders}) "
        f"ORDER BY created_at DESC", tuple(statuses))
    out = []
    for r in rows:
        for key in ("created_at", "updated_at"):
            if r.get(key) is not None:
                r[key] = str(r[key])
        # 机审结论（needs_fix 时供人工核对是否误判）
        try:
            review = (json.loads(r.get("fields_json") or "{}")).get("review") or {}
        except Exception:
            review = {}
        r.pop("fields_json", None)
        ex = execute_params(
            "SELECT id FROM submission_tasks WHERE task_type='filing_preparation' AND case_volume=%s",
            (r["case_volume"],))
        out.append({**r, "review_missing": review.get("missing") or [],
                    "review_note": review.get("note") or "",
                    "transferred": bool(ex), "filing_task_id": ex[0]["id"] if ex else None})
    return {"tasks": out}


@app.post("/api/submission/signatures/{task_id}/mark-signed")
def mark_signature_signed(task_id: str):
    """手动「已收到签署」：signature_followup 置 done 并立即转入递交准备（幂等）。
    cron(auto-transfer) 兜底覆盖由回签检测 skill 标 done 的记录。"""
    row = _load_submission_task(task_id)
    if row["task_type"] != "signature_followup":
        raise HTTPException(400, f"任务 {task_id} 不是 signature_followup（实际 {row['task_type']}）")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        ff = json.loads(row["fields_json"]) if row["fields_json"] else {}
    except Exception:
        ff = {}
    ff["signed_at"] = now
    execute_params(
        "UPDATE submission_tasks SET status='done', confirmed_at=%s, fields_json=%s, updated_at=%s WHERE id=%s",
        (now, json.dumps(ff, ensure_ascii=False), now, task_id))
    res = _transfer_to_filing(row["case_volume"])
    return {"ok": True, "case_volume": row["case_volume"], "signed_at": now,
            "filing_task_id": res["task_id"], "existed": res["existed"],
            "review_link": res["review_link"], "notified": res["notified"]}


@app.post("/api/submission/filing/auto-transfer")
def auto_transfer_filing():
    """cron 入口：扫已回签(signature_followup=done)且未转入的案件 → 建 filing_preparation。
    供定时器周期调用（schtasks/crontab → curl 本路由）。幂等，可重复跑。"""
    rows = execute_params(
        "SELECT DISTINCT case_volume FROM submission_tasks "
        "WHERE task_type='signature_followup' AND status='done'")
    created, skipped, failed = [], [], []
    for r in rows:
        cv = r["case_volume"]
        exists = execute_params(
            "SELECT id FROM submission_tasks WHERE task_type='filing_preparation' AND case_volume=%s", (cv,))
        if exists:
            skipped.append(cv)
            continue
        try:
            res = _transfer_to_filing(cv)
            created.append({"case_volume": cv, "task_id": res["task_id"], "notified": res["notified"]})
        except HTTPException as e:
            failed.append({"case_volume": cv, "error": str(e.detail)})
    return {"created": created, "skipped": skipped, "failed": failed,
            "summary": f"新建 {len(created)}，已存在 {len(skipped)}，失败 {len(failed)}"}


@app.get("/api/submission/agent-firms")
def list_agent_firms():
    """代理所候选（固定 4 家），供 filing 审核页下拉。"""
    return {"firms": FILING_AGENT_FIRMS}


@app.get("/api/submission/agent-persons")
def list_agent_persons(firm: str, case_volume: str = ""):
    """按代理所列该所可选代理人（CNname 去重），供 filing 审核页「代理人」下拉。
    cus_code 与查库带出同口径（按代理所+案号重映射）；查不到/异常返回空列表（不阻塞手填）。"""
    try:
        cus_code = _resolve_agent_cus_code(case_volume, firm)
        rows = execute_params(
            "SELECT DISTINCT CNname FROM agent_info "
            "WHERE cus_code=%s AND agent LIKE %s AND CNname IS NOT NULL AND CNname<>'' "
            "ORDER BY CNname",
            (cus_code, f"%{firm}%")) or []
        persons = [r.get("CNname").strip() for r in rows if (r.get("CNname") or "").strip()]
    except Exception as exc:   # noqa: BLE001
        print(f"[agent-persons] 查代理人失败 firm={firm}: {exc}", file=sys.stderr)
        persons = []
    return {"firm": firm, "persons": persons}


@app.get("/api/submission/agent-info")
def get_agent_info(case_volume: str, firm: str, person: str):
    """按代理所/代理人查 agent_info，供 filing 审核页「查库带出」签字人/Customer No/Deposit/邮箱。"""
    ai = query_agent_info(case_volume, firm, person)
    return {
        "matched": ai.get("_matched", False),
        "note": ai.get("_note", ""),
        "agent_info": {k: v for k, v in ai.items() if not k.startswith("_")},
    }


@app.get("/api/submission/filing/{task_id}/confirmation-original")
def filing_confirmation_original(task_id: str):
    """预览客户实际收到的那份确认函原件（同案 filing_confirmation 的 final/ 成品；docx→PDF）。
    不重新生成，找不到则返回 available=False + 说明。"""
    row = _load_submission_task(task_id)
    cv = row["case_volume"]
    conf = execute_params(
        "SELECT id FROM submission_tasks WHERE task_type='filing_confirmation' AND case_volume=%s "
        "ORDER BY created_at DESC LIMIT 1", (cv,))
    if not conf:
        return {"available": False, "note": "无同案确认函(filing_confirmation)任务"}
    src = _find_confirmation_original(conf[0]["id"])
    if not src:
        return {"available": False, "note": "确认函原件不存在（环节2 未生成/发送，或成品已清理）"}
    if src.suffix.lower() == ".pdf":
        return {"available": True, "name": src.name, "pdf_url": _output_url(src)}
    try:
        out_dir = SUBMISSION_OUTPUT_DIR / task_id / "conf_ref"
        out_dir.mkdir(parents=True, exist_ok=True)
        pdf = docx_to_pdf(str(src), out_dir)
        return {"available": True, "name": src.name, "pdf_url": _output_url(pdf)}
    except Exception as exc:
        return {"available": False, "note": f"确认函转 PDF 失败：{exc}"}


@app.get("/api/submission/filing/{task_id}")
def get_filing_task(task_id: str):
    row = _load_submission_task(task_id)
    fields = json.loads(row["fields_json"]) if row["fields_json"] else {}
    final_dir = _filing_final_docs_dir(task_id)
    final_docs = ([{"name": p.name, "url": _output_url(p)}
                   for p in sorted(final_dir.glob("*")) if p.is_file()]
                  if final_dir.exists() else [])
    _scans = _filing_poa_scan_paths(task_id)
    poa_scans = {str(i): {"name": p.name, "url": _output_url(p)} for i, p in _scans.items()}   # 按申请人下标
    poa_scan = poa_scans.get("0")   # 兼容旧前端（单张=index 0）
    # 同案确认函任务 id（供送审邮件附「确认函及参考文件页」链接 /submission/review/{id}）
    conf = execute_params(
        "SELECT id FROM submission_tasks WHERE task_type='filing_confirmation' AND case_volume=%s "
        "ORDER BY created_at DESC LIMIT 1", (row["case_volume"],))
    return {
        "id": row["id"],
        "task_type": row["task_type"],
        "case_volume": row["case_volume"],
        "status": row["status"],
        "fields_json": fields,
        "transmittal_options": fields.get("transmittal_options") or {},
        "final_docs": final_docs,
        "poa_scan": poa_scan,
        "poa_scans": poa_scans,   # {申请人下标: {name,url}}，每人一份
        "confirmation_task_id": conf[0]["id"] if conf else None,
    }


class FilingSaveReq(BaseModel):
    fields_json: dict
    transmittal_options: dict = None


@app.post("/api/submission/filing/{task_id}/save")
def save_filing_task(task_id: str, req: FilingSaveReq):
    _load_submission_task(task_id)
    fields = dict(req.fields_json or {})
    if req.transmittal_options is not None:
        fields["transmittal_options"] = req.transmittal_options
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_params(
        "UPDATE submission_tasks SET fields_json=%s, updated_at=%s WHERE id=%s",
        (json.dumps(fields, ensure_ascii=False), now, task_id))
    return {"ok": True, "task_id": task_id}


@app.post("/api/submission/filing/{task_id}/upload-final")
def upload_final_doc(task_id: str, file: UploadFile = File(...)):
    """上传定稿文件（说明书/权要/附图终版）到 final-docs/。"""
    _load_submission_task(task_id)
    dest_dir = _filing_final_docs_dir(task_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", file.filename or "upload.bin").strip() or "upload.bin"
    dest = dest_dir / name
    dest.write_bytes(file.file.read())
    return {"ok": True, "name": name, "url": _output_url(dest)}


@app.delete("/api/submission/filing/{task_id}/final/{name}")
def delete_final_doc(task_id: str, name: str):
    safe = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", name)
    p = _filing_final_docs_dir(task_id) / safe
    if p.is_file():
        p.unlink()
    return {"ok": True, "name": safe}


@app.post("/api/submission/filing/{task_id}/upload-poa-scan")
def upload_poa_scan(task_id: str, index: int = 0, file: UploadFile = File(...)):
    """上传第 index 个申请人的 POA 第二页扫描件（每人一份，存 poa-scan/{index}.pdf，重传覆盖该份）。
    生成/发送该申请人的 POA 时追加为第二页。"""
    _load_submission_task(task_id)
    raw = file.file.read()
    if not (file.filename or "").lower().endswith(".pdf") or not raw.startswith(b"%PDF"):
        raise HTTPException(400, "POA 扫描件必须是 PDF 文件")
    dest_dir = _filing_poa_scan_dir(task_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{int(index)}.pdf"      # 按申请人下标命名，只覆盖该份
    dest.write_bytes(raw)
    return {"ok": True, "index": int(index), "name": dest.name, "url": _output_url(dest)}


@app.delete("/api/submission/filing/{task_id}/poa-scan")
def delete_poa_scan(task_id: str, index: int = None):
    """删除 POA 扫描件：给 index 删该申请人那份(poa-scan/{index}.pdf)；不给 index 删全部(兼容)。"""
    d = _filing_poa_scan_dir(task_id)
    if not d.is_dir():
        return {"ok": True}
    if index is None:
        shutil.rmtree(d)
    else:
        p = d / f"{int(index)}.pdf"
        if p.is_file():
            p.unlink()
    return {"ok": True, "index": index}


@app.post("/api/submission/filing/{task_id}/upload-replacement")
def upload_filing_replacement(task_id: str, target: str, file: UploadFile = File(...)):
    """上传 POA/Transmittal/ADS 的替换件到 manual/（存为 {Token}-replacement.ext，重传覆盖）。
    预览优先展示、发美代理时实发替换件（覆盖生成件内容、保留生成件 stem）。"""
    _load_submission_task(task_id)
    token = _FILING_TOKENS.get(target)
    if not token:
        raise HTTPException(400, f"未知 target: {target}")
    ext = (Path(file.filename or "").suffix or "").lower()
    if ext not in (".pdf", ".docx"):
        raise HTTPException(400, "替换件仅支持 PDF 或 DOCX")
    md = _submission_manual_dir(task_id)
    md.mkdir(parents=True, exist_ok=True)
    for old in md.glob(f"{token}-replacement.*"):   # 先清旧的(可能扩展名不同)，再写新的
        old.unlink()
    dest = md / f"{token}-replacement{ext}"
    dest.write_bytes(file.file.read())
    return {"ok": True, "target": target, "name": dest.name, "url": _output_url(dest)}


@app.get("/api/submission/filing/{task_id}/replacements")
def list_filing_replacements(task_id: str):
    """列出当前已上传的替换件：{poa|transmittal|ads: {name,url} 或 null}。"""
    _load_submission_task(task_id)
    out = {}
    for tgt in _FILING_TOKENS:
        p = _filing_replacement_path(task_id, tgt)
        out[tgt] = {"name": p.name, "url": _output_url(p)} if p else None
    return {"replacements": out}


@app.delete("/api/submission/filing/{task_id}/replacement")
def delete_filing_replacement(task_id: str, target: str):
    """删除某 target 的替换件（恢复用系统生成版）。"""
    _load_submission_task(task_id)
    token = _FILING_TOKENS.get(target)
    if not token:
        raise HTTPException(400, f"未知 target: {target}")
    md = _submission_manual_dir(task_id)
    if md.is_dir():
        for p in md.glob(f"{token}-replacement.*"):
            p.unlink()
    return {"ok": True, "target": target}


class FilingPreviewReq(BaseModel):
    target: str                    # poa | transmittal | ads
    fields_json: dict = None       # 页面当前编辑值；缺省用库中值
    transmittal_options: dict = None


@app.post("/api/submission/filing/{task_id}/preview")
def preview_filing_task(task_id: str, req: FilingPreviewReq):
    """生成 POA / Transmittal / ADS 预览（PDF）。POA/Transmittal 可内联预览，ADS 仅下载。"""
    row = _load_submission_task(task_id)
    fields = req.fields_json if req.fields_json is not None else (
        json.loads(row["fields_json"]) if row["fields_json"] else {})
    fields["subject_matter"] = infer_subject_matter(fields)
    normalize_parents(fields)
    opts = req.transmittal_options if req.transmittal_options is not None else (fields.get("transmittal_options") or {})
    fields["transmittal_options"] = opts   # 合并页面最新递交清单，供 ADS 取实体/图纸页数（原在 ci 之后→取不到最新，已修）
    ci, _ai = _filing_case_info(row, fields)

    preview_dir = SUBMISSION_OUTPUT_DIR / task_id / "preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    warnings = []
    try:
        if req.target == "poa":
            scans = _filing_poa_scan_paths(task_id)   # {申请人下标: 扫描件}
            poas = generate_poas(ci, preview_dir, scan_paths={i: str(p) for i, p in scans.items()})
            files = [{"name": d["file_name"], "pdf_url": _output_url(d["file_path"]),
                      "type": d.get("type"), "applicant": d.get("applicant", "")} for d in poas]
        elif req.target == "transmittal":
            d = generate_transmittal(ci, preview_dir, options=opts)
            warnings.extend(d.get("warnings") or [])
            files = [{"name": d["file_name"], "pdf_url": _output_url(d["file_path"]), "type": d.get("type")}]
        elif req.target == "ads":
            # 审阅阶段：本地"数据核对版"PDF（不上云、不产 XFA）；正式 XFA 在确认发送时生成
            ads = generate_ads_preview(ci, preview_dir)
            warnings.append("ADS 在线为数据核对版（本地生成，仅供核对字段）；正式 XFA 版在确认发送时生成")
            files = [{"name": ads["file_name"], "pdf_url": _output_url(ads["file_path"]), "type": ads["type"]}]
        else:
            raise HTTPException(400, f"未知 target: {req.target}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"预览生成失败：{exc}")
    return {"target": req.target, "files": files, "warnings": warnings}


_FILING_TOKENS = {"poa": "POA", "transmittal": "Transmittal", "ads": "ADS"}


def _filing_replacement_path(task_id: str, target: str):
    """env5 替换件源文件：manual/ 里 {Token}-replacement.(pdf|docx)。无则 None。（发送用，不看 mtime）"""
    token = _FILING_TOKENS.get(target)
    md = _submission_manual_dir(task_id)
    if not token or not md.is_dir():
        return None
    cands = sorted((p for p in md.glob(f"{token}-replacement.*") if p.suffix.lower() in (".pdf", ".docx")),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


def _filing_override_pdf(task_id: str, target: str, gen_mtime: float = 0.0):
    """预览用替换件(转成可内联的 PDF)：仅当替换件比 gen_mtime(最近一次生成的预览)新才采用——
    点过刷新预览后生成版更新 → 回落生成版(与 env2 同一 mtime 逻辑)。pdf 直用；docx 转 PDF 到 preview/_ov。"""
    src = _filing_replacement_path(task_id, target)
    if not src or src.stat().st_mtime <= gen_mtime:
        return None
    if src.suffix.lower() == ".pdf":
        return src
    ov_dir = SUBMISSION_OUTPUT_DIR / task_id / "preview" / "_ov"
    ov_dir.mkdir(parents=True, exist_ok=True)
    out = ov_dir / (src.stem + ".pdf")
    if (not out.exists()) or out.stat().st_mtime < src.stat().st_mtime:
        docx_to_pdf(str(src), ov_dir)
    return out if out.exists() else None


@app.get("/api/submission/filing/{task_id}/preview-existing")
def filing_preview_existing(task_id: str, target: str = "poa"):
    """展示已存在成品(不重生成)。POA/Transmittal/ADS 优先展示 manual/ 里的替换件(比最近一次
    生成的预览新时)，无则看 preview/。供打开/切 tab 时「有则直接展示、无则再 POST /preview 生成」。"""
    _load_submission_task(task_id)
    preview_dir = SUBMISSION_OUTPUT_DIR / task_id / "preview"
    token = _FILING_TOKENS.get(target, target)
    # 替换件优先（比生成版新才用；点过刷新预览→回落生成版）
    _gen_mtime = 0.0
    if preview_dir.is_dir():
        _ms = [p.stat().st_mtime for p in preview_dir.glob("*.pdf")
               if token.lower() in p.name.lower() and "-flat" not in p.name.lower()]
        _gen_mtime = max(_ms) if _ms else 0.0
    ov = _filing_override_pdf(task_id, target, _gen_mtime)
    if ov:
        return {"target": target, "override": True,
                "files": [{"name": ov.stem, "pdf_url": _output_url(ov), "type": "pdf"}]}
    files = []
    if preview_dir.is_dir():
        cand = [p for p in preview_dir.glob("*.pdf")
                if token.lower() in p.name.lower() and "-flat" not in p.name.lower()]  # 排除在线扁平版
        # 按基名去重：去掉日期前缀(YYYY-MM-DD-)和 _free_output_path 在 Windows 占用时追加的 -时间戳 锁后缀，
        # 这样同一份 POA 的不同日期/重生成版本合并为一条；POA 多申请人时基名含申请人名 → 每人各留一份。
        best = {}
        for p in cand:
            base = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", p.stem)   # 去日期前缀
            base = re.sub(r"-\d{6,}$", "", base)                # 去时间戳锁后缀
            if base not in best or p.stat().st_mtime > best[base].stat().st_mtime:
                best[base] = p
        picks = sorted(best.values(), key=lambda p: p.stat().st_mtime, reverse=True)
        # ADS/Transmittal 天然单份 → 只取最新一份（POA 可多份=每申请人一份）
        if target in ("ads", "transmittal"):
            picks = picks[:1]
        for p in picks:
            files.append({"name": p.stem, "pdf_url": _output_url(p), "type": "pdf"})
    return {"target": target, "files": files}


class FilingAdsXfaReq(BaseModel):
    fields_json: dict = None       # 页面当前编辑值（未保存也生效）；缺省用库中值
    transmittal_options: dict = None


@app.post("/api/submission/filing/{task_id}/ads-xfa")
def filing_ads_xfa(task_id: str, online: int = 0, req: FilingAdsXfaReq = None):
    """按需生成 ADS XFA 版：默认本地 XFA 供下载（Adobe 打开，不上云）；
    online=1 时额外走 pdfRest 扁平化，产出可在线看的真实排版 PDF。
    与预览一致，优先用页面当前编辑值 req.fields_json（未点保存也能带出签字/通信），缺省回退库中值。"""
    row = _load_submission_task(task_id)
    fields = (req.fields_json if (req and req.fields_json is not None)
              else (json.loads(row["fields_json"]) if row["fields_json"] else {}))
    if req and req.transmittal_options is not None:
        fields["transmittal_options"] = req.transmittal_options
    fields["subject_matter"] = infer_subject_matter(fields)
    normalize_parents(fields)
    ci, _ai = _filing_case_info(row, fields)
    out_dir = SUBMISSION_OUTPUT_DIR / task_id / "preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        if online:
            ads = generate_ads_flat(ci, out_dir)
            return {"download_url": _output_url(ads["xfa_file_path"]), "download_name": ads["xfa_file_name"],
                    "online_pdf_url": _output_url(ads["file_path"]), "warnings": ads.get("warnings") or []}
        ads = generate_ads(ci, out_dir)
        return {"download_url": _output_url(ads["file_path"]), "download_name": ads["file_name"]}
    except Exception as exc:
        raise HTTPException(500, f"ADS XFA 生成失败：{exc}")


class FilingConfirmReq(BaseModel):
    fields_json: dict = None
    transmittal_options: dict = None
    recipients: list = []          # 美国代理人邮箱（必填）
    cc: list = []
    recipient_name: str = "X总/X律师"
    subject: str = ""
    body: str = ""
    file_channels: dict = {}       # {文件key: "docusign"|"email"}；key=POA/Transmittal/ADS 或定稿文件名
    signer_name: str = ""          # DocuSign 签字人姓名（缺省用收件人邮箱）
    qa: dict = None                # 操作留痕：{opened_at, duration_sec, changed:[{path,old,new}]}（前端采集）


class SendReviewerReq(BaseModel):
    recipients: list = []          # 审核人邮箱（必填，下拉/手填）
    cc: list = []
    body: str = ""                 # 邮件正文（可编辑；含【在线审核链接】占位，发送时替换成真链接）


def _doc_channel_key(path, docs):
    """文件的通道 key：生成的三件用类型(POA/Transmittal/ADS)，定稿用文件名。"""
    for d in docs:
        if str(d["file_path"]) == str(path):
            t = (d.get("type") or "")
            if "Transmittal" in t:
                return "Transmittal"
            return t or Path(path).name           # "POA" / "ADS"
    return Path(path).name                        # 定稿：文件名


_DS_DEFAULT_NAME_RE = re.compile(r"ADS|POA|Transmittal|Declarations|Petition", re.I)


def _default_doc_channel(key):
    """前端未显式指定 file_channels 时的默认通道兜底（与前端 defChannelForName 一致）：
    生成的 POA/Transmittal→DocuSign；生成的 ADS(动态 XFA，DocuSign 不接受)→内部邮箱；
    定稿按文件名含 ADS/POA/Transmittal/Declarations/Petition→DocuSign，否则内部邮箱。"""
    if key in ("POA", "Transmittal"):
        return "docusign"
    if key == "ADS":
        return "email"
    return "docusign" if _DS_DEFAULT_NAME_RE.search(key or "") else "email"


def _docusign_kind(path, docs):
    """DocuSign 锚点用的文档类型（不同于通道路由 key）：生成三件用 POA/Transmittal/ADS；
    定稿按文件名认 Petition/Declarations（套 anchor_offsets 里的 'By:' 锚点），否则回退文件名。"""
    k = _doc_channel_key(path, docs)
    if k in ("POA", "Transmittal", "ADS"):
        return k
    return _docusign.infer_kind(Path(path).name) or k


@app.post("/api/submission/filing/{task_id}/confirm")
def confirm_filing_task(task_id: str, req: FilingConfirmReq):
    """生成 POA/Transmittal/ADS 三件成品 + 给美代理邮件 → 发美代理（附定稿）→ done。"""
    row = _load_submission_task(task_id)
    if row["status"] != "pending":
        raise HTTPException(400, f"任务状态为 {row['status']}，不可确认")
    recipients = [r.strip() for r in req.recipients if r and r.strip()]
    # 收件人校验延后到通道拆分后：仅当确有文件走 DocuSign/内部邮箱时才必填（全「仅存档」可空）

    fields = req.fields_json if req.fields_json is not None else (
        json.loads(row["fields_json"]) if row["fields_json"] else {})
    if req.transmittal_options is not None:
        fields["transmittal_options"] = req.transmittal_options
    fields["subject_matter"] = infer_subject_matter(fields)
    normalize_parents(fields)
    ci, _ai = _filing_case_info(row, fields)
    opts = fields.get("transmittal_options") or {}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1) 重建 final/ 生成三件成品
    final_dir = _submission_final_dir(task_id)
    if final_dir.exists():
        shutil.rmtree(final_dir)
    final_dir.mkdir(parents=True, exist_ok=True)
    warnings = []
    try:
        _scans = _filing_poa_scan_paths(task_id)   # {申请人下标: 扫描件}
        _poas = generate_poas(ci, final_dir, scan_paths={i: str(p) for i, p in _scans.items()})   # 每申请人一份
        docs = [*_poas,                                                  # 多份 POA（每申请人一份）
                generate_transmittal(ci, final_dir, options=opts),
                generate_ads(ci, final_dir)]
        for d in docs:
            warnings.extend(d.get("warnings") or [])
        # 替换件顶替：有 manual 替换件的成品，用替换件内容覆盖 final/(保留生成件 stem，采用替换件扩展名)。
        # 通道按 docs 类型、env6 按 stem 比对，均不受影响。POA 多份(多申请人)时替换歧义 → 仅单份时替换。
        _poa_ct = len(_poas)
        for _d in docs:
            _tgt = {"POA": "poa", "Transmittal": "transmittal", "ADS": "ads"}.get(
                "Transmittal" if "Transmittal" in (_d.get("type") or "") else (_d.get("type") or ""))
            if not _tgt:
                continue
            if _tgt == "poa" and _poa_ct > 1:
                continue   # 多申请人多 POA：替换哪一份有歧义，暂不替换（Transmittal/ADS 不受影响）
            _rep = _filing_replacement_path(task_id, _tgt)
            if not _rep:
                continue
            _gen = Path(_d["file_path"])
            _dest = final_dir / (_gen.stem + _rep.suffix.lower())
            _dest.write_bytes(_rep.read_bytes())
            if _dest != _gen and _gen.exists():
                _gen.unlink()   # 删原生成件，避免重复附件
            _d["file_path"] = str(_dest)
            _d["file_name"] = _dest.name
            warnings.append(f"{_tgt.upper()} 使用了上传的替换件（{_rep.name}）")
    except Exception as exc:
        shutil.rmtree(final_dir, ignore_errors=True)
        raise HTTPException(500, f"成品生成失败：{exc}")

    # 2) 附件 = 三件成品 + 人工上传的定稿
    attach_paths = [Path(d["file_path"]) for d in docs]
    fdir = _filing_final_docs_dir(task_id)
    if fdir.exists():
        attach_paths += [p for p in sorted(fdir.glob("*")) if p.is_file()]

    # 2b) 按通道拆分：默认 POA/Transmittal/ADS 走 DocuSign，其余走内部邮箱；req.file_channels 覆盖。
    #     archive=仅存档（不发 DocuSign、不发邮件，只留在 final/ 供存档、并计入 agent_followup 清单）
    _fc = req.file_channels or {}
    ds_paths, email_paths, archive_paths, ch_map = [], [], [], {}
    for p in attach_paths:
        key = _doc_channel_key(p, docs)
        # 默认通道见 _default_doc_channel（生成 ADS=XFA 走内部邮箱；定稿按文件名关键字）；req.file_channels 覆盖
        ch = (_fc.get(key) or _default_doc_channel(key)).lower()
        ch_map[p.name] = ch
        (archive_paths if ch == "archive" else ds_paths if ch == "docusign" else email_paths).append(p)

    # DocuSign 通道当前【只登记不发送】：生产账号无 API 权限(IAM Standard 套餐不含)，改由人工手动发签字件；
    # 系统只登记这些件(记入 docusign_files)，供环节6 轮询邮箱时与回邮比对。
    # 将来账号买了 API：把 email_config.submission.docusign_api_send 设 true 即恢复自动建信封发送。
    _ds_api = bool((_load_email_config().get("submission") or {}).get("docusign_api_send", False))

    # 收件人校验：内部邮箱由系统发→必填；DocuSign 走人工手动发(未开 API)、仅存档不发→不强制。
    if (email_paths or (ds_paths and _ds_api)) and not recipients:
        raise HTTPException(400, "有文件需由系统发送美代理，收件人不能为空")

    case_volume = row["case_volume"]
    mail = build_agent_email(case_volume, req.recipient_name or "X总/X律师")
    subject = req.subject or mail["subject"]
    body = req.body or mail["body"]
    # 代理所（开 API 自动发时决定用哪个 DocuSign 账号；env6 取回须用同一账号）
    agent_firm = (fields.get("filing_extra") or {}).get("agent_firm") or ""

    # 3a) DocuSign 组：
    #   未开 API(默认，当前) → 只登记 ds_paths、不发（人工手动发 DocuSign），envelope_id=None；
    #   开了 API → 按代理所选账号(Metis/Poseidon/Porus)建信封自动发。
    envelope_id = None
    if ds_paths and _ds_api:
        _dcfg_all = _docusign.load_config()
        # 拦截：代理所未配 DocuSign 账号（如 Lai Runzhi）却设成 DocuSign 通道 → 拒绝，避免误用别所账号
        if not _docusign.firm_uses_docusign(_dcfg_all, agent_firm):
            raise HTTPException(400, f"代理所「{agent_firm or '未指定'}」不走 DocuSign（未配 DocuSign 账号）；"
                                     f"请把以下文件改为内部邮箱或仅存档后重发：{', '.join(p.name for p in ds_paths)}")
        try:
            dcfg = _docusign.resolve_account(_dcfg_all, agent_firm)
            dauth = _docusign.get_access_token(dcfg)
            signer = {"name": (req.signer_name or "").strip() or recipients[0], "email": recipients[0]}
            ds_docs = [{"path": str(p), "kind": _docusign_kind(p, docs)} for p in ds_paths]
            envelope_id = _docusign.send_envelope(
                dcfg, dauth, ds_docs, signer,
                email_subject=subject, anchor=dcfg.get("anchor", "Signature"),
                date_anchor=dcfg.get("date_anchor"),
                anchor_x=dcfg.get("anchor_x_offset", 0),
                anchor_y=dcfg.get("anchor_y_offset", 0),
                anchor_units=dcfg.get("anchor_units", "pixels"),
                anchor_case_sensitive=dcfg.get("anchor_case_sensitive", True),
                anchor_whole_word=dcfg.get("anchor_whole_word", True),
                anchor_offsets=dcfg.get("anchor_offsets"))
        except Exception as exc:
            raise HTTPException(502, f"DocuSign 发送失败（任务保留 pending，成品已存 final/）：{exc}")

    # 3b) 内部邮箱组 → SMTP 附件发美代理
    if email_paths:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        for p in email_paths:
            part = MIMEApplication(p.read_bytes())
            part.add_header("Content-Disposition", "attachment", filename=("utf-8", "", p.name))
            msg.attach(part)
        account_cfg, _cc = _filing_send_config(agent_firm)   # 发美代理发件人按代理所切换
        try:
            _send_smtp(msg, account_cfg, recipients, req.cc or None)
        except Exception as exc:
            raise HTTPException(502, f"邮件发送失败（任务保留 pending，成品已存 final/）：{exc}")

    # 3c) 先归档：把「仅存档」件（不需签字、不发美代理，如说明书/权要/附图定稿）复制进案号上传目录，
    #     环节7 上传包 = 这些归档件 + 环节6 回收的签署版。签字件不在此复制（其签署版由环节6 落入同目录）。
    staged = []
    if archive_paths:
        up_dir = Path(__file__).resolve().parents[2] / "uspto_upload" / case_volume
        try:
            up_dir.mkdir(parents=True, exist_ok=True)
            for p in archive_paths:
                shutil.copy2(str(p), str(up_dir / p.name))
                staged.append(p.name)
        except Exception as exc:
            warnings.append(f"仅存档件归档到上传目录失败：{exc}")

    # 3d) 固定版额外归档到网络盘：{base}\{码}\{组内号}\{案号}\，并按用途分子文件夹便于后期核销：
    #     发美代理\ = 发给美代理需回签的件（DocuSign + 内部邮箱通道）；仅存档\ = 不发、直接进上传包的件。
    #     码=案号前5位、组内号=案号前10位（同 OA 目录约定）。base 可配，缺省 Z:\upload_USPTO。best-effort。
    _arch_base = (_load_email_config().get("submission") or {}).get("uspto_upload_archive_base", r"Z:\upload_USPTO")
    if _arch_base and len(case_volume) >= 10:
        try:
            arch_root = Path(_arch_base) / case_volume[:5] / case_volume[:10] / case_volume
            sent_dir = arch_root / "发美代理"      # 需回签，后期核销比对
            sent_dir.mkdir(parents=True, exist_ok=True)
            for p in (ds_paths + email_paths):
                shutil.copy2(str(p), str(sent_dir / p.name))
            if archive_paths:
                only_dir = arch_root / "仅存档"
                only_dir.mkdir(parents=True, exist_ok=True)
                for p in archive_paths:
                    shutil.copy2(str(p), str(only_dir / p.name))
        except Exception as exc:
            warnings.append(f"固定版归档到 {_arch_base} 失败：{exc}")

    # 4) 落库 done + 存编辑后的 fields + 插 agent_followup（供环节6 跟进美代理回邮）
    execute_params(
        "UPDATE submission_tasks SET status='done', fields_json=%s, confirmed_at=%s, updated_at=%s WHERE id=%s",
        (json.dumps(fields, ensure_ascii=False), now, now, task_id))
    followup_fields = json.dumps({
        "source_task_id": task_id, "files": [p.name for p in attach_paths],
        "sent_to": recipients, "sent_cc": req.cc, "sent_at": now,
        "channels": ch_map,                          # {文件名: docusign|email|archive}
        "docusign_files": [p.name for p in ds_paths],
        "email_files": [p.name for p in email_paths],
        "archive_files": [p.name for p in archive_paths],   # 仅存档、未发送
        "envelope_id": envelope_id,                  # DocuSign 信封号（环节6 取签署版用）
        "docusign_firm": agent_firm,                 # 代理所（env6 取回须用同一 DocuSign 账号）
    }, ensure_ascii=False)
    exist = execute_params(
        "SELECT id FROM submission_tasks WHERE task_type='agent_followup' AND case_volume=%s",
        (case_volume,))
    if exist:
        execute_params(
            "UPDATE submission_tasks SET fields_json=%s, status='pending', updated_at=%s WHERE id=%s",
            (followup_fields, now, exist[0]["id"]))
        followup_id = exist[0]["id"]
    else:
        followup_id = str(uuid.uuid4())
        execute_params(
            "INSERT INTO submission_tasks (id, task_type, case_volume, fields_json, contact_email, status, created_at) "
            "VALUES (%s, 'agent_followup', %s, %s, %s, 'pending', %s)",
            (followup_id, case_volume, followup_fields, row.get("contact_email"), now))

    # QA 操作留痕（修改痕迹+时长）：best-effort，不影响发送。env5 责任人=递交人 filer_email
    try:
        from submission.qa_log import append as _qa_append, build_op_record as _qa_build
        _qa_append(_qa_build("filing", case_volume, row.get("filer_email"), req.qa))
    except Exception:
        pass

    return {"ok": True, "task_id": task_id, "status": "done", "sent_to": recipients,
            "files": [p.name for p in attach_paths], "followup_task_id": followup_id, "warnings": warnings}


@app.post("/api/submission/filing/{task_id}/send-reviewer")
def send_reviewer_link(task_id: str, req: SendReviewerReq):
    """把当前递交页链接发给审核人（下拉/手填收件人）。与「发美代理」并列，不改任务状态。"""
    row = _load_submission_task(task_id)
    recipients = [r.strip() for r in req.recipients if r and r.strip()]
    if not recipients:
        raise HTTPException(400, "审核人收件人不能为空")
    cc = [c.strip() for c in (req.cc or []) if c and c.strip()]
    case_volume = row["case_volume"]
    link = f"{_filing_review_base()}/submission/filing/{task_id}"
    account_cfg, _cc = _submission_send_config()
    msg = MIMEMultipart()
    msg["Subject"] = f"【US递交-待审核】{case_volume} 递交文件"
    body = (req.body or "").strip()
    if body:
        # 操作员自定义正文（前端已把链接填进正文）：转义 → 兼容旧【在线审核链接】占位 →
        # 裸 http(s) URL 自动变可点（负向后视避开已在 <a href='…'> 里的 URL）→ 换行转 <br>
        link_html = f"<a href='{link}'>{link}</a>"
        esc = body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if "【在线审核链接】" in esc:
            esc = esc.replace("【在线审核链接】", link_html)
        esc = re.sub(r"(?<!['\">=])(https?://[^\s<]+)", r"<a href='\1'>\1</a>", esc)
        html = esc.replace("\n", "<br>")
    else:
        html = (f"<p>案号 <b>{case_volume}</b> 的递交文件已生成，请在线审核 POA/Transmittal/ADS 等：</p>"
                f"<p><a href='{link}'>{link}</a></p><p>本邮件由系统自动发送。</p>")
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        _send_smtp(msg, account_cfg, recipients, cc or None)
    except Exception as exc:
        raise HTTPException(502, f"审核链接发送失败：{exc}")
    return {"ok": True, "sent_to": recipients, "cc": cc, "link": link}


@app.post("/api/submission/filing/{task_id}/skip")
def skip_filing_task(task_id: str):
    _load_submission_task(task_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_params("UPDATE submission_tasks SET status='skipped', updated_at=%s WHERE id=%s", (now, task_id))
    return {"ok": True, "task_id": task_id, "status": "skipped"}


# ── 环节7「待上传 USPTO」pull 消费：环节6 全部签署件回齐(agent_followup done)时，
#    销账函数建 task_type='uspto_upload'(pending)；环节7 扫 pending 拉起上传、传完 mark-uploaded。
@app.get("/api/submission/uspto-uploads")
def list_uspto_uploads(status: str = "pending"):
    """列「待上传 USPTO」任务（默认 pending）。供环节7 pull 拉取；每条含案号 + 归档目录 + 文件清单。"""
    statuses = [s.strip() for s in status.split(",") if s.strip()] or ["pending"]
    placeholders = ",".join(["%s"] * len(statuses))
    rows = execute_params(
        f"SELECT id, case_volume, fields_json, status, created_at, updated_at "
        f"FROM submission_tasks WHERE task_type='uspto_upload' AND status IN ({placeholders}) "
        f"ORDER BY created_at ASC", tuple(statuses))
    out = []
    for r in rows:
        for k in ("created_at", "updated_at"):
            if r.get(k) is not None:
                r[k] = str(r[k])
        try:
            fj = json.loads(r.get("fields_json") or "{}")
        except Exception:
            fj = {}
        r.pop("fields_json", None)
        out.append({**r, "archived_dir": fj.get("archived_dir"),
                    "files": fj.get("files") or [], "ready_at": fj.get("ready_at")})
    return {"tasks": out}


@app.post("/api/submission/uspto-uploads/{task_id}/mark-uploaded")
def mark_uspto_uploaded(task_id: str):
    """环节7 上传 Patent Center 成功后置 uspto_upload=done（避免重复上传；环节8 复审接续）。"""
    row = _load_submission_task(task_id)
    if row["task_type"] != "uspto_upload":
        raise HTTPException(400, f"任务 {task_id} 不是 uspto_upload（实际 {row['task_type']}）")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_params(
        "UPDATE submission_tasks SET status='done', confirmed_at=%s, updated_at=%s WHERE id=%s",
        (now, now, task_id))
    return {"ok": True, "task_id": task_id, "status": "done"}


# ═══ 环节8：上传 USPTO 后的文件预览页（只读，纯增量，不影响其它路由）═══
# 环节7 上传成功后由 env7 机（D:\up_uspto）发链接邮件；链接指向本页，预览该案上传到
# USPTO 的文件（来自 Z 盘归档 {base}\{码}\{组内号}\{案号}\ 的 仅存档\ + 签署版\）。
USPTO_REVIEW_HTML = WEB_DIR / "uspto_review.html"
_USPTO_REVIEW_SUBS = ("仅存档", "签署版")   # 上传包来源；发美代理\ 是未签发出版，不在预览范围


def _uspto_zcase_root(case_volume: str) -> str:
    """该案在 Z 盘的归档根：{base}\\{码}\\{组内号}\\{案号}（码=前5位、组内号=前10位，同 OA/env7 约定）。"""
    base = (_load_email_config().get("submission") or {}).get("uspto_upload_archive_base") or r"Z:\upload_USPTO"
    cv = (case_volume or "").strip()
    return os.path.join(base, cv[:5], cv[:10], cv)


def _uspto_safe_name(name: str) -> str:
    """只允许纯文件名（防路径穿越）：无路径分隔符、非 . / ..，否则 400。"""
    n = (name or "").strip()
    if not n or n in (".", "..") or "/" in n or "\\" in n or os.path.basename(n) != n:
        raise HTTPException(400, "非法文件名")
    return n


@app.get("/submission/uspto-review/{case_volume}")
def uspto_review_page(case_volume: str):
    """环节8 预览页（web/uspto_review.html）；案号由前端从 URL 读取后拉 /files。"""
    if not USPTO_REVIEW_HTML.exists():
        return PlainTextResponse(
            f"预览页前端尚未部署（web/uspto_review.html 缺失）。案号: {case_volume}\n"
            f"可先用 GET /api/submission/uspto-review/{case_volume}/files 查看文件清单。",
            status_code=200)
    return FileResponse(str(USPTO_REVIEW_HTML), media_type="text/html; charset=utf-8")


@app.get("/api/submission/uspto-review/{case_volume}/files")
def uspto_review_files(case_volume: str):
    """列该案 Z 盘 仅存档\\ + 签署版\\ 下的文件（分组、名字、大小）。目录缺失返回空组，不报错。"""
    root = _uspto_zcase_root(case_volume)
    groups = []
    for sub in _USPTO_REVIEW_SUBS:
        d = os.path.join(root, sub)
        items = []
        if os.path.isdir(d):
            for n in sorted(os.listdir(d)):
                fp = os.path.join(d, n)
                if os.path.isfile(fp):
                    items.append({"name": n, "size": os.path.getsize(fp),
                                  "is_pdf": n.lower().endswith(".pdf")})
        groups.append({"sub": sub, "files": items})
    return {"case_volume": case_volume, "root": root, "groups": groups}


@app.get("/api/submission/uspto-review/{case_volume}/file")
def uspto_review_file(case_volume: str, sub: str, name: str):
    """返回单个文件：PDF 内联预览、其余作附件下载。sub 限 仅存档/签署版，name 防穿越。"""
    if sub not in _USPTO_REVIEW_SUBS:
        raise HTTPException(400, f"非法子目录：{sub}")
    safe = _uspto_safe_name(name)
    fp = os.path.join(_uspto_zcase_root(case_volume), sub, safe)
    if not os.path.isfile(fp):
        raise HTTPException(404, "文件不存在")
    if safe.lower().endswith(".pdf"):
        return FileResponse(fp, media_type="application/pdf", content_disposition_type="inline")
    return FileResponse(fp, filename=safe)   # 非 PDF → 下载


if __name__ == "__main__":
    print(f"启动汇报信审核服务: http://localhost:8501", file=sys.stderr)
    print(f"  - 模板目录: {TEMPLATES_DIR}", file=sys.stderr)
    print(f"  - 审核页:   {PROTOTYPE_HTML}", file=sys.stderr)
    uvicorn.run(app, host="0.0.0.0", port=8501)
