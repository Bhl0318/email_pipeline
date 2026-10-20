"""OA 官文无汇报信时 20618/20633 的转发兜底（不访问数据库或发送邮件）。"""
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


REPORT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "report"


class OaNoReportForwardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rules = json.loads((REPORT_DIR / "oa_report_rules.json").read_text(encoding="utf-8"))
        fake_store = types.ModuleType("rules_store")
        fake_store.build_oa_rules = lambda: rules
        spec = importlib.util.spec_from_file_location("report_read_email_no_db_test", REPORT_DIR / "read_email.py")
        cls.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"rules_store": fake_store}):
            with patch.object(sys, "path", [str(REPORT_DIR), *sys.path]):
                spec.loader.exec_module(cls.module)

    def dispatch(self, region, ntype, customer, dry_run=True):
        item = {
            "region": region, "notification_type": ntype,
            "project": f"{customer}-0001{region}00", "project_name": "测试案件",
            "message_id": "<test@example.com>",
        }
        fake_db = types.ModuleType("db_query")
        fake_db.execute = lambda sql: self.fail("dry-run must not query the database")
        emails = [({}, {"message_id": item["message_id"], "raw_bytes": b"Subject: test\r\n\r\nbody", "subject": "test"})]
        with patch.dict(sys.modules, {"db_query": fake_db}):
            with patch.object(self.module, "load_config", return_value={"accounts": {"pa": {"user": "pa@example.com"}}}), \
                 patch.object(self.module, "send_review_links_email"):
                return self.module.dispatch_report([item], emails, dry_run=dry_run)

    def test_existing_skip_forwards_once(self):
        actions = self.dispatch("US", "CTNF", "20618")
        self.assertEqual([a["action"] for a in actions], ["转发原始"])

    def test_global_ignore_uses_customer_fallback(self):
        actions = self.dispatch("US", "NT.CR.APP.PA", "20633")
        self.assertEqual([a["action"] for a in actions], ["转发原始"])

    def test_no_template_uses_customer_fallback(self):
        actions = self.dispatch("CN", "办理登记手续通知书", "20633")
        self.assertEqual([a["action"] for a in actions], ["转发原始"])

    def test_no_template_forwards_original_to_report_and_cc(self):
        with patch.object(self.module, "_forward_official_email") as forward:
            self.dispatch("EP", "European search report", "20618", dry_run=False)
        forward.assert_called_once()
        self.assertEqual(forward.call_args.args[3], ["report@metis-ip.com"])
        self.assertEqual(forward.call_args.args[4], ["ui_pa@metis-ip.com"])

    def test_explicit_assignment_still_wins(self):
        actions = self.dispatch("CN", "驳回决定", "20633")
        self.assertEqual([a["action"] for a in actions], ["分配汇报信"])

    def test_other_customer_does_not_use_fallback(self):
        actions = self.dispatch("US", "NOA", "20608")
        self.assertEqual(actions, [])


if __name__ == "__main__":
    unittest.main()
