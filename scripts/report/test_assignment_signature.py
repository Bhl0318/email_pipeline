"""通用 Assignment 签字区回归测试；不连接数据库。"""

import tempfile
import unittest

from docx import Document

from submission.assignment_generator import generate_assignment


class GeneralAssignmentSignatureTests(unittest.TestCase):
    def test_company_assignor_once_and_execution_date_blank(self):
        fields = {
            "case_volume": "99999-0001US00",
            "application_type": "发明",
            "case_info": {"case_name_en": "Test invention"},
            "applicants": [{"applicant_name_en": "ASSIGNEE CO.",
                            "address1": "1 Main Street", "city_en": "Suzhou",
                            "country_en_us": "China"}],
            "inventors": [{"last_name_en": "LI", "first_name_en": "Alice"}],
        }
        assignment = {
            "assignment_type": "公司转公司",
            "assigning_company": "CRYSTAL PHARMACEUTICAL (SUZHOU) CO., LTD.",
            "company_representative": "bi",
            "company_address1": "No.1002, Dagunan Road",
            "company_city_en": "Tianjin",
        }
        with tempfile.TemporaryDirectory() as folder:
            result = generate_assignment(fields, assignment, folder)
            doc = Document(result["file_path"])
            tables = [table for table in doc.tables
                      if table.rows and table.rows[0].cells[0].text.strip() == "Assignor"]
            self.assertEqual(len(tables), 1)
            cells = [cell.text for row in tables[0].rows for cell in row.cells]
            self.assertIn("CRYSTAL PHARMACEUTICAL (SUZHOU) CO., LTD.", cells)
            self.assertIn("bi", cells)
            date_index = cells.index("Execution Date:")
            self.assertEqual(cells[date_index + 1], "")
            self.assertNotIn("转让公司代表签字日期", "".join(cells))


if __name__ == "__main__":
    unittest.main()
