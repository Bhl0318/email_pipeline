import unittest

from submission.common import build_priority_rows, clean_priority_no


class PctPriorityNumberTests(unittest.TestCase):
    def test_pct_priority_keeps_prefix_in_assignment(self):
        fields = {
            "priorities": [{"priority_no": "PCT/CN2023/012345", "priority_country_id": "CN",
                            "priority_date": "2023-01-01"}],
            "case_advance_info": {"pct_app_no": "PCT/CN2024/090619", "pct_app_date": "2024-08-01"},
        }
        self.assertEqual(build_priority_rows(fields), [
            ("PCT/CN2023/012345", "CN", "2023-01-01"),
            ("PCT/CN2024/090619", "CN", "2024-08-01"),
        ])

    def test_cn_priority_still_keeps_check_digit(self):
        self.assertEqual(clean_priority_no("CN 202511948961.X"), "202511948961.X")
        self.assertEqual(clean_priority_no(" pct / cn2024 / 090619 "), "PCT/CN2024/090619")


if __name__ == "__main__":
    unittest.main()
