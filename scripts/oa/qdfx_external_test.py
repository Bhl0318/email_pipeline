"""外部 OA 前端分析材料提交的离线测试。"""

import os
import sys
import unittest
from unittest.mock import Mock, patch
import fitz

sys.path.insert(0, os.path.dirname(__file__))
from qdfx_external import _ep_reference_numbers, _fpo_pdf, _reference_markdown, submit_oa_analysis


class ExternalAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.item = {"project": "20615-0011US00", "region": "US"}
        self.refs = [{"doc_no": "US20250150762A1"}]

    @patch("qdfx_external._fpo_pdf")
    def test_reference_must_match_full_publication_number_and_contain_full_text(self, fpo):
        def pdf_bytes(number):
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((40, 40), f"{number}\n" +
                             ("Specification text. Specification text.\n" * 35) +
                             "CLAIMS\n" + ("Claim text. Claim text.\n" * 12))
            data = doc.tobytes()
            doc.close()
            return data
        fpo.return_value = (pdf_bytes("US20250150762A1"), "https://www.freepatentsonline.com/20250150762.pdf")
        md = _reference_markdown("US 2025/0150762 A1")
        self.assertIn("Specification", md)
        self.assertIn("Claim text", md)
        fpo.assert_called_once_with("US20250150762A1", None)

        fpo.return_value = (pdf_bytes("US20250150762B2"), "https://www.freepatentsonline.com/20250150762.pdf")
        with self.assertRaisesRegex(ValueError, "公开号与请求不符"):
            _reference_markdown("US20250150762A1")

    def test_fpo_is_direct_source_and_country_is_kept(self):
        session = Mock()
        page = Mock(text='<iframe src="https://s3.amazonaws.com/pdf.sumobrain.com/110693604.pdf?X-Amz-Date=1"></iframe>')
        pdf = Mock(content=b"%PDF-1.7")
        session.get.side_effect = [page, pdf]
        content, source = _fpo_pdf("CN110693604A", session)
        self.assertEqual(content, b"%PDF-1.7")
        self.assertEqual(source, "https://www.freepatentsonline.com/CN110693604.pdf")
        self.assertEqual(session.get.call_args_list[0].args[0], source)
        self.assertEqual(session.get.call_args_list[1].args[0],
                         "https://s3.amazonaws.com/pdf.sumobrain.com/110693604.pdf?X-Amz-Date=1")

    @patch.dict(os.environ, {"QDFX_API_TOKEN": "test-token", "QDFX_API_BASE_URL": "http://example.test/assist"})
    @patch("oa_report_ai.find_application_files", return_value={"spec": "/tmp/spec.docx"})
    @patch("oa_report_ai._docx_text", return_value="Application text")
    @patch("qdfx_external._reference_markdown", return_value="# cited patent\nfull text")
    def test_upload_requires_complete_refs_and_checks_http_and_body(self, ref_text, docx, find_app):
        session = Mock()
        session.post.return_value.status_code = 202
        session.post.return_value.json.return_value = {"code": 202, "data": {"parseId": "parse-1", "version": 1}}
        result = submit_oa_analysis(self.item, "OA text", self.refs, session=session)
        self.assertEqual(result, {"status": "submitted", "parseId": "parse-1", "version": 1})
        kwargs = session.post.call_args.kwargs
        self.assertEqual([field for field, _ in kwargs["files"]], ["scyj", "sqwj", "dbwj"])
        self.assertEqual(kwargs["data"]["caseNo"], self.item["project"])
        self.assertEqual(kwargs["headers"]["X-Api-Token"], "test-token")

        ref_text.side_effect = ValueError("wrong patent")
        session.post.reset_mock()
        result = submit_oa_analysis(self.item, "OA text", self.refs, session=session)
        self.assertEqual(result["status"], "skipped")
        session.post.assert_not_called()

        ref_text.side_effect = None
        session.post.return_value.status_code = 200
        session.post.return_value.json.return_value = {"code": 202, "data": {"parseId": "parse-2"}}
        result = submit_oa_analysis(self.item, "OA text", self.refs, session=session)
        self.assertEqual(result["status"], "failed")

    @patch.dict(os.environ, {"QDFX_API_TOKEN": "test-token"})
    @patch("oa_report_ai.find_application_files", return_value={"spec": None})
    @patch("oa_report_ai._docx_text", return_value="")
    def test_missing_application_skips_before_fetch(self, docx, find_app):
        session = Mock()
        result = submit_oa_analysis(self.item, "OA text", self.refs, session=session)
        self.assertEqual(result["status"], "skipped")
        session.get.assert_not_called()
        session.post.assert_not_called()

    def test_ep_inline_reference_and_unrecognized_reference(self):
        self.assertEqual(_ep_reference_numbers("D1: EP 1234567 A1; D2: WO2020123456A1"),
                         [{"doc_no": "EP1234567A1"}, {"doc_no": "WO2020123456A1"}])
        with patch.dict(os.environ, {"QDFX_API_TOKEN": "test-token"}), \
             patch("oa_report_ai.find_application_files", return_value={"spec": "/tmp/spec.docx"}), \
             patch("oa_report_ai._docx_text", return_value="Application text"):
            session = Mock()
            result = submit_oa_analysis(self.item, "OA text", [{"doc_no": "conference paper"}], session=session)
            self.assertEqual(result["status"], "skipped")
            session.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
