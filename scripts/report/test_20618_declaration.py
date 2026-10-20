import tempfile
import unittest
import re

import fitz

from submission.common import DECLARATION_20618_TEMPLATE, DECLARATION_ENCN_TEMPLATE
from submission.declaration_generator import _build_field_dict, generate_declarations


class Declaration20618Tests(unittest.TestCase):
    def test_20618_template_has_no_sample_case_values(self):
        with fitz.open(DECLARATION_20618_TEMPLATE) as doc:
            values = {w.field_name: (w.field_value or "").strip()
                      for w in doc[0].widgets()}
        self.assertFalse(values["Title of Invention"])
        self.assertFalse(values["Inventor"])
        self.assertFalse(values["This declaration"])
        self.assertFalse(values["undefined"])

    def test_20618_fills_each_inventor_and_correct_route(self):
        fields = {
            "case_volume": "20618-9999US00",
            "case_info": {"case_name_en": "A NEW MEDICAL DEVICE"},
            "inventors": [
                {"last_name_en": "LI", "first_name_en": "Alice"},
                {"last_name_en": "WU", "first_name_en": "Bob"},
            ],
            "case_advance_info": {"pct_app_no": "PCT/CN2024/123456",
                                  "pct_app_date": "2024-01-02"},
        }
        for route, first, second in (("Paris", "On", ""),
                                     ("Bypass Continuation", "", "On")):
            with self.subTest(route=route), tempfile.TemporaryDirectory() as folder:
                fields["filing_route"] = route
                result = generate_declarations(fields, folder)[0]
                with fitz.open(result["file_path"]) as doc:
                    self.assertEqual(len(doc), 2)
                    for i, name in enumerate(("LI, Alice", "WU, Bob")):
                        # PyMuPDF 合并同名表单字段时会给第二页起的字段加 [xref] 后缀。
                        values = {re.sub(r" \[\d+\]$", "", w.field_name):
                                  (w.field_value or "").strip()
                                  for w in doc[i].widgets()}
                        self.assertEqual(values["Title of Invention"], "A NEW MEDICAL DEVICE")
                        self.assertEqual(values["Inventor"], name)
                        self.assertEqual(values["This declaration"], first)
                        self.assertEqual(values["undefined"], second)
                        self.assertEqual(values["United States application or PCT international application number"],
                                         "PCT/CN2024/123456" if second else "")
                        self.assertNotIn("LI, Hongdi", "\n".join(values.values()))

    def test_other_customers_keep_bilingual_template(self):
        template, _ = _build_field_dict(False, "TITLE", "LI, Alice", "", "")
        self.assertEqual(template, DECLARATION_ENCN_TEMPLATE)


if __name__ == "__main__":
    unittest.main()
