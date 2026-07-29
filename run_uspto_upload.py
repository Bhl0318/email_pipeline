#!/usr/bin/env python3
"""环节7（定时脚本）：扫「待上传」案件 → 自动触发上传 USPTO Patent Center（不递交）。

条件（用户定）：`uspto_upload` = pending **且** 同案 `agent_followup` = done（全部签署件回齐）。
满足即自动组包、驱动 Patent Center 上传（代码操作浏览器，无需人工网页点击），传完置
`uspto_upload` = done（避免重复；环节8 复审接续）。与环节6 两条抓件线一样**独立、各自定时、不并 main.py**。

⚠️ 现状与前置（patent_center_ui.py 尚在联调，未开 --live 前只 dry-run 规划）：
  1. patent_center_ui.run() 结尾的 input() 需去掉（否则卡住）、并返回成功/失败；选择器需按真实页面稳定；
  2. Okta 登录要 OTP（可走钉钉机器人回复，仍需人递一次码）——非纯无人；
  3. 上传包需完整：uspto_upload/{案号}/ 目前只有美代理签回件，说明书/权要/附图**定稿**（环节5 上传）
     需并入才齐（下方 _build_upload_data 已留 TODO）。
  默认 **dry-run**（只规划、不驱动浏览器、不置 done）；补齐上述后加 --live 才真正上传。
  ⚠️ 环节7 严禁 AI，纯确定性代码；本脚本连真实 DB/USPTO，按项目规矩只提交、由人工在受控环境发起。

用法：
  python3 run_uspto_upload.py            # dry-run：列待上传 + 规划，不上传、不改库
  python3 run_uspto_upload.py --live     # 真正驱动 Patent Center 上传并销账（前置补齐后）
"""
import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ROOT = os.path.join(SCRIPT_DIR, "uspto_upload")
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
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
    """组 Patent Center 上传载荷 {submission_type, practitioner, ads_path, other_paths}。
    文件取 archived_dir 里现有件：名字含 ADS 的作 ads_path，其余 other_paths。
    TODO：说明书/权要/附图**定稿**（环节5 上传，不在 archived_dir）需并入才是完整上传包。"""
    d = case["archived_dir"]
    files = []
    if os.path.isdir(d):
        files = sorted(os.path.join(d, n) for n in os.listdir(d) if os.path.isfile(os.path.join(d, n)))
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
              f"其余 {len(data['other_paths'])} 件；归档目录 {c['archived_dir']}")
        if not files:
            print("  ⚠️ 归档目录无文件，跳过。")
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


if __name__ == "__main__":
    run(live=("--live" in sys.argv))
