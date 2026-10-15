"""OA 自动推荐的历史角色与负责人资格规则。"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "oa"))

from oa_personnel import collect_candidates
from oa_schemes import build_assignment_schemes


class CandidateRulesTest(unittest.TestCase):
    def test_historical_formal_only_is_excluded(self):
        own = [
            {"id": "writing", "project_type": "CN撰写", "project_leader": "撰写人", "project_qc": ""},
            {"id": "oa1", "project_type": "中国答复及其他", "project_leader": "形式人", "project_qc": "实质人"},
        ]
        perf = [
            {"proid": "oa1", "person": "形式人", "wkrole": "形式答复"},
            {"proid": "oa1", "person": "实质人", "wkrole": "实质答复"},
        ]

        def execute(sql):
            if "FROM tip_budgetperformance " in sql:
                return perf
            if "FROM projects " in sql:
                return [] if "project LIKE" in sql else own
            if "FROM users " in sql:
                return [{"usertype": "分析师", "position": "", "status": "在职", "usermail": "a@example.com"}]
            raise AssertionError(sql)

        names = {c["name"] for c in collect_candidates("20618-1234CN00", execute=execute)}
        self.assertEqual(names, {"撰写人", "实质人"})

    def test_spm_cqc_aqc_cannot_be_responder_but_can_be_qc(self):
        attrs = {
            "经理": ("SPM", ""),
            "质检": ("", "CQC"),
            "助理质检": ("", "AQC"),
            "负责人": ("", ""),
        }
        candidates = [{"name": n, "status": "在职", "sources": ["本案历史OA"]} for n in attrs]

        def execute(sql):
            if "SELECT username_zn, cls" in sql:
                return [{"username_zn": n, "cls": cls, "user_type": kind}
                        for n, (cls, kind) in attrs.items()]
            if "SELECT username_zn FROM users" in sql:
                return [{"username_zn": n} for n in attrs]
            raise AssertionError(sql)

        with patch("oa_personnel.collect_candidates", return_value=candidates), \
             patch("oa_whitelist_store.list_for", return_value=[]), \
             patch("oa_schemes._deepseek_schemes") as generate:
            for restricted in ("经理", "质检", "助理质检"):
                generate.return_value = [{"responder": restricted, "qc": "质检", "note": ""}]
                schemes = build_assignment_schemes("20618-1234CN00", region="CN", execute=execute)
                self.assertEqual(schemes[0]["responder"], "负责人")
                self.assertEqual(schemes[0]["qc"], "质检")

    def test_restriction_also_applies_with_whitelist(self):
        candidates = [
            {"name": "经理", "status": "在职", "sources": ["本案历史OA"]},
            {"name": "负责人", "status": "在职", "sources": ["本案历史OA"]},
            {"name": "质检", "status": "在职", "sources": ["本案历史OA"]},
        ]
        whitelist = [
            {"name": "经理", "tier": "1", "field": "通用", "tier_level": 1},
            {"name": "负责人", "tier": "2", "field": "通用", "tier_level": 2},
            {"name": "质检", "tier": "QC", "field": "通用", "tier_level": 1},
        ]

        def execute(sql):
            if "SELECT username_zn, cls" in sql:
                return [
                    {"username_zn": "经理", "cls": "SPM", "user_type": ""},
                    {"username_zn": "负责人", "cls": "", "user_type": ""},
                    {"username_zn": "质检", "cls": "", "user_type": "CQC"},
                ]
            if "SELECT username_zn FROM users" in sql:
                return [{"username_zn": c["name"]} for c in candidates]
            raise AssertionError(sql)

        with patch("oa_personnel.collect_candidates", return_value=candidates), \
             patch("oa_whitelist_store.list_for", return_value=whitelist), \
             patch("oa_schemes._deepseek_schemes_wl", return_value=[
                 {"responder": "经理", "qc": "质检", "field": "通用"}
             ]):
            schemes = build_assignment_schemes("20618-1234CN00", region="CN", execute=execute)
        self.assertEqual(schemes[0]["responder"], "负责人")
        self.assertEqual(schemes[0]["qc"], "质检")

    def test_attribute_query_failure_does_not_recommend_responder(self):
        candidates = [{"name": "可能受限", "status": "在职", "sources": ["本案历史OA"]}]

        def execute(sql):
            if "SELECT username_zn, cls" in sql:
                raise RuntimeError("数据库不可用")
            if "SELECT username_zn FROM users" in sql:
                return [{"username_zn": "可能受限"}]
            raise AssertionError(sql)

        with patch("oa_personnel.collect_candidates", return_value=candidates), \
             patch("oa_whitelist_store.list_for", return_value=[]), \
             patch("oa_schemes._deepseek_schemes", return_value=[
                 {"responder": "可能受限", "qc": "可能受限"}
             ]):
            schemes = build_assignment_schemes("20618-1234CN00", region="CN", execute=execute)
        self.assertEqual(schemes[0]["responder"], "")
        self.assertEqual(schemes[0]["qc"], "可能受限")


if __name__ == "__main__":
    unittest.main()
