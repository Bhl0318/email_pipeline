"""结项抄送规则的数据源与回退路径（不连接数据库）。"""
import unittest
from unittest.mock import patch

import close_cc
import rules_store


class CloseCcSourceTest(unittest.TestCase):
    def test_v2_region_is_taken_from_project(self):
        for region in ("CN", "CM", "CS", "US", "DS", "PR", "WO", "DM"):
            with self.subTest(region=region):
                self.assertEqual(close_cc.region_of(f"6C301-H002{region}00"), region)

    def test_v2_type1_fallback_and_project_region_priority(self):
        rules = {"CM": {"combinations": {"其他递交": "类型1规则"},
                        "rules": {"类型1规则": {"rules": {"其他": {
                            "action": "skip", "forward": {"to": ["a@example.com"], "cc": []}
                        }}}}}}
        result = close_cc.resolve_cc(rules, "6C301-H002CM00", "其他递交", "任意类型2", region="US")
        self.assertEqual(result["region"], "CM")
        self.assertEqual(result["closeType"], "类型1规则")
        self.assertEqual(result["cc"], ["a@example.com"])

    def test_table_rules_drive_cc(self):
        rules = {"CN": {"combinations": {"著录项目_变更申请人": "变更申请人"},
                        "rules": {"变更申请人": {"rules": {"其他": {
                            "action": "skip", "forward": {"to": ["a@example.com"], "cc": []}
                        }}}}}}
        with patch.object(rules_store, "build_close_rules", return_value=rules):
            loaded = close_cc.load_rules()
        self.assertEqual(
            close_cc.resolve_cc(loaded, "12345-0001CN00", "著录项目", "变更申请人")["cc"],
            ["a@example.com"],
        )

    def test_empty_or_failed_table_falls_back_to_json(self):
        for result, error in (({}, None), (None, RuntimeError("database unavailable"))):
            with self.subTest(error=error):
                with patch.object(rules_store, "build_close_rules", return_value=result, side_effect=error):
                    rules = close_cc.load_rules()
                self.assertIn("CN", rules)
                self.assertIn("combinations", rules["CN"])


if __name__ == "__main__":
    unittest.main()
