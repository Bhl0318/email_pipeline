#!/usr/bin/env python3
"""email_pipeline 统一调度入口。

一封邮件只读一次、只分类一次，扇出给「OA 立项」和「汇报信」两个下游 sink。
解决两条原流程各自读同一 docketing 邮箱、各自归档到 TEST_AUTO 抢邮件的冲突。

流程：
  ① 读邮件 + 分类（一次）—— 用 report 副本（其分类是 OA 的超集，多 message_id 字段）
  ② 扇出 —— 按 pipeline_config.json 的 sink 开关，分别调 dispatch_oa / dispatch_report
  ③ 归档（一次）—— 单次 move 到 TEST_AUTO

原始 OA立项/、汇报信流程/ 不参与，全部用 email_pipeline/scripts/{oa,report}/ 副本。
说明：本脚本会连真实邮箱/数据库并发邮件，属有副作用脚本，请在受控环境运行。
"""
import os
import sys
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from loader import Pipeline  # noqa: E402

CONFIG_PATH = os.path.join(SCRIPT_DIR, "pipeline_config.json")
# 两个副本共用的邮箱凭据（gitignore，本地维护）
SHARED_EMAIL_CONFIG = os.path.join(SCRIPT_DIR, "email_config.json")


def load_pipeline_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main(dry_run=False):
    cfg = load_pipeline_config()
    accounts = cfg.get("accounts")          # None → 各副本用自己的 DEFAULT_ACCOUNTS
    sinks = cfg.get("sinks", {})
    oa_on = bool(sinks.get("oa", False))
    report_on = bool(sinks.get("report", True))
    oa_test_prefix = cfg.get("oa_test_project_prefix") or None

    if dry_run:
        print("[email_pipeline] ★ DRY-RUN：照常读邮件+分类，但不写库/不发邮件/不移邮件"
              "（注：读取阶段仍会把官文 PDF 暂存到 output/_inbox/）", file=sys.stderr)

    oa = Pipeline(os.path.join(SCRIPT_DIR, "oa"))
    rpt = Pipeline(os.path.join(SCRIPT_DIR, "report"))

    # ① 读 + 分类（只一次）。用 report 副本：classify_report 是 filter_oa_email 的超集。
    with rpt as RPT:
        RPT.set_config_path(SHARED_EMAIL_CONFIG)
        all_emails, all_results = RPT.read_and_classify(accounts=accounts)

    print(f"\n{'='*40}", file=sys.stderr)
    print(f"[email_pipeline] 读取 {len(all_emails)} 封 / 分类 {len(all_results)} 条", file=sys.stderr)
    print(f"[email_pipeline] sink 开关：oa={oa_on}  report={report_on}", file=sys.stderr)

    # ② 扇出。OA 在前（其 US 期限补全会就地改写 result，report 随后能用到）。
    if oa_on:
        print("[email_pipeline] → OA 立项 sink", file=sys.stderr)
        with oa as OA:
            OA.set_config_path(SHARED_EMAIL_CONFIG)
            OA.dispatch_oa(all_results, all_emails, dry_run=dry_run, test_project_prefix=oa_test_prefix)
    else:
        print("[email_pipeline] OA 立项 sink 关闭（sinks.oa=false）", file=sys.stderr)

    if report_on:
        print("[email_pipeline] → 汇报信 sink", file=sys.stderr)
        with rpt as RPT:
            RPT.set_config_path(SHARED_EMAIL_CONFIG)
            RPT.dispatch_report(all_results, all_emails, dry_run=dry_run)
    else:
        print("[email_pipeline] 汇报信 sink 关闭（sinks.report=false）", file=sys.stderr)

    # ③ 归档（只一次，用 report 副本的 archive_emails）。
    #    命中（OA/汇报信任一）→ TEST_AUTO；未命中（两者都不是）→ TEST_SKIPPED。
    with rpt as RPT:
        RPT.set_config_path(SHARED_EMAIL_CONFIG)
        RPT.archive_emails(all_emails, all_results, dry_run=dry_run)
    print("[email_pipeline] 归档完成" + ("（dry-run，未实际归档）" if dry_run else ""), file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="email_pipeline 统一调度入口")
    parser.add_argument("--dry-run", action="store_true",
                        help="只读+分类+打印，不写库/不发邮件/不移邮件")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
