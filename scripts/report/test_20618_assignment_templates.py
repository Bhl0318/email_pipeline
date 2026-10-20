import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docx import Document

from submission.assignment_generator import (SPECIAL_ASSIGNMENT_TEMPLATES,
                                             generate_assignment, generate_assignments)
from submission.common import ASSIGNMENT_TEMPLATE


def doc_text(path):
    doc = Document(path)
    text = "\n".join([p.text for p in doc.paragraphs]
                     + [c.text for table in doc.tables for row in table.rows for c in row.cells]
                     + [p.text for section in doc.sections for p in section.header.paragraphs])
    return doc, text


class SpecialAssignmentTemplateTests(unittest.TestCase):
    def test_special_templates_keep_customer_wording_and_signature_layout(self):
        for template in SPECIAL_ASSIGNMENT_TEMPLATES.values():
            with self.subTest(template=template.name):
                doc = Document(template)
                self.assertIn("{{APPLICATION_CHAIN}}", "\n".join(p.text for p in doc.paragraphs))
                self.assertNotIn("Application Number", "\n".join(c.text for t in doc.tables for r in t.rows for c in r.cells))
        company = Document(SPECIAL_ASSIGNMENT_TEMPLATES["公司转公司"])
        self.assertEqual(company.tables[0].rows[0].cells[0].text, "Assignor")
        self.assertEqual(company.tables[0].rows[0].cells[-1].text, "{{ASSIGNOR}}")
        inventor = Document(SPECIAL_ASSIGNMENT_TEMPLATES["个人转公司"])
        general = Document(ASSIGNMENT_TEMPLATE)
        self.assertEqual([t._tbl.xml for t in inventor.tables],
                         [t._tbl.xml for t in general.tables[1:3]])

    def test_other_clients_still_use_general_template(self):
        fields = {
            "case_volume": "20752-0001US00", "application_type": "发明",
            "case_info": {"case_name_en": "A DIFFERENT DEVICE"},
            "applicants": [{"applicant_name_en": "OTHER CORP.", "address1": "1 Main Street"}],
            "inventors": [{"last_name_en": "DOE", "first_name_en": "Jane"}],
        }
        with tempfile.TemporaryDirectory() as folder:
            result = generate_assignment(fields, {"assignment_type": "个人转公司",
                                                  "assignee": "OTHER CORP."}, folder)
            _, text = doc_text(result["file_path"])
            self.assertIn("A DIFFERENT DEVICE", text)
            self.assertNotIn("{{", text)

    def test_20618_uses_both_templates_without_sample_case_data(self):
        fields = {
            "case_volume": "20618-9999US00",
            "application_type": "发明",
            "case_info": {"case_name_en": "A NEW MEDICAL DEVICE"},
            "applicants": [{"applicant_name_en": "NEW MEDICAL CORP.",
                            "address1": "100 Main Street, Building 123, Industrial Development Zone",
                            "address2": "45 Riverside Avenue, Suite 321", "city_en": "Boston",
                            "province_city_en_us": "Massachusetts", "postcode": "02101",
                            "country_en_us": "US"}],
            "inventors": [{"last_name_en": name, "first_name_en": "Test",
                           "employer": "NEW MEDICAL CORP.",
                           "residence_en": ("1 Very Long Main Street, Building 123, Industrial Development Zone, "
                                            "45 Riverside Avenue, Suite 321, Boston, Massachusetts 02101, US")
                           if idx == 1 else f"{idx} Test Street, Boston, US"}
                          for idx, name in enumerate(("SMITH", "LEE", "KIM"), 1)],
            "assignments": [{"assignment_type": "公司转公司",
                             "assigning_company": "AMERICA HOLDINGS INC.",
                             "company_representative": "ALEX WU",
                             "representative_title": "CEO",
                             "company_address1": "100 Main Street",
                             "company_city_en": "Boston",
                             "company_country_en": "US",
                             "assignee": "NEW MEDICAL CORP."}],
            "parent_applications": [{"Application No": "18/123,456",
                                     "Prior Application Number": "18/123,456",
                                     "Continuity Type": "Continuation of",
                                     "Filing Date": "2024-01-01"}],
            "case_advance_info": {"pct_app_no": "PCT/CN2023/987654",
                                  "pct_app_date": "2023-01-01"},
        }
        with tempfile.TemporaryDirectory() as folder:
            with patch("submission.assignment_generator.Document", wraps=Document) as load_template:
                files = generate_assignments(fields, folder)
            self.assertEqual([Path(c.args[0]).name for c in load_template.call_args_list],
                             ["Assignment-20618-inventors.docx", "Assignment-20618-company.docx"])
            self.assertEqual(len(files), 2)
            inventor_doc, inventor_text = doc_text(files[0]["file_path"])
            company_doc, company_text = doc_text(files[1]["file_path"])
            self.assertEqual(len(inventor_doc.tables), 3)
            self.assertEqual(len(company_doc.tables), 4)
            self.assertGreater(len(inventor_doc.tables[0].rows), 5)  # 长地址续行
            self.assertEqual(len(inventor_doc.tables[0].columns), 3)
            self.assertIn("1 Very Long Main Street", inventor_doc.tables[0].rows[3].cells[-1].text)
            self.assertIn("2 Test Street", "\n".join(c.text for r in inventor_doc.tables[1].rows for c in r.cells))
            self.assertEqual(company_doc.tables[0].rows[0].cells[-1].text, "AMERICA HOLDINGS INC.")
            self.assertIn("for which is a continuation of", inventor_text)
            self.assertIn("for which is a continuation of", company_text)
            for text in (inventor_text, company_text):
                self.assertIn("20618-9999US00", text)
                self.assertIn("A NEW MEDICAL DEVICE", text)
                self.assertIn("U.S. Patent Application No. 18/123,456", text)
                self.assertIn("PCT/CN2023/987654", text)
                self.assertNotIn("{{", text)
                for old in ("20618-0168US04", "SHANGHAI UNITED", "UNITED IMAGING",
                            "PCT/CN2016/085434", "No.2258 Chengbei"):
                    self.assertNotIn(old, text)
            self.assertIn("SMITH, Test", inventor_text)
            self.assertIn("ALEX WU", company_text)

            single = generate_assignment(fields, {"assignment_type": "个人转公司",
                                                  "assignor_inventors": ["SMITH, Test"],
                                                  "assignee": "NEW MEDICAL CORP."}, Path(folder) / "single")
            single_doc, _ = doc_text(single["file_path"])
            self.assertEqual(len(single_doc.tables), 1)


if __name__ == "__main__":
    unittest.main()
