"""20618 确认邮件样式回归测试；不连接邮箱或数据库。"""

import unittest

from submission.email_modules import build_email_modules


class Email20618Tests(unittest.TestCase):
    def test_sample_structure_and_emphasis(self):
        fields = {
            "case_volume": "20618-0947US01",
            "case_info": {"case_name_en": "MASTER MANIPULATORS OF ROBOTS"},
            "filing_route": "Continuation-in-part",
            "parent_applications": [{"Prior Application Number": "US 18/363,687",
                                      "Filing Date": "2023-08-01"}],
            "case_advance_info": {"pct_app_no": "PCT/CN2022/075245",
                                  "pct_app_date": "2022-01-30"},
            "priorities": [{"priority_no": "CN 202110454129.X", "priority_date": "2021-04-26"}],
            "applicants": [{"applicant_name_en": "WUHAN UNITED IMAGING SURGICAL CO., LTD.",
                            "contact_address_en": "Area A, Wuhan"}],
            "inventors": [{"full_name_en": "LU, Zhuangzhuang", "name_cn": "路壮壮",
                           "employer": "WUHAN UNITED IMAGING SURGICAL CO., LTD."}],
        }
        params = {"client_case_no": "ST2020056PCT-US-CIP1", "client_handler": "张文林",
                  "filing_deadline": "2026/8/21"}
        modules = build_email_modules(fields, params)
        self.assertEqual(len(modules), 6)
        self.assertEqual(len(modules[1]["extra_inputs"]), 5)
        greeting, info, route, signing, ids, closing = [m["html"] for m in modules]
        self.assertIn('<span style="background-color:#FFFF00;">（标黄部分烦请重点确认）</span>', greeting)
        self.assertIn("<b>烦请回邮确认</b>", greeting)
        self.assertIn("<table", info)
        self.assertIn('<span style="background-color:#FFFF00;">MASTER MANIPULATORS OF ROBOTS</span>', info)
        self.assertIn("优先权3：", info)
        self.assertIn("2021年4月26日", info)
        self.assertIn("<b>2026/8/21</b>", info)
        self.assertIn("<span style=\"background-color:#FFFF00;\">LU, Zhuangzhuang", info)
        self.assertIn("Continuation-in-part</span>", route)
        self.assertIn("<b>Declaration（发明人声明）。</b>", signing)
        self.assertIn("<b><u>⚠️温馨提示：关于签字文件的要求</u></b>", signing)
        self.assertIn("2.1）可以通过飞书", signing)
        self.assertIn("<b>IDS</b>", ids)
        self.assertIn("期限为美国时间2026/8/21</span>", closing)

    def test_escapes_dynamic_values_and_keeps_generic_template(self):
        fields = {"case_volume": "20618-0001US00",
                  "case_info": {"case_name_en": "A < B & C"}}
        html = "".join(m["html"] for m in build_email_modules(fields, {"client_case_no": "<script>"}))
        self.assertIn("A &lt; B &amp; C", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        generic = build_email_modules({"case_volume": "12345-H001US00"})
        self.assertIn("本案已定稿", generic[0]["html"])
        self.assertNotIn("<table", generic[1]["html"])


if __name__ == "__main__":
    unittest.main()
