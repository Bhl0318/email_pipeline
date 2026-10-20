import tempfile
import unittest
from pathlib import Path

from docx import Document

from submission.assignment_generator import _special_chain, generate_assignment, generate_assignments


def doc_text(path):
    doc = Document(path)
    text = "\n".join([p.text for p in doc.paragraphs]
                     + [c.text for table in doc.tables for row in table.rows for c in row.cells]
                     + [p.text for section in doc.sections for p in section.header.paragraphs])
    return doc, text


class SpecialAssignmentTemplateTests(unittest.TestCase):
    def test_chain_ignores_this_app_when_prior_is_empty(self):
        chain = _special_chain({"parent_applications": [{"Application No": "18/999,999",
                                                          "Prior Application Number": ""}],
                                "case_advance_info": {"pct_app_no": "PCT/CN2024/012345"},
                                "filing_route": "Bypass Continuation in part of"})
        self.assertNotIn("18/999,999", chain)
        self.assertIn("a continuation-in-part of International Patent Application No. PCT/CN2024/012345", chain)

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
                            "address1": "100 Main Street", "city_en": "Boston",
                            "country_en_us": "US"}],
            "inventors": [{"last_name_en": name, "first_name_en": "Test",
                           "employer": "NEW MEDICAL CORP.",
                           "residence_en": f"{idx} Test Street, Boston, US"}
                          for idx, name in enumerate(("SMITH", "LEE", "KIM"), 1)],
            "assignments": [{"assignment_type": "公司转公司",
                             "assigning_company": "NEW MEDICAL CORP.",
                             "company_representative": "ALEX WU",
                             "representative_title": "CEO",
                             "company_address1": "100 Main Street",
                             "company_city_en": "Boston",
                             "company_country_en": "US",
                             "assignee": "NEW MEDICAL CORP."}],
            "parent_applications": [{"Prior Application Number": "18/123,456",
                                     "Continuity Type": "Continuation of",
                                     "Filing Date": "2024-01-01"}],
            "case_advance_info": {"pct_app_no": "PCT/CN2023/987654",
                                  "pct_app_date": "2023-01-01"},
        }
        with tempfile.TemporaryDirectory() as folder:
            files = generate_assignments(fields, folder)
            self.assertEqual(len(files), 2)
            inventor_doc, inventor_text = doc_text(files[0]["file_path"])
            company_doc, company_text = doc_text(files[1]["file_path"])
            self.assertEqual(len(inventor_doc.tables), 3)
            self.assertEqual(len(company_doc.tables), 4)
            for text in (inventor_text, company_text):
                self.assertIn("20618-9999US00", text)
                self.assertIn("A NEW MEDICAL DEVICE", text)
                self.assertIn("18/123,456", text)
                self.assertIn("PCT/CN2023/987654", text)
                self.assertNotIn("{{", text)
                for old in ("20618-0168US04", "SHANGHAI UNITED", "UNITED IMAGING",
                            "PCT/CN2016/085434", "No.2258 Chengbei"):
                    self.assertNotIn(old, text)
            self.assertIn("SMITH, Test", inventor_text)
            self.assertIn("3 Test Street", inventor_text)
            self.assertIn("ALEX WU", company_text)


if __name__ == "__main__":
    unittest.main()
