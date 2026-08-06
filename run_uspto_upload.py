#!/usr/bin/env python3
"""环节7（定时脚本）：扫「待上传」案件 → 自动触发上传 USPTO Patent Center（不递交）。

条件（用户定）：`uspto_upload` = pending **且** 同案 `agent_followup` = done（全部签署件回齐）。
满足即自动组包、驱动 Patent Center 上传（代码操作浏览器，无需人工网页点击），传完置
`uspto_upload` = done（避免重复；环节8 复审接续）。与环节6 两条抓件线一样**独立、各自定时、不并 main.py**。

⚠️ 现状与前置（patent_center_ui.py 尚在联调，未开 --live 前只 dry-run 规划）：
  1. patent_center_ui.run() 结尾的 input() 需去掉（否则卡住）、并返回成功/失败；选择器需按真实页面稳定；
  2. Okta 登录要 OTP（可走钉钉机器人回复，仍需人递一次码）——非纯无人；
  3. 上传包完整性：环节5 递交人上传全套 USPTO 文档，不签字的（说明书/权要/附图定稿等）选「仅存档」
     环节5 归档到 Z:\\upload_USPTO\\{码}\\{组内号}\\{案号}\\仅存档\\，签署版由环节6 落 签署版\\ →
     上传包 = 仅存档\\ + 签署版\\（发美代理\\ 是未签发出版，不上传）。
  默认 **dry-run**（只规划、不驱动浏览器、不置 done）；补齐上述后加 --live 才真正上传。
  ⚠️ 环节7 严禁 AI，纯确定性代码；本脚本连真实 DB/USPTO，按项目规矩只提交、由人工在受控环境发起。

用法：
  python3 run_uspto_upload.py                  # 单次 dry-run：列待上传 + 规划，不上传、不改库
  python3 run_uspto_upload.py --live           # 单次：真正驱动 Patent Center 上传并销账
  python3 run_uspto_upload.py --loop           # 常驻轮询（默认 60s/轮），单次 dry-run 规划
  python3 run_uspto_upload.py --loop 30 --live # 常驻轮询：每 30s 扫一次，有齐的就真上传并销账
"""
import os
import sys
import json
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ROOT = os.path.join(SCRIPT_DIR, "uspto_upload")
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
# patent_center_ui.py 位置：优先与本脚本同目录（如新机 D:\up_uspto 平铺部署：
# run_uspto_upload.py / patent_center_ui.py / sendInfobyDing.py 同级），
# 找不到再回退仓库内 us_submission/seleTest（开发仓布局）。
if os.path.exists(os.path.join(SCRIPT_DIR, "patent_center_ui.py")):
    SELE_DIR = SCRIPT_DIR
else:
    SELE_DIR = os.path.join(REPO_ROOT, "us_submission", "seleTest")

# DB（atw.submission_tasks），复用 report 端 db_query。best-effort。
try:
    sys.path.insert(0, os.path.join(SCRIPT_DIR, "scripts", "report"))
    from db_query import execute_params as _db_exec
    _DB_OK = True
except Exception as exc:  # noqa: BLE001
    print(f"[uspto-upload] DB 不可用：{exc}", file=sys.stderr)
    _DB_OK = False

# subject_matter → Patent Center 申请类型
_SUBMISSION_TYPE = {"UTL": "Utility Nonprovisional", "371": "Utility Nonprovisional",
                    "DES": "Design"}


def _archive_base():
    """Z 盘归档基路径：email_config.json 的 submission.uspto_upload_archive_base，缺省 Z:\\upload_USPTO。"""
    try:
        with open(os.path.join(SCRIPT_DIR, "scripts", "report", "email_config.json"), encoding="utf-8") as f:
            return ((json.load(f).get("submission") or {}).get("uspto_upload_archive_base")) or r"Z:\upload_USPTO"
    except Exception:
        return r"Z:\upload_USPTO"


def _zcase_root(case_volume):
    """该案在 Z 盘的归档根：{base}\\{码}\\{组内号}\\{案号}（码=前5位、组内号=前10位，同 OA 约定）。"""
    return os.path.join(_archive_base(), case_volume[:5], case_volume[:10], case_volume)


def _ready_cases():
    """待上传：uspto_upload=pending 且同案 agent_followup=done。返回 [{upload_id, case_volume, up_fj}]。"""
    rows = _db_exec(
        "SELECT u.id AS upload_id, u.case_volume AS case_volume, u.fields_json AS up_fj "
        "FROM submission_tasks u "
        "JOIN submission_tasks a "
        "  ON a.case_volume = u.case_volume AND a.task_type='agent_followup' AND a.status='done' "
        "WHERE u.task_type='uspto_upload' AND u.status='pending' "
        "ORDER BY u.created_at ASC") or []
    out = []
    for r in rows:
        try:
            fj = json.loads(r.get("up_fj") or "{}")
        except Exception:
            fj = {}
        out.append({"upload_id": r["upload_id"], "case_volume": r["case_volume"],
                    "archived_dir": fj.get("archived_dir") or os.path.join(OUTPUT_ROOT, r["case_volume"]),
                    "files": fj.get("files") or []})
    return out


def _submission_type(case_volume):
    """从同案 filing_preparation 的 fields_json.subject_matter 推申请类型（缺省 Utility Nonprovisional）。"""
    rows = _db_exec(
        "SELECT fields_json FROM submission_tasks "
        "WHERE task_type='filing_preparation' AND case_volume=%s ORDER BY created_at DESC LIMIT 1",
        (case_volume,)) or []
    sm = ""
    if rows:
        try:
            sm = (json.loads(rows[0].get("fields_json") or "{}") or {}).get("subject_matter") or ""
        except Exception:
            sm = ""
    return _SUBMISSION_TYPE.get(sm.upper(), "Utility Nonprovisional")


def _build_upload_data(case):
    """从 Z 盘归档目录取上传件：{base}\\{码}\\{组内号}\\{案号}\\ 下的
    「仅存档」(不签的定稿：说明书/权要/附图等) + 「签署版」(环节6 回收的签署版)。
    「发美代理」是未签发出版，不上传。名字含 ADS 的作 ads_path，其余 other_paths。"""
    root = _zcase_root(case["case_volume"])
    files = []
    for sub in ("仅存档", "签署版"):
        d = os.path.join(root, sub)
        if os.path.isdir(d):
            files += sorted(os.path.join(d, n) for n in os.listdir(d) if os.path.isfile(os.path.join(d, n)))
    ads = [f for f in files if "ADS" in os.path.basename(f).upper()]
    others = [f for f in files if f not in ads]
    return {
        "submission_type": _submission_type(case["case_volume"]),
        "practitioner": None,                 # None=按 practitioner 列表序号1；后续可从 agent_info 带
        "ads_path": ads[0] if ads else None,
        "other_paths": others,
    }, files


def _mark_uploaded(upload_id, now):
    _db_exec("UPDATE submission_tasks SET status='done', confirmed_at=%s, updated_at=%s WHERE id=%s",
             (now, now, upload_id))


def _notify_review(case_volume):
    """环节8：上传成功后发预览链接邮件给指定人（best-effort，失败只记日志、不影响 done）。
    链接指向 report_server 预览页；收件人/base 从 email_config.json 取（缺省 hailing.bi + 8501）。"""
    try:
        import submission_mailer as _mailer   # scripts/report 已在 sys.path（db_query 同目录）
        link = f"{_mailer.review_base_url()}/submission/uspto-review/{case_volume}"
        recipients = _mailer.uspto_review_recipients()
        html = (f"<p>案号 <b>{case_volume}</b> 已上传至 USPTO Patent Center（存草稿，未递交）。</p>"
                f"<p>请点击以下链接预览本案实际上传的全套文件，核对后在 Patent Center 正式递交：</p>"
                f"<p><a href='{link}'>{link}</a></p>"
                f"<p>本邮件由系统自动发送。</p>")
        _mailer.send_html(f"【US递交-已上传待复审】{case_volume}", html, recipients)
        print(f"  ✉️ 已发预览链接邮件给 {', '.join(recipients)}")
    except Exception as exc:  # noqa: BLE001
        print(f"  ⚠️ 预览链接邮件发送失败（不影响上传/销账）：{exc}", file=sys.stderr)


def run(live=False):
    if not _DB_OK:
        print("[uspto-upload] DB 不可用，退出。")
        return
    cases = _ready_cases()
    print(f"待上传案件（uspto_upload=pending 且 agent_followup=done）：{len(cases)} 个")
    if not cases:
        return

    runner = None
    if live:
        try:
            sys.path.insert(0, SELE_DIR)
            import patent_center_ui as runner   # noqa: F401
        except Exception as exc:  # noqa: BLE001
            print(f"[uspto-upload] 无法加载 patent_center_ui（联调中？）：{exc}；本次仅规划不上传。")
            live = False

    import datetime
    for c in cases:
        data, files = _build_upload_data(c)
        print(f"\n案 {c['case_volume']}：类型={data['submission_type']} "
              f"ADS={os.path.basename(data['ads_path']) if data['ads_path'] else '（缺）'} "
              f"其余 {len(data['other_paths'])} 件；Z 盘目录 {_zcase_root(c['case_volume'])}")
        if not files:
            print("  ⚠️ Z 盘归档目录(仅存档/签署版)无文件，跳过。")
            continue
        if not data["ads_path"]:
            print("  ⚠️ 未找到 ADS 件，跳过（上传需 ADS）。")
            continue
        if not live:
            print("  [dry-run] 满足条件，将触发上传（加 --live 且 UI 联调通后真正执行）。")
            continue
        try:
            runner.run(data, dry_run=False)
        except Exception as exc:  # noqa: BLE001
            print(f"  ❌ 上传失败：{exc}（保留 pending 待重试/人工）")
            continue
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _mark_uploaded(c["upload_id"], now)
        print(f"  ✅ 已上传（存草稿）并置 uspto_upload=done（{c['case_volume']}）。")
        _notify_review(c["case_volume"])   # 环节8：发预览链接邮件（best-effort）


def run_loop(interval, live=False):
    """常驻轮询：每 interval 秒扫一轮待上传案。单轮内异常不退整体，continue 下一轮。
    单案上传失败留 pending，下轮自动重试。Ctrl+C / SIGTERM 退出。"""
    if not _DB_OK:
        print("[uspto-upload] DB 不可用，无法轮询，退出。")
        return
    _log_hdr = f"env7 轮询启动：每 {interval}s 扫一次「附件齐全的待上传案」" \
               f"（{'真上传' if live else 'dry-run 规划'}，Ctrl+C 退出）"
    print(_log_hdr)
    while True:
        try:
            run(live=live)
        except KeyboardInterrupt:
            print("\n[uspto-upload] 收到中断，退出轮询。")
            return
        except Exception as exc:  # noqa: BLE001
            print(f"[uspto-upload] 本轮异常（忽略，继续下一轮）：{exc}")
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[uspto-upload] 收到中断，退出轮询。")
            return


def _parse_interval(argv, default=60):
    """从 argv 取 --loop 后紧跟的秒数；无数字则用默认。返回 (loop?, interval)。"""
    if "--loop" not in argv:
        return False, default
    i = argv.index("--loop")
    if i + 1 < len(argv):
        try:
            return True, max(5, int(argv[i + 1]))
        except ValueError:
            pass
    return True, default


if __name__ == "__main__":
    _live = "--live" in sys.argv
    _loop, _interval = _parse_interval(sys.argv)
    if _loop:
        run_loop(_interval, live=_live)
    else:
        run(live=_live)
