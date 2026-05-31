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
import sys
import re
import base64
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent                       # DS/汇报信流程/
TEMPLATES_DIR = ROOT / "templates" / "md"
WEB_DIR = ROOT / "web"
PROTOTYPE_HTML = WEB_DIR / "prototype.html"
EMAIL_CONFIG_PATH = SCRIPT_DIR / "email_config.json"

sys.path.insert(0, str(SCRIPT_DIR))
from db_query import execute_params  # noqa: E402


app = FastAPI(title="汇报信审核服务", version="0.1")
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# output/ 目录只读挂载，供审核页预览官文 PDF
_OUTPUT_DIR_FOR_MOUNT = ROOT / "output"
_OUTPUT_DIR_FOR_MOUNT.mkdir(parents=True, exist_ok=True)
app.mount("/output", StaticFiles(directory=str(_OUTPUT_DIR_FOR_MOUNT)), name="output")


# ─── 健康检查 ────────────────────────────────────────────

@app.get("/")
def root():
    return {"service": "report-review", "version": "0.1", "status": "ok"}


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
    if project:
        try:
            from enrich_report import enrich_cn_fields
            enriched = enrich_cn_fields(project)
        except Exception as e:
            print(f"[warn] task {task_id} enrich 失败: {e}", file=sys.stderr)

    # 合并优先级（低→高）：projects 默认 < enrich 主数据 < fields_json（审核人改过的最优先）
    # 注：fields_json 里值为 ""/"请提供"/None 的是占位，不应覆盖 enrich 查到的真实值
    effective_user = {k: v for k, v in user_fields.items() if v not in ("", "请提供", None)}
    merged = {**p_defaults, **enriched, **effective_user}

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
    }


# ─── 模板内容 ────────────────────────────────────────────

@app.get("/templates/{name}")
def get_template(name: str):
    """返回 templates/md/{name} 原文。"""
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(400, "invalid template name")
    p = TEMPLATES_DIR / name
    if not p.is_file():
        raise HTTPException(404, f"template {name} not found")
    return PlainTextResponse(p.read_text(encoding="utf-8"), media_type="text/plain; charset=utf-8")


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


def _safe_filename(fields):
    """按 example/ 的命名拼汇报信文件名（去掉文件名非法字符）"""
    issue = (fields.get("发文日期") or "").replace("/", "-")
    ntype = fields.get("通知类型") or "汇报信"
    if not ntype.endswith("转达"):
        ntype += "转达"
    cref = fields.get("客户案号") or "请提供"
    oref = fields.get("代理所案号") or ""
    name = f"{issue}-{ntype}（贵方案号：{cref}；代理所案号：{oref}）"
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
        msg["To"] = ", ".join(recipients)
        if cc_addrs:
            msg["Cc"] = ", ".join(cc_addrs)
        all_rcpts = recipients + (cc_addrs or [])
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


class PreviewSendReq(BaseModel):
    fields: dict
    attach_pdf: bool = True


@app.post("/api/tasks/{task_id}/preview-send")
def preview_send(task_id: str, req: PreviewSendReq):
    """发送前的预览：返回 from/recipients/subject/附件清单，供 modal 显示。"""
    base = _safe_filename(req.fields) or task_id
    subject = f"Privileged & Confidential-{base}"

    # 官文 PDF 清单
    source_attachments = []
    rows = execute_params("SELECT source_attachments FROM report_tasks WHERE id = %s", (task_id,))
    if rows and rows[0].get("source_attachments"):
        try:
            source_attachments = json.loads(rows[0]["source_attachments"])
        except Exception:
            pass

    # 收发件配置
    try:
        cfg = _load_email_config()
        send_cfg = cfg.get("accounts", {}).get("pa") or {}
        notif = cfg.get("notification", {})
        recipients = notif.get("recipients", [])
        cc_addrs = notif.get("cc", [])
    except Exception as e:
        raise HTTPException(500, f"读 email_config.json 失败: {e}")

    return {
        "from": send_cfg.get("user", ""),
        "recipients": recipients,
        "cc": cc_addrs,
        "subject": subject,
        "report_pdf_filename": (base + ".pdf") if req.attach_pdf else None,
        "source_attachments": [{"path": rel, "filename": rel.rsplit("/", 1)[-1]} for rel in source_attachments],
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
    base = _safe_filename(fields) or task_id
    project = fields.get("代理所案号") or task_id
    case_dir = OUTPUT_DIR / re.sub(r'[\\/:*?"<>|\r\n]', "_", project).strip()
    out = {"task_id": task_id}

    # 查官文 PDF 附件路径
    source_attachments = []
    sa_rows = execute_params("SELECT source_attachments FROM report_tasks WHERE id = %s", (task_id,))
    if sa_rows and sa_rows[0].get("source_attachments"):
        try:
            source_attachments = json.loads(sa_rows[0]["source_attachments"])
        except Exception:
            pass

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

    # 3) 构 MIME，写 .eml 备份
    subject = f"Privileged & Confidential-{base}"
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
        send_cfg = cfg.get("accounts", {}).get("pa")
        notif = cfg.get("notification", {})
        recipients = notif.get("recipients", [])
        cc_addrs = notif.get("cc", [])
        if not send_cfg:
            raise RuntimeError("email_config.json 缺 accounts.pa")
        if not recipients:
            raise RuntimeError("email_config.json 缺 notification.recipients")

        _send_smtp(mime_msg, send_cfg, recipients, cc_addrs)

        # 发送成功才更新 status
        execute_params(
            "UPDATE report_tasks SET status = 'done', reviewer = %s WHERE id = %s",
            (req.reviewer or None, task_id),
        )
        out["ok"] = True
        out["status"] = "done"
        out["sent_to"] = recipients
        out["sent_from"] = send_cfg["user"]
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


if __name__ == "__main__":
    print(f"启动汇报信审核服务: http://localhost:8501", file=sys.stderr)
    print(f"  - 模板目录: {TEMPLATES_DIR}", file=sys.stderr)
    print(f"  - 审核页:   {PROTOTYPE_HTML}", file=sys.stderr)
    uvicorn.run(app, host="0.0.0.0", port=8501)
