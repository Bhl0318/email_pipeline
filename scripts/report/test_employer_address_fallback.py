"""发明人归属公司未匹配时，不得把申请人地址冒充归属公司地址。"""

import unittest

from submission.fields_mapping import _inventor_applicant_addr


class EmployerAddressFallbackTests(unittest.TestCase):
    def test_unknown_employer_never_inherits_applicant_address(self):
        applicant = {"applicant_name_en": "APPLICANT A", "address1": "Applicant Road"}
        inventor = {"employer": "COMPANY X"}
        self.assertEqual(_inventor_applicant_addr(inventor, [applicant], []), {})
        self.assertEqual(_inventor_applicant_addr(inventor, [applicant], [],
                                                 {"COMPANY X": {"applicant_name_en": "COMPANY X"}})
                         .get("address1"), None)
        self.assertEqual(_inventor_applicant_addr({"employer": "APPLICANT A"}, [applicant], [])
                         ["address1"], "Applicant Road")
        self.assertEqual(_inventor_applicant_addr(inventor, [applicant], [],
                                                 {"COMPANY X": {"address1": "Company X Road"}})
                         ["address1"], "Company X Road")


if __name__ == "__main__":
    unittest.main()
