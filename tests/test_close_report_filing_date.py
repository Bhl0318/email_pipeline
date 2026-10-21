"""结项汇报信的本申请递交日从 IPEasy divisional_date 读取。"""
import importlib.util
import sys
import types
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "report" / "enrich_report.py"
SPEC = importlib.util.spec_from_file_location("report_enrich_for_test", MODULE_PATH)
enrich = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(enrich)


class CloseReportFilingDateTests(unittest.TestCase):
    def test_case_info_joins_advance_info_by_case_id(self):
        class Cursor:
            def execute(self, sql, params):
                self.sql, self.params = sql, params

            def fetchone(self):
                return ("客户案号", "申请号", "申请名称", datetime(2020, 1, 2), datetime(2021, 3, 4))

            def close(self):
                pass

        cursor = Cursor()
        connection = types.SimpleNamespace(cursor=lambda: cursor, close=lambda: None)
        pymssql = types.ModuleType("pymssql")
        pymssql.connect = lambda *args, **kwargs: connection
        with patch.dict(sys.modules, {"pymssql": pymssql}), \
             patch.object(enrich, "_load_db_config", return_value={"mssql_ipeasy": {
                 "host": "mock", "user": "mock", "password": "mock", "database": "mock"}}):
            info = enrich.query_case_info("20618-0001US00", include_divisional_date=True)
        self.assertIn("ci.case_id = ai.case_id", cursor.sql)
        self.assertIn("ai.divisional_date", cursor.sql)
        self.assertEqual(cursor.params, ("20618-0001US00",))
        self.assertEqual(info["divisional_date"], datetime(2021, 3, 4))

        with patch.dict(sys.modules, {"pymssql": pymssql}), \
             patch.object(enrich, "_load_db_config", return_value={"mssql_ipeasy": {
                 "host": "mock", "user": "mock", "password": "mock", "database": "mock"}}):
            ordinary = enrich.query_case_info("20618-0001US00")
        self.assertNotIn("p_case_advance_info", cursor.sql)
        self.assertNotIn("divisional_date", ordinary)

    def test_only_close_enrichment_includes_divisional_date(self):
        case = {"app_date": datetime(2020, 1, 2), "divisional_date": datetime(2021, 3, 4)}
        with patch.object(enrich, "query_customer_name", return_value=""), \
             patch.object(enrich, "query_case_info", return_value=case) as query:
            oa = enrich.enrich_cn_fields("20618-0001US00")
            close = enrich.enrich_cn_fields("20618-0001US00", include_divisional_date=True)
        self.assertEqual(query.call_args_list[0].kwargs, {"include_divisional_date": False})
        self.assertEqual(query.call_args_list[1].kwargs, {"include_divisional_date": True})
        self.assertNotIn("本申请递交日", oa)
        self.assertEqual(close["本申请递交日"], "2021-03-04")
        self.assertEqual(close["申请日"], "2020-01-02")


if __name__ == "__main__":
    unittest.main()
