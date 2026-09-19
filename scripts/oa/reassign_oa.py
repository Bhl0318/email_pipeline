#!/usr/bin/env python3
"""按案号补发 OA 分配（独立脚本）。

用途：之前有些案子因涉及新颖性/创造性被跳过分配（未进待分配、未发分配链接）。
本脚本按案号把它们重新纳入分配：进待分配库 → 读该案审意生成 AI 报告/方案 → 发分配链接给对应人。
流程与主流水线（read_email.dispatch_oa 立项后半段）一致，复用同一批函数：
  add_pending / build_case_report / build_assignment_schemes / render_schemes_md / save_report /
  build_assign_notifies（收件人路由：补正类→杨姣、20608→王志刚、5*/6*/8*→杨姣、其余→薛虹，均抄送海灵）。

用法：
  python3 reassign_oa.py <案号> [<案号> ...] [--region CN|US|EP] [--force] [--dry-run]

  --force    该案立项行即使已在待分配/已分配，也重新生成报告并再发一次分配链接
  --region   覆盖地区判定（默认：project_type 含「中国」→CN，否则 US）；影响报告取申请文件/地区标注
  --dry-run  只打印将要做什么，不写库、不发邮件

说明：
  * 会真实写库 + 发邮件，属有副作用脚本，请在生产/受控环境运行。
  * 审意文件从 attachment/{案号}/ 读（与主流程同源）；缺件则报告第四类标注待补，但分配链接照发。
  * 分配链接依赖 pipeline_config.json 的 oa_assign_base_url（为空则不带链接，仅打印提示）。
"""
import os
import sys
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def _load_pipeline_env():
    """把 pipeline_config.json 的分配相关配置注入环境变量（与 main.py 一致），供 build_assign_notifies 读。"""
    try:
        with open(os.path.join(SCRIPT_DIR, "..", "pipeline_config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"[补发] 读取 pipeline_config.json 失败（分配链接可能不带 URL）: {e}", file=sys.stderr)
        cfg = {}
    base = (cfg.get("oa_assign_base_url") or "").strip()
    if base:
        os.environ["OA_ASSIGN_BASE_URL"] = base
    os.environ["OA_SEND_ASSIGN_LINK"] = "0" if cfg.get("send_assign_link", True) is False else "1"
    return cfg


def _region_of(project_type, override=""):
    """地区判定：显式覆盖优先；否则 project_type 含「中国」→CN，其余（海外答复及其他）默认 US。"""
    if override:
        return override.upper()
    return "CN" if "中国" in (project_type or "") else "US"


def _fetch_latest_project_row(project, db_execute):
    """查 projects 该案号「最新一次」立项行（按 OA 发文日倒序取第一条）。
    一个案号历年有多次 OA 立项，补发只针对当前这次 OA（一案号一条分配链接），故只取最新一条。
    取不到返回 None。"""
    proj = project.replace("'", "\\'")
    rows = db_execute(
        "SELECT id, project, project_name, project_type, customer, oa_doc_date, "
        "project_deadline, oaNum, oa_remark FROM projects "
        f"WHERE project='{proj}' ORDER BY oa_doc_date DESC, entrust_date DESC LIMIT 1")
    return rows[0] if isinstance(rows, list) and rows else None


def _already_pending(oa_id, db_execute):
    """该立项行是否已在待分配表（oa_assign_task）。"""
    oid = (oa_id or "").replace("'", "\\'")
    rows = db_execute(f"SELECT id FROM oa_assign_task WHERE id='{oid}'")
    return bool(rows) if isinstance(rows, list) else False


def _row_to_item(row, region_override=""):
    """projects 行 → 主流程用的 item（含分配/报告所需字段）。"""
    return {
        "oa_id": row.get("id", ""),
        "project": row.get("project", ""),
        "project_name": row.get("project_name", ""),      # OA类别，兼作路由的 OA类型
        "customer": row.get("customer", ""),
        "region": _region_of(row.get("project_type", ""), region_override),
        "project_deadline": str(row.get("project_deadline", "") or ""),
        "oaNum": row.get("oaNum", ""),
        "oa_remark": row.get("oa_remark", ""),
        "notification_type": "",
    }


def _collect_items(projects, region_override, force, db_execute):
    """每个案号取「最新一次」立项行 → 过滤出要补发的 item（一案号最多一条）。
    默认：该行已在待分配则跳过（除非 --force）。"""
    items = []
    for proj in projects:
        row = _fetch_latest_project_row(proj, db_execute)
        if not row:
            print(f"[补发] {proj}：projects 无立项记录，跳过（该案是否已立项？）", file=sys.stderr)
            continue
        oa_id = row.get("id", "")
        if not oa_id:
            print(f"[补发] {proj}：最新立项行无 id，跳过", file=sys.stderr)
            continue
        pending = _already_pending(oa_id, db_execute)
        if pending and not force:
            print(f"[补发] {proj} [{row.get('project_name','')}]：最新一次 OA 已在待分配，跳过"
                  f"（如需重发加 --force）", file=sys.stderr)
            continue
        item = _row_to_item(row, region_override)
        item["_already_pending"] = pending
        items.append(item)
        print(f"[补发] {proj} [{item['project_name']}] region={item['region']} "
              f"oa_id={oa_id}{'（重发）' if pending else ''} → 待处理", file=sys.stderr)
    return items


def _open_pa_smtp(pa_cfg):
    """打开并认证 PA 账号 SMTP（复用 read_email 的 OAuth2/密码降级逻辑）。"""
    import smtplib
    from read_email import _get_smtp_oauth2_token
    smtp = smtplib.SMTP(pa_cfg["smtp_host"], pa_cfg["smtp_port"])
    smtp.ehlo(); smtp.starttls(); smtp.ehlo()
    token = _get_smtp_oauth2_token(pa_cfg)
    if token:
        auth = f"user={pa_cfg['user']}\x01auth=Bearer {token}\x01\x01"
        try:
            import base64
            smtp.docmd("AUTH", "XOAUTH2 " + base64.b64encode(auth.encode()).decode())
        except smtplib.SMTPAuthenticationError:
            smtp.login(pa_cfg["user"], pa_cfg["password"])
    else:
        smtp.login(pa_cfg["user"], pa_cfg["password"])
    return smtp


def _gen_reports(items, dry_run):
    """为每件生成 AI 报告 + 方案并落 oa_assign_report（分配页打开即秒读）。"""
    from oa_report_ai import build_case_report
    from oa_schemes import build_assignment_schemes, render_schemes_md
    from oa_assign_store import save_report
    for item in items:
        proj = item.get("project", "")
        if dry_run:
            print(f"  [dry-run][报告] {proj}：将读 attachment/{proj}/ 审意生成报告+方案", file=sys.stderr)
            continue
        try:
            md = build_case_report(item)
            sch = build_assignment_schemes(proj, region=item.get("region", ""), report_md=md)
            sec = render_schemes_md(sch)
            if sec:
                md = md.rstrip() + "\n\n" + sec
            save_report(item.get("oa_id", ""), md, sch)
            print(f"  [报告] {proj}：已生成 → oa_assign_report", file=sys.stderr)
        except Exception as e:
            print(f"  [报告] {proj}：生成失败（不影响分配链接）: {e}", file=sys.stderr)


def _send_links(items, dry_run):
    """按收件人路由发分配链接（build_assign_notifies 分组，每收件人一封列出其名下案件）。"""
    from forward_oa import build_assign_notifies, assign_person_name
    plans = [{"item": it} for it in items]
    for it in items:
        who = assign_person_name(it.get("project", ""), it.get("project_name", ""))
        print(f"  [路由] {it.get('project')} [{it.get('project_name')}] → 分配人 {who or '(未匹配)'}",
              file=sys.stderr)
    notifies = build_assign_notifies(plans)
    if not notifies:
        print("  [分配链接] 无可发（OA_ASSIGN_BASE_URL 为空 或 发送开关关闭）——请检查 pipeline_config.json",
              file=sys.stderr)
        return
    if dry_run:
        for nt in notifies:
            print(f"  [dry-run][分配链接] → {nt['to']} 抄送 {', '.join(nt['cc'])}  主题: {nt['subject']}",
                  file=sys.stderr)
            print("      正文:\n" + "\n".join("      " + ln for ln in nt["body"].splitlines()),
                  file=sys.stderr)
        return
    from read_email import load_config
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    pa_cfg = load_config().get("accounts", {}).get("pa")
    if not pa_cfg:
        print("  [分配链接] 未配置 PA 账号，无法发送", file=sys.stderr)
        return
    smtp = _open_pa_smtp(pa_cfg)
    try:
        for nt in notifies:
            msg = MIMEMultipart()
            msg["From"] = pa_cfg["user"]
            msg["To"] = nt["to"]
            if nt["cc"]:
                msg["Cc"] = ", ".join(nt["cc"])
            msg["Subject"] = nt["subject"]
            msg.attach(MIMEText(nt["body"], "plain", "utf-8"))
            try:
                smtp.sendmail(pa_cfg["user"], [nt["to"]] + nt["cc"], msg.as_string())
                print(f"  [分配链接] 已发 → {nt['to']} 抄送 {', '.join(nt['cc'])}", file=sys.stderr)
            except Exception as e:
                print(f"  [分配链接] 发送失败 → {nt['to']}: {e}", file=sys.stderr)
    finally:
        try:
            smtp.quit()
        except Exception:
            pass


def reassign(projects, region_override="", force=False, dry_run=False):
    """主流程：按案号补发分配。"""
    _load_pipeline_env()
    from db_query import execute as db_execute

    items = _collect_items(projects, region_override, force, db_execute)
    if not items:
        print("[补发] 无待处理案件，结束。", file=sys.stderr)
        return 0

    # 1. 进待分配库（已在库的不重复写；force 重发时也不必重写，add_pending 内部按 id 去重）
    if dry_run:
        _new = [it for it in items if not it.get("_already_pending")]
        print(f"  [dry-run][待分配] 将新增 {len(_new)} 件到待分配库", file=sys.stderr)
    else:
        from oa_assign_store import add_pending
        n = add_pending(items)
        print(f"[补发][待分配] 新增 {n} 件到待分配库", file=sys.stderr)

    # 2. 生成 AI 报告 + 方案
    _gen_reports(items, dry_run)

    # 3. 发分配链接
    _send_links(items, dry_run)

    print(f"[补发] 完成：处理 {len(items)} 件（案号 {', '.join(projects)}）"
          + ("（dry-run，未写库/未发信）" if dry_run else ""), file=sys.stderr)
    return len(items)


def main():
    ap = argparse.ArgumentParser(description="按案号补发 OA 分配（进待分配 + 生成报告 + 发分配链接）")
    ap.add_argument("projects", nargs="+", help="案号（可多个）")
    ap.add_argument("--region", default="", help="覆盖地区判定 CN|US|EP（默认按 project_type 推）")
    ap.add_argument("--force", action="store_true", help="已在待分配/已分配也重新生成报告并再发链接")
    ap.add_argument("--dry-run", action="store_true", help="只打印，不写库不发信")
    args = ap.parse_args()
    reassign(args.projects, region_override=args.region, force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
